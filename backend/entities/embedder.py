from entities.variables import OPENAI_EMBEDDING_MODEL
from langchain_openai import OpenAIEmbeddings

embedder = OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)