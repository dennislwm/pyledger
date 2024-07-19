from abc import ABC
import pandas as pd
from app.common.base_processor import BaseProcessor

class XlsProcessor(BaseProcessor, ABC):
    def load_rules(self) -> dict:
        # Implement logic to load rules specific to XLS files
        # For demonstration, returning an empty dict
        return {}

    def load_input_file(self) -> pd.DataFrame:
        # Implement logic to load an XLS file
        # For demonstration, returning an empty DataFrame
        return pd.DataFrame()

    def get_header(self) -> dict:
        # Implement logic to retrieve headers specific to XLS files
        # For demonstration, returning an empty dict
        return {}
