import os
from dotenv import load_dotenv
load_dotenv()

# EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBED_MODEL="all-MiniLM-L6-v2"
EMBED_MODEL_TOKEN_SIZE = 384
REGULAR_COLLECTION_NAME = "regular_embeddings"

NER_EMBED_MODEL = "dslim/bert-base-NER"
NER_EMBED_TOKEN_SIZE = 768
NER_COLLECTION_NAME = "ner_embeddings"

POSTGRES_USER = os.environ.get("POSTGRES_USER", "myuser")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "mydatabase")
POSTGRES_PW = os.environ.get("POSTGRES_PW", "mypassword")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")