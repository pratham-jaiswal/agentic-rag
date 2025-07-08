from dotenv import load_dotenv

load_dotenv()

from entities.variables import AGENT_NAME, TOP_K, ALLOWED_ORIGINS, ORG_NAME
from entities.embedder import embedder
from entities.llm import llm
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.vectorstores import FAISS
from langgraph.graph import MessagesState, StateGraph
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from typing import TypedDict, Optional, List, Annotated
import traceback
import base64
import json
import os

app = FastAPI()

FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

print(ALLOWED_ORIGINS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    vectorstore = FAISS.load_local(
        FAISS_INDEX_DIR,
        embeddings=embedder,
        allow_dangerous_deserialization=True
    )
    print("FAISS index loaded.")
except Exception as e:
    print("Failed to load FAISS index:", e)
    raise e


class Payload(BaseModel):
    chat_history: List[dict]

class ResponseSchema(TypedDict):
    response: str
    source_pdfs: Annotated[Optional[List[str]], ..., "List of source PDF names"]
    source_images: Annotated[Optional[List[str]], ..., "List of source image paths"]

@tool
def query_vectorstore(query):
    """
    Perform a similarity search on the FAISS vectorstore using the provided query.

    Args:
        query (str): Restructured user's query

    Returns:
        List[Document]: A list of documents from the vectorstore that are most similar to the query.
    """
    docs = vectorstore.similarity_search(query=query, k=TOP_K)
    return docs

def rag_agent_node():
    system_prompt = f"""
        You are a retrieval-augmented generation (RAG) agent for {ORG_NAME}.

        Your job is to **only** answer questions based on context retrieved from the 'query_vectorstore' tool.
        Follow these strict instructions:

        - ALWAYS call the 'query_vectorstore' tool for any user question.
        - If needed, restructure or rephrase the query and call the tool multiple times to retrieve better results.
        - If no answer is found in the context retrieved, respond with: "I don't know."
        - Output must ALWAYS be in JSON with keys: `response`, `source_pdfs`, and `source_images`.
        - Mention all relevant source PDF names in `source_pdfs`.
        - Mention all relevant image file paths (if any) in `source_images`.
        - Do NOT fabricate or guess answers.
        - Do NOT respond with outside knowledge or opinions.
        - You may reply briefly to greetings but must not offer any unsolicited help.
        - For basic greetings, do not call the `query_vectorstore` tool, and do not pass anything to `source_pdfs` or `source_images`
        
        Your first action after a user question (not greetings) must be to call `query_vectorstore`.
    """

    agent = create_react_agent(
        model=llm,
        tools=[query_vectorstore],
        name=AGENT_NAME,
        prompt=system_prompt
    )

    return agent

def structured_response_agent(state: MessagesState):
    response = llm.with_structured_output(ResponseSchema).invoke([
        SystemMessage(content="""
            You are a structured response agent. 
            Your task is to convert a json response into a structured response.
            If its just a greeting, keep 'source_pdfs' and 'source_images' empty.
        """), 
        state["messages"][-1]
    ])

    res_json = {
        "response": response.get("response", ""),
        "source_pdfs": response.get("source_pdfs", []),
        "source_images": response.get("source_images", [])
    }

    message = AIMessage(
        content=json.dumps(res_json),
        name="structured_response_agent"
    )
    
    return {
        "messages": [message]
    }

@app.post("/query")
async def call_agent(req: Payload):
    try:
        agent = rag_agent_node()

        workflow = StateGraph(MessagesState)
        workflow.add_node("rag_agent", agent)
        workflow.add_node("structured_response_agent", structured_response_agent)
        workflow.add_edge("__start__", "rag_agent")
        workflow.add_edge("rag_agent", "structured_response_agent")
        graph = workflow.compile()

        res = graph.invoke({"messages": req.chat_history})
        res = res["messages"][-1].content
        res = json.loads(res)

        if "source_images" in res and res["source_images"]:
            res["source_images"] = [
                base64.b64encode(open(path, "rb").read()).decode("utf-8")
                for path in res["source_images"] if os.path.exists(path)
            ]
        return {
            "result": res
        }
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
