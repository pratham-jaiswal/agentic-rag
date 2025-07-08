## Setup .env

- Copy the contents ftom `.env.example` to `.env`.
- Replace the value of `OPENAI_API_KEY` with your OpenAI API key.
- `SOURCE_DOC_DIR` defines the directory where the source PDFs are stored.
- `IMAGE_DIR` defines the directory where the extracted images are stored.
- `OPENAI_MODEL` defines the OpenAI model to use for the LLM. ([guide](https://platform.openai.com/docs/models))
- `OPENAI_EMBEDDING_MODEL` defines the OpenAI model to use for the embedder. ([guide](https://platform.openai.com/docs/guides/embeddings#embedding-models))
- `FAISS_INDEX_DIR` defines the directory where the FAISS index of the PDFs is stored.
- `TOP_K` defines the number of top results to return.
- `AGENT_NAME` defines the name of the agent.
- `ALLOWED_ORIGINS` defines the origins that are allowed to access the API.
- `ORG_NAME` defines the name of the organization.
- Create your PDF directory (as in `SOURCE_DOC_DIR`), and store your PDFs in it.
- You can change the values of these variables in the `.env` file as per your needs.
- Play around with the system prompt in `app.py` in `rag_agent_node` to customize the behavior of the agent.

## Get Started

- Download and install [Python 3.11.13](https://www.python.org/downloads/release/python-31113/)
- Install the required packages using `pip install -r requirements.txt`.
- Install Poppler using `apt-get install -y poppler-utils` (required by the `unstructured` library).
- Run `source_indexing.py` to index the source PDFs and create the FAISS index by executing either `python source_indexing.py` or `./run_indexing.sh`.
- Locally run the app using `uvicorn app:app --reload --port 8000`.