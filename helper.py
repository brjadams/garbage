from typing import Iterable, Optional

from docling_core.transforms.chunker.base import BaseChunk
from docling_core.transforms.chunker.hierarchical_chunker import DocChunk
from docling_core.types.doc.labels import DocItemLabel
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from docling.document_converter import DocumentConverter
from langchain_core.documents import Document

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


def print_chunk(chunks, chunk_pos):
    chunk = chunks[chunk_pos]
    ctx_text = chunker.contextualize(chunk=chunk)
    num_tokens = tokenizer.count_tokens(text=ctx_text)
    doc_items_refs = [it.self_ref for it in chunk.meta.doc_items]
    title = f"{chunk_pos=} {num_tokens=} {doc_items_refs=}"
    console.print(Panel(ctx_text, title=title))

def get_converted_doc(fp):
    # Convert CSV to Docling document
    converter = DocumentConverter()
    result = converter.convert(source=Path(fp)).document
    return result
    # output = result.document.export_to_markdown()
    
def chunk_it(source, chnkr) -> list[Document]:
    converter = DocumentConverter()
    i = 0
    texts = [] 
    for chunk in chnkr.chunk(converter.convert(source=source).document):
        print(chunk.meta.doc_items)
        texts.append(Document(page_content=chunk.text, metadata={"doc_id": (i:=i+1), "source": source}))
    return texts
