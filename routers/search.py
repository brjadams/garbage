from dotenv import load_dotenv
from fastapi import APIRouter
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from pydantic import BaseModel
from rich.console import Console
from rq.job import Job

import constants

console = Console()
load_dotenv()

document_search_router = APIRouter(prefix="/search", tags=["search"])


class SearchResponse(BaseModel):
    message: str
    error: bool = False
    results: list[dict] = []


@document_search_router.get("/")
async def get_job_status(
    query: str | None = None, collection: str = "regular_embeddings"
):
    if not query:
        return SearchResponse(
            message="Please provide a query parameter.", error=True, results=[]
        )
    # try:
    store = get_vector_store()
    sim_docs = store.as_retriever(search_kwargs={"k": 10})
    sim_retrieved = sim_docs.invoke(query)
    console.log(f"Retrieved {len(sim_retrieved)} documents from vector store.")
    console.log(
        "\n--- Step 1: Documents fetched from PGVector (Semantic Search) ---"
    )
    for i, doc in enumerate(sim_retrieved):
        console.log(f"{i + 1}. (ID: {doc.metadata['id']}) {doc.page_content}")

    # filtered_by_meta = store.similarity_search_with_score("", filter={"page_id": "1"})
    # print("\n--- Step 2: Documents filtered by metadata (page_id=1) ---")
    # for i, (doc, score) in enumerate(filtered_by_meta):
    #     print(f"{i+1}. (Score: {score}) (ID: {doc.metadata['id']}) {doc.page_content}")

    # bm25_reranker = BM25Retriever.from_documents(sim_retrieved)
    # reranked_docs = bm25_reranker.invoke(query, k=25)

    for i, doc in enumerate(sim_retrieved):
        console.log(f"{i + 1}. (ID: {doc.metadata['id']}) {doc.page_content}")
    return SearchResponse(
        message="Search completed successfully.",
        error=False,
        results=[
            {
                "id": doc.metadata.get("id"),
                "page_id": doc.metadata.get("page_id"),
                "content": doc.page_content,
                "source": doc.metadata.get("source"),
            }
            for doc in sim_retrieved
        ],
    )
    # except Exception as e:
    #     return SearchResponse(
    #         message=f"Error fetching job: {str(e)}", error=True, results=[]
    #     )


def get_vector_store():
    console.log("Connecting to Postgres Vector Store...")
    console.log(f"Using connection string: {constants.PG_CONNECTION_STR}")
    console.log(f"Using embedding model: {constants.EMBEDDING_MODEL}")
    cache_folder = "./.venv/huggingface"
    vector_store = PGVector(
        embeddings=HuggingFaceEmbeddings(
            model_name=constants.EMBEDDING_MODEL, cache_folder=cache_folder
        ),
        collection_name="regular_embeddings",
        connection=constants.PG_CONNECTION_STR,
        embedding_length=constants.EMBED_MODEL_TOKEN_SIZE or None,
    )
    return vector_store
