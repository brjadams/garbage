from langchain_core.vectorstores import PGVector, pg_add_documents
from langchain_core.documents import Document
from langchain_postgres import PGEngine, PGVector


POSTGRES_USER = "myuser"
POSTGRES_DB = "mydatabase"
POSTGRES_PW = "mypassword"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
COLLECTION_NAME = "tweet_embeddings"

CONNECTION_STRING = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_HOST}"
    f":{POSTGRES_PORT}/{POSTGRES_DB}"
)

def getPGEngine():
    CONNECTION_STRING = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_HOST}"
        f":{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    pg_engine = PGEngine.ffrom_connection_string(url=CONNECTION_STRING)
    return pg_engine

def getPGVectorStore():
    pg_engine = getPGEngine()
    vectorstore = PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )