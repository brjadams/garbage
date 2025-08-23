import asyncio
import json
import pdb

import rich
import transformers

from .helper import chunk_documents, convert_json_to_langchain_docs
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGEngine, PGVector
# from ner import get_standard_ner_pipeline
from transformers import AutoModel, AutoModelForTokenClassification, AutoTokenizer
from transformers.pipelines import pipeline

import constants
from llm.csv_import import CsvProcessor

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

connectionStr = "postgresql+psycopg://myuser:mymypassword@localhost:5432/mydatabase"

EMBED_MODEL = constants.EMBED_MODEL


def pg_add_documents(store: PGVector, documents):
    d = store.add_documents(documents)
    return d


async def main(model_name=EMBED_MODEL, data: str = "", hash: str = ""):
    # embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # json_documents = CsvProcessor(csv_file_name=file).export_to_json(
    #     keys_to_drop=[],
    #     keys_to_metadata=[
    #         "mod_class",
    #         "confidence",
    #         "top_groups",
    #         "match_score",
    #         "score_per_100_char",
    #         "screen_name",
    #     ],
    # )
    content = ""
    try:
        if data:
            content = json.loads(data)
        # ner_pipe = get_standard_ner_pipeline(
        #     model_name=NER_EMBED_MODEL, tokenizer_name=NER_EMBED_MODEL
        # )

        documents = convert_json_to_langchain_docs(
            data=content, text_column="tweet_text", metadata_key="metadata"
        )
        chunked_documents = chunk_documents(
            documents, chunk_char_overlap=20, chunk_char_size=340
        )
    except Exception as e:
        print(f"Error processing documents: {e}")
        return
    rich.print(f"Total chunked documents: {len(chunked_documents)}")
    import db.database as database

    vector_store = database.getRegularVectorStore()
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
