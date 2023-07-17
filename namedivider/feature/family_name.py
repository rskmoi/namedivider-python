import os
from pathlib import Path
from typing import Union

import numpy as np


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
        with open(path_txt, "rb") as f:
            family_text = f.read().decode()
        self.__family_names = {}
        for rank, _family in enumerate(family_text.split(os.linesep)):
            self.__family_names[_family] = rank

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
