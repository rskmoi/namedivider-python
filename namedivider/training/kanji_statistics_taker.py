from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Tuple, Union

import numpy as np
import pandas as pd
import regex

from namedivider.feature.kanji import KanjiStatistics


class KanjiStatisticsMode(Enum):
    ONLY_FREQUENT_KANJI = auto()
    ONLY_KANJI = auto()
    ALL = auto()


class KanjiStatisticsTaker:
    """
    Create assets/kanji.csv from names.
    """

    def __init__(self, mode: KanjiStatisticsMode = KanjiStatisticsMode.ONLY_FREQUENT_KANJI):
        self.statistics: Dict[str, KanjiStatistics] = {}
        self.mode = mode
        self.compiled_regex_kanji = regex.compile(r"\p{Script=Han}+")

    def is_target(self, target_kanji_statistics: KanjiStatistics) -> bool:
        if self.mode == KanjiStatisticsMode.ALL:
            return True
        elif self.mode == KanjiStatisticsMode.ONLY_KANJI:
            if self.compiled_regex_kanji.fullmatch(target_kanji_statistics.kanji):
                return True
            return False
        elif self.mode == KanjiStatisticsMode.ONLY_FREQUENT_KANJI:
            if np.sum(target_kanji_statistics.order_counts) < 10:
                return False
            if self.compiled_regex_kanji.fullmatch(target_kanji_statistics.kanji):
                return True
            return False
        return True

    @staticmethod
    def get_order(name: str, idx: int, is_family: bool) -> int:
        if is_family:
            if idx == 0:
                return 0
            if idx == len(name) - 1:
                return 2
            return 1
        else:
            if idx == len(name) - 1:
                return 5
            if idx == 0:
                return 3
            return 4

    @staticmethod
    def get_length(name: str, is_family: bool) -> int:
        if is_family:
            return min(len(name) - 1, 3)
        else:
            return min(len(name) - 1 + 4, 7)

    def set_kanji(self, text: str) -> None:
        for _kanji in text:
            if _kanji not in self.statistics:
                self.statistics[_kanji] = KanjiStatistics(
                    kanji=_kanji,
                    order_counts=np.array([0, 0, 0, 0, 0, 0]),
                    length_counts=np.array([0, 0, 0, 0, 0, 0, 0, 0]),
                )

    def set_count(self, kanji: str, order: int, length: int) -> None:
        self.statistics[kanji].order_counts[order] += 1
        self.statistics[kanji].length_counts[length] += 1

    def append(self, family: str, given: str) -> None:
        self.set_kanji(family + given)
        for i, _kanji in enumerate(family):
            _order = self.get_order(family, i, is_family=True)
            _length = self.get_length(family, is_family=True)
            self.set_count(kanji=_kanji, order=_order, length=_length)
        for i, _kanji in enumerate(given):
            _order = self.get_order(given, i, is_family=False)
            _length = self.get_length(given, is_family=False)
            self.set_count(kanji=_kanji, order=_order, length=_length)

    def to_csv(self, dst: Union[str, Path]) -> None:
        stats: List[Tuple[str, KanjiStatistics]] = sorted(self.statistics.items(), key=lambda x: x[0])
        items = []
        for _key, _stat in stats:
            if not self.is_target(_stat):
                continue
            items.append(
                {
                    "kanji": _stat.kanji,
                    "oc_family_first": _stat.order_counts[0],
                    "oc_family_other": _stat.order_counts[1],
                    "oc_family_last": _stat.order_counts[2],
                    "oc_given_first": _stat.order_counts[3],
                    "oc_given_other": _stat.order_counts[4],
                    "oc_given_last": _stat.order_counts[5],
                    "lc_family_1": _stat.length_counts[0],
                    "lc_family_2": _stat.length_counts[1],
                    "lc_family_3": _stat.length_counts[2],
                    "lc_family_4": _stat.length_counts[3],
                    "lc_given_1": _stat.length_counts[4],
                    "lc_given_2": _stat.length_counts[5],
                    "lc_given_3": _stat.length_counts[6],
                    "lc_given_4": _stat.length_counts[7],
                }
            )
        df = pd.DataFrame(items)
        df.to_csv(dst, index=False)

    def show(self) -> None:
        stats = sorted(self.statistics.items(), key=lambda x: x[0])
        for _key, _stat in stats:
            if not self.is_target(_stat):
                continue
            print(_stat)
