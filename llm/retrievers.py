from langchain_community.retrievers import BM25Retriever


def get_bm25_retriever(docs: list=[]):
    """
    Create a BM25 reranker from a given set of documents
    """
    # return BM25Retriever(
    #     vector_store=vector_store,
    #     k=k,
    #     search_type="similarity",
    #     search_kwargs={"k": k},
    # )
