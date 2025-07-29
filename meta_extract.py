from docling_core.transforms.chunker.base import BaseChunk
from langchain_docling.loader import BaseMetaExtractor
import pdb

# --- 2. Custom Meta Extractor CLASS with 'extract_chunk_meta' method ---
class BlueSkyMetaExtractor(BaseMetaExtractor):
    """
    A custom meta extractor designed to work with DoclingLoader's expectation
    of an object with an 'extract_chunk_meta' method.
    """
    def extract_chunk_meta(self, file_path, chunk:BaseChunk) -> dict:
        """
        Extracts metadata from a DoclingDocument (which is a chunk in this context)
        that originated from a CSV row following the new moderation data model.
        """
        
        extracted_metadata = {}
        # print(f"DOCCCC:::::::{chunk}")
        table_element = None
        # In this context, docling might already give us a DoclingDocument that
        # represents a chunk, and its 'body' might contain the row's data directly
        # or still wrap it in a Table element if the chunk is derived from a table row.
        # We'll stick to navigating the Table element as it's safer for CSVs.
        # print(dir(chunk))
        row = {}
        row_text = chunk.text
        # pdb.set_trace()

        # Extracting and converting new fields
        try:
            extracted_metadata["row_id"] = int(row_data.get("row_id", 0))
        except (ValueError, TypeError):
            extracted_metadata["row_id"] = None

        extracted_metadata["mod_class"] = row_data.get("mod_class")

        try:
            extracted_metadata["confidence"] = float(row_data.get("confidence", 0.0))
        except (ValueError, TypeError):
            extracted_metadata["confidence"] = 0.0

        top_groups_str = row_data.get("top_groups")
        if top_groups_str:
            extracted_metadata["top_groups"] = [g.strip() for g in top_groups_str.split('|') if g.strip()]
        else:
            extracted_metadata["top_groups"] = []

        try:
            extracted_metadata["match_score"] = float(row_data.get("match_score", 0.0))
        except (ValueError, TypeError):
            extracted_metadata["match_score"] = 0.0

        try:
            extracted_metadata["tweet_length"] = int(row_data.get("tweet_length", 0))
        except (ValueError, TypeError):
            extracted_metadata["tweet_length"] = 0

        try:
            extracted_metadata["score_per_100_char"] = float(row_data.get("score_per_100_char", 0.0))
        except (ValueError, TypeError):
            extracted_metadata["score_per_100_char"] = 0.0

        extracted_metadata["screen_name"] = row_data.get("screen_name")
        extracted_metadata["original_tweet_text"] = row_data.get("tweet_text")

        return extracted_metadata

