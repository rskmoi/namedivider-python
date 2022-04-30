import numpy as np
from typing import Union
from pathlib import Path


class FamilyNameRepository:
    def __init__(self, path_txt:  Union[str, Path]):
        with open(path_txt, "rb") as f:
            family_text = f.read().decode()
        self.family_names = family_text.split("\n")

    def exists(self, family: str):
        return family in self.family_names

    def get_rank(self, family: str):
        if self.exists(family):
            return self.family_names.index(family)
        else:
            return np.nan
