import asyncio
import json

import rich
from langchain_postgres import PGVector

# from ner import get_standard_ner_pipeline
import constants
import db.database as database

from .helper import chunk_documents, convert_json_to_langchain_docs

# POSTGRES_USER = "myuser"
# POSTGRES_DB = "mydatabase"
# POSTGRES_PW = "mypassword"
# POSTGRES_HOST = "localhost"
# POSTGRES_PORT = "5432"
# COLLECTION_NAME = "tweet_embeddings"

# EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
# NER_EMBED_MODEL = "dslim/bert-base-NER"
# # EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# # SOURCE_DOC = "all_tweets_classified_10.csv"
# SOURCE_DOC = "./tweets.7k.csv"


EMBED_MODEL = constants.EMBED_MODEL

async def main(model_name=EMBED_MODEL, data: str = "", hash: str = ""):
    content = ""
    rich.print(f"Model: {model_name}, Data type: {type(data)}, Hash: {hash}")
    # try:
    if data:
        content = json.loads(data)
    # ner_pipe = get_standard_ner_pipeline(
    #     model_name=NER_EMBED_MODEL, tokenizer_name=NER_EMBED_MODEL
    # )

    documents = convert_json_to_langchain_docs(
        data=content, text_column="tweet text", metadata_key="metadata"
    )
    chunked_documents = chunk_documents(
        documents, chunk_char_overlap=20, chunk_char_size=340
    )

    rich.print(f"Total chunked documents: {len(chunked_documents)}")

    vector_store = database.getRegularVectorStore(
        metadata={
            "embedding_model": EMBED_MODEL,
            "collection_name": "skeets",
            "embedding_length": 384,
            "document_hash": hash,
        }
    )
    vector_store.create_collection()
    rich.print(
        f"Using Postgres collection: {vector_store.collection_name} with embedding model: {model_name}"
    )
    ids = vector_store.add_documents(chunked_documents)
    # print(f"{len(ids)} documents added to the vector database")

    # ner_vector_store = database.getNERVectorStore()

    # await semantic_search(vector_store, query)
    # await vector_search(vector_store, query, embeddings_model)
    # print("No. Embeddings: {len(texts)}")
    # ids = vector_store.add_documents(texts)
    # print(f"{len(ids)} documents added to the vector database")
    # print(f"ids stored: {ids}")
    # found = vector_store.similarity_search(
    #     "energiewende", k=1, filter={"metadata": ">0.4"}
    # )
    # for doc in found:
    #     print(f"* Found: {doc}")

    return {
        "status": "completed",
        "collection": vector_store.collection_name,
        "original_document_uuid": hash,
        "documents_added": len(ids),
        "message": f"Processed {len(ids)} documents and added to vector store.",
    }


# def run_model(model_name):
#     model = OllamaLLM(model=model_name)


async def semantic_search(vector_store, query):
    results = await vector_store.asimilarity_search(query=f"{query}")
    for doc in results:
        print(f"* {doc.page_content} [{doc.metadata}]")


async def vector_search(store, query, embedding):
    query_vector = embedding.embed_query(query)
    docs = await store.asimilarity_search_by_vector(query_vector, k=2)
    for d in docs:
        print(f"Result: {d.page_content.tweet_text}")


if __name__ == "__main__":
    asyncio.run(main())
