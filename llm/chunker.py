from chonkie import NeuralChunker


def chonkie_neural(documents, model_id):
    # Basic initialization with default parameters
    chunker = NeuralChunker(
        # model="mirth/chonky_modernbert_base_1",  # Default model
        model=model_id,
        device_map="cpu",                        # Device to run the model on ('cpu', 'cuda', etc.)
        min_characters_per_chunk=10,             # Minimum characters for a chunk
    )

    batch_chunks = chunker.chunk_batch(documents)

    for doc_chunks in batch_chunks:
        for chunk in doc_chunks:
            print(f"Chunk: {chunk.text}")