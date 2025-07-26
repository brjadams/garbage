from transformers import AutoModelForTokenClassification, AutoTokenizer, AutoModel
from transformers.pipelines import pipeline
from langchain_huggingface import HuggingFaceEmbeddings
import asyncio
import pdb
from ner import get_standard_ner_pipeline
import json

# from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer
import transformers

# from langchain_ollama.llms import OllamaLLM
from csv_import import CsvProcessor
from helper import convert_json_to_langchain_docs, chunk_documents
from langchain_postgres import PGEngine, PGVector

POSTGRES_USER = "myuser"
POSTGRES_DB = "mydatabase"
POSTGRES_PW = "mypassword"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
COLLECTION_NAME = "tweet_embeddings"

EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
NER_EMBED_MODEL = "dslim/bert-base-NER"
# EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# SOURCE_DOC = "all_tweets_classified_10.csv"
SOURCE_DOC = "./tweets.7k.csv"

connectionStr = "postgresql+psycopg://myuser:mymypassword@localhost:5432/mydatabase"


# MAX_TOKENS = 64
def get_embedding_model(model_id=EMBED_MODEL):
    return AutoModel.from_pretrained(model_id)


# def get_tokenizer(model_id=EMBED_MODEL):
#     tokenizer: BaseTokenizer = HuggingFaceTokenizer(
#         tokenizer=AutoTokenizer.from_pretrained(model_id)
#     )
#     return tokenizer


def getPGEngine():
    CONNECTION_STRING = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_HOST}"
        f":{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    pg_engine = PGEngine.ffrom_connection_string(url=CONNECTION_STRING, vector_size=768)
    return pg_engine


def pg_add_documents(store: PGVector, documents):
    d = store.add_documents(documents)
    return d


async def main(model_name=EMBED_MODEL, file=SOURCE_DOC):
    embeddings_model = get_embedding_model(model_id=model_name)
    # embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    ner_model = AutoModelForTokenClassification.from_pretrained(NER_EMBED_MODEL)
    ner_tokenizer = AutoTokenizer.from_pretrained(NER_EMBED_MODEL)

    json_documents = CsvProcessor(csv_file_name=SOURCE_DOC).export_to_json(
        keys_to_drop=[],
        keys_to_metadata=[
            "uuid",
            "mod_class",
            "confidence",
            "top_groups",
            "match_score",
            "score_per_100_char",
            "screen_name",
        ],
    )

    ner_pipe = get_standard_ner_pipeline(model_name=NER_EMBED_MODEL, tokenizer_name=NER_EMBED_MODEL)

    for doc in json.loads(json_documents)[:3]:
        pdb.set_trace()
        print(doc)
    documents = convert_json_to_langchain_docs(
        data=json_documents, text_column="tweet_text", metadata_key="metadata"
    )
    chunked_documents = chunk_documents(
        documents, chunk_char_overlap=20, chunk_char_size=340
    )
    vector_store = PGVector(
        embeddings=embeddings_model,
        pre_delete_collection=True,
        use_jsonb=True,
        embedding_length=384,
        collection_name=COLLECTION_NAME,
        connection=connectionStr,
        collection_metadata={"model": f"{model_name}"},
        # async_mode=True,
        create_extension=True,
    )

    # ids = pg_add_documents(vector_store, chunked_documents)

    # await semantic_search(vector_store, query)
    # await vector_search(vector_store, query, embeddings_model)
    # print("No. Embeddings: {len(texts)}")
    # ids = vector_store.add_documents(texts)
    # print(f"{len(ids)} documents added to the vector database")
    # print(f"ids stored: {ids}")
    # found = vector_store.similarity_search("energiewende", k=1, filter={"metadata": ">0.4"})
    # for doc in found:
    #     print(f"* Found: {doc}")


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
