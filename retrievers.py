from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.schema import Document


def get_bm25_retriever(vector_store, k=5):
    """
    Create a BM25 retriever from the given vector store.
    """
    return BM25Retriever(
        vector_store=vector_store,
        k=k,
        search_type="similarity",
        search_kwargs={"k": k},
    )
