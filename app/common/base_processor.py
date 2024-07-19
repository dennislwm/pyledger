from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import yaml

class BaseProcessor(ABC):
    def __init__(self):
        self.rules: dict = {}
        self.headers: dict = {}