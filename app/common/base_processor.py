from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import yaml

class BaseProcessor(ABC):
    def __init__(self):
        self.rules: dict = {}
        self.headers: dict = {}

    @abstractmethod
    def load_rules(self) -> dict:
        """Load rules into the rules attribute."""
        pass

    @abstractmethod
    def load_input_file(self) -> pd.DataFrame:
        """Load input file and return as a DataFrame."""
        pass

    @abstractmethod
    def get_header(self) -> dict:
        """Return the headers attribute."""
        pass
