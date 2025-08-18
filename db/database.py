import os
from langchain_huggingface import HuggingFaceEmbeddings
import constants
from langchain_postgres import PGEngine
from langchain_postgres.vectorstores import PGVector
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# connection = "postgresql+psycopg://langchain:langchain@localhost:6024/langchain"  # Uses psycopg3!
# connectionStr = "postgresql+psycopg://myuser:mymypassword@localhost:5432/mydatabase"
connectionStr = f"postgresql+psycopg://{constants.POSTGRES_USER}:{constants.POSTGRES_PW}@{constants.POSTGRES_HOST}:{constants.POSTGRES_PORT}/{constants.POSTGRES_DB}"
NER_COLLECTION_NAME = "ner_embeddings"
REGULAR_COLLECTION_NAME = "regular_embeddings"


def _getVectorStore(embedding_model, collection_name: str, embedding_length: int = 384):
    embeddings_model = HuggingFaceEmbeddings(model_name=embedding_model)
    vector_store = PGVector(
        embeddings=embeddings_model,
        collection_name=collection_name,
        connection=connectionStr,
        embedding_length=embedding_length,
        collection_metadata={"model": f"{embedding_model}"},
    )
    return vector_store


def getRegularVectorStore(
    embedding_model=constants.EMBED_MODEL,
    collection_name=constants.REGULAR_COLLECTION_NAME,
    embedding_length=constants.EMBED_MODEL_TOKEN_SIZE,
):
    return _getVectorStore(embedding_model, collection_name, embedding_length)


def getNERVectorStore(
    embedding_model=constants.NER_EMBED_MODEL,
    collection_name=constants.NER_COLLECTION_NAME,
    embedding_length=constants.NER_EMBED_TOKEN_SIZE,
):
    return _getVectorStore(embedding_model, collection_name, embedding_length)
