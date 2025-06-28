from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.transforms.chunker.tokenizer.base import BaseTokenizer
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer, AutoModel

# from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer

# from langchain_ollama.llms import OllamaLLM
from helper import get_converted_doc, chunk_it
from docling.datamodel.base_models import InputFormat
from langchain_postgres import PGVector

# EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SOURCE_DOC = "all_tweets_classified_10.csv"

connectionStr = "postgresql+psycopg://myuser:mymypassword@localhost:5432/mydatabase"


# MAX_TOKENS = 64
def get_embedding_model(model_id="sentence-transformers/all-mpnet-base-v2"):
    return AutoModel.from_pretrained(model_id)


def get_tokenizer(model_id):
    tokenizer: BaseTokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(model_id)
    )
    return tokenizer


def main(model_name=EMBED_MODEL, file=SOURCE_DOC):
    embeddings_model = get_embedding_model(model_id=model_name)
    embeddings_tokenizer = get_tokenizer(model_id=model_name)
    chunker = HybridChunker(tokenizer=embeddings_tokenizer, merge_peers=True)
    print(f"{embeddings_tokenizer.get_max_tokens()=}")
    texts = chunk_it(SOURCE_DOC, chunker)
    print(f"{len(texts)} document chunks created")
    for document in texts:
        print(f"Document ID: {document.metadata['doc_id']}")
        print(f"Source: {document.metadata['source']}")
        print(f"Content:\n{document.page_content}")
        print("=" * 80)  # Separator for clarity
    vector_store = PGVector(
        embeddings=embeddings_model,
        collection_name="my_embeddings",
        connection=connectionStr,
        # use_jsonb=True,
    )
    ids = vector_store.add_documents(texts)
    print(f"{len(ids)} documents added to the vector database")


# def run_model(model_name):
#     model = OllamaLLM(model=model_name)


if __name__ == "__main__":
    main()
