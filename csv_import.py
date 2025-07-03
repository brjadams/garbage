from dataclasses import dataclass, field
from typing import List, Optional
from langchain_core.documents import Document  # Import LangChain Document type
import pandas as pd
import json
import os
import pdb


@dataclass
class CsvProcessor:
    """
    A data class to process CSV files and export their content to JSON format.
    """

    csv_file_name: str
    df: pd.DataFrame = field(init=False, default=None)  # type: ignore # df is not initialized by __init__

    def __post_init__(self):
        """
        Initializes the DataFrame after the dataclass's __init__ method.
        This is where the CSV file is read into a pandas DataFrame.
        """
        try:
            # Check if the CSV file exists before attempting to read
            print(f"FileName: {self.csv_file_name}")
            if not os.path.exists(self.csv_file_name):
                raise FileNotFoundError(f"CSV file not found: {self.csv_file_name}")

            # Read the CSV file into a pandas DataFrame
            self.df = pd.read_csv(self.csv_file_name, delimiter="\t")
            self.df.columns = self.df.columns.str.replace(" ", "_")
            self.df.dropna(subset=['tweet_text'], inplace=True)
            print(f"Successfully loaded CSV: {self.csv_file_name}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except pd.errors.EmptyDataError:
            print(f"Error: CSV file '{self.csv_file_name}' is empty.")
        except pd.errors.ParserError:
            print(
                f"Error: Could not parse CSV file '{self.csv_file_name}'. Check its format."
            )
        except Exception as e:
            print(f"An unexpected error occurred while reading CSV: {e}")

    def export_to_json(
        self,
        keys_to_drop: Optional[List[str]] = None,
        keys_to_metadata: Optional[List[str]] = None,
    ) -> str:
        """
        Exports the loaded CSV data to a JSON formatted string.
        Optionally drops a specified list of columns from the DataFrame before conversion.
        Optionally moves a specified list of column values into a nested 'metadata' key.

        Args:
            keys_to_drop (List[str], optional): A list of column names to drop from the DataFrame.
                                                Defaults to None, meaning no columns are dropped.
            keys_to_metadata (List[str], optional): A list of column names whose values should be
                                                    moved into a nested 'metadata' dictionary.
                                                    These columns will then be dropped from the main record.
                                                    Defaults to None, meaning no keys are moved to metadata.

        Returns:
            str: A JSON formatted string representation of the data, or an empty string if no data is loaded.
        """
        if self.df is None:
            print(
                "Error: No data loaded. Please ensure the CSV file was loaded successfully."
            )
            return ""  # Return empty string if no data

        try:
            df_to_export = (
                self.df.copy()
            )  # Work on a copy to avoid modifying the original DataFrame

            # --- Handle keys to drop directly from DataFrame ---
            if keys_to_drop:
                existing_columns_to_drop = [
                    col for col in keys_to_drop if col in df_to_export.columns
                ]
                non_existent_columns_drop = [
                    col for col in keys_to_drop if col not in df_to_export.columns
                ]

                if existing_columns_to_drop:
                    df_to_export = df_to_export.drop(columns=existing_columns_to_drop)
                    print(
                        f"Dropped columns: {existing_columns_to_drop} from the DataFrame."
                    )
                if non_existent_columns_drop:
                    print(
                        f"Warning: Columns {non_existent_columns_drop} not found in DataFrame for dropping. They were not dropped."
                    )

            # Convert (potentially modified) DataFrame to a list of dictionaries for further processing
            list_of_dicts = df_to_export.to_dict(orient="records")
            processed_dicts = []

            # --- Handle keys to move to metadata ---
            if keys_to_metadata:
                for original_dict in list_of_dicts:
                    new_record = original_dict.copy()
                    metadata_dict = {}
                    columns_moved_to_metadata = []
                    non_existent_columns_metadata = []

                    for key in keys_to_metadata:
                        if key in new_record:
                            metadata_dict[key] = new_record.pop(
                                key
                            )  # Move value and remove from main dict
                            columns_moved_to_metadata.append(key)
                        else:
                            non_existent_columns_metadata.append(key)

                    if metadata_dict:  # Only add metadata key if there's content
                        new_record["metadata"] = metadata_dict
                    if non_existent_columns_metadata:
                        print(
                            f"Warning: Columns {non_existent_columns_metadata} not found in record for metadata. They were not moved."
                        )

                    processed_dicts.append(new_record)
                data_to_json = processed_dicts
            else:
                data_to_json = list_of_dicts

            # Export the final list of dictionaries to a JSON string
            json_string = json.dumps(data_to_json, indent=4)
            print("Successfully exported data to JSON string.")
            return json_string
        except Exception as e:
            print(f"An error occurred while exporting to JSON string: {e}")
            return ""  # Return empty string on error
