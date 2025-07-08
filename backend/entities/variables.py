import os
import re

OPENAI_MODEL = os.getenv("OPENAI_MODEL").lower()
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL").lower()

SOURCE_DOC_DIR = os.getenv("SOURCE_DOC_DIR")
IMAGE_DIR = os.getenv("IMAGE_DIR")

AGENT_NAME = re.sub(r'\s+', '_', re.sub(r'[^a-zA-Z]', ' ', os.getenv("AGENT_NAME"))).lower()

TOP_K = 4
FAISS_INDEX_DIR = os.getenv("FAISS_INDEX_DIR")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS").split(",")
ORG_NAME = os.getenv("ORG_NAME")