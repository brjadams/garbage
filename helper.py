from typing import Iterable, Optional
import uuid
import json
from docling_core.transforms.chunker.base import BaseChunk
from docling_core.transforms.chunker.hierarchical_chunker import DocChunk
from docling_core.types.doc.labels import DocItemLabel
from rich.console import Console
from docling.document_converter import DocumentConverter
from langchain_core.documents import Document
import pdb
from typing import List, Optional
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from meta_extract import BlueSkyMetaExtractor
from langchain_core.documents import Document
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)  # This is the key import

console = Console(
    width=200,  # for getting Markdown tables rendered nicely
)


def find_n_th_chunk_with_label(
    iter: Iterable[BaseChunk], n: int, label: DocItemLabel
) -> Optional[DocChunk]:
    num_found = -1
    for i, chunk in enumerate(iter):
        doc_chunk = DocChunk.model_validate(chunk)
        for it in doc_chunk.meta.doc_items:
            if it.label == label:
                num_found += 1
                if num_found == n:
                    return i, chunk
    return None, None


def chunk_it(source, chnkr) -> list[Document]:
    converter = DocumentConverter()
    i = 0
    texts = []
    # with console.screen():
    for i, chunk in enumerate(chnkr.chunk(converter.convert(source=source).document)):
        print(f"Chunks for Doc #{i}: {len(chunk.meta.doc_items)}")
        texts.append(
            Document(
                page_content=chunk.text,
                id=uuid.uuid4(),
                metadata={"doc_id": (i := i + 1), "source": source},
            )
        )
    return texts


def chunk_documents(
    docs: Iterable[Document], chunk_char_size: int = 700, chunk_char_overlap: int = 20
):
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_char_size,  # The maximum number of characters in a chunk
        chunk_overlap=chunk_char_overlap,  # The number of characters to overlap between chunks
    )

    # Split the documents into chunks
    return text_splitter.split_documents(docs)


def convert_json_to_langchain_docs(data, text_column, metadata_key="metadata"):
    data_to_convert = json.loads(data) if isinstance(data, str) else data
    langchain_documents = []
    for doc in data_to_convert:
        if doc[text_column] is not None:
            langchain_documents.append(
                Document(
                    page_content=doc[text_column],
                    id=doc["uuid"],
                    metadata=doc[metadata_key],
                )
            )
    return langchain_documents
