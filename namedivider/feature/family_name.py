import pickle
from pathlib import Path
from typing import Union, cast

import numpy as np

from namedivider.util import get_verified_family_name_bytes


class FamilyNameRepository:
    def __init__(self, path_txt: Union[str, Path]):
        """
        :param path_txt: Path of a file with multiple family names enumerated.
        This is in order of the most common family names in Japan.
        Format is following:
        ------------
        佐藤
        鈴木
        高橋
        ...
        ------------
        """
        with open(path_txt, encoding="utf-8") as f:
            lines = f.read().splitlines()
        families = [line for line in lines if line.strip()]
        self.__family_names = {}
        for rank, family in enumerate(families):
            self.__family_names[family] = rank

    @classmethod
    def from_path(cls, path: Union[str, Path]) -> "FamilyNameRepository":
        """Load a verified standard dictionary or a custom pickle/text dictionary."""
        content = get_verified_family_name_bytes(path)
        if content is not None:
            # Restore the verified snapshot; never reopen the standard cache.
            return cast("FamilyNameRepository", pickle.loads(content))
        if Path(path).suffix == ".pickle":
            with open(path, "rb") as file:
                return cast("FamilyNameRepository", pickle.load(file))
        return cls(path_txt=path)

    def exists(self, family: str) -> bool:
        """
        Returns if the family name entered is included in the pre-prepared family names.
        :param family: Family name.
        :return: bool
        """
        return family in self.__family_names

    def get_rank(self, family: str) -> Union[int, float]:
        """
        Returns the rank of the family name entered.
        :param family: Family name.
        :return:
        """
        if self.exists(family):
            return self.__family_names[family]
        else:
            return np.nan
