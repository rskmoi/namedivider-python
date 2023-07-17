import warnings
from pathlib import Path
from typing import List, Optional

import numpy as np
import numpy.typing as npt
import pandas as pd
import regex

from namedivider.divider.divided_name import DividedName
from namedivider.feature.kanji import KanjiStatistics

CURRENT_DIR = Path(__file__).resolve().parent


class NameDivider:
    def __init__(self, path_csv: str = f"{CURRENT_DIR}/assets/kanji.csv", separator: str = " "):
        """
        Class for dividing an undivided name
        ("undivided name" means names with no space between the family name and given name.)
        :param path_csv: Path of the file containing the kanji information
        :param separator: Characters to separate first and last names
        """
        warnings.warn(
            "Class NameDivider is deprecated in 0.2 and will be removed in 0.4. "
            "Use BasicNameDivider.from_version(NameDividerVersions.BASIC_NAME_DIVIDER_V1) "
            "if you want to use a class with same behavior.",
            category=FutureWarning,
            stacklevel=1,
        )
        kanji_records = pd.read_csv(path_csv).to_numpy()
        kanjis = kanji_records[:, 0]
        orders = kanji_records[:, 1:7]
        lengths = kanji_records[:, 7:]

        self.kanji_dict = {}
        for _kanji, _order, _length in zip(kanjis, orders, lengths):
            self.kanji_dict[_kanji] = KanjiStatistics(kanji=_kanji, order_counts=_order, length_counts=_length)

        self.default_kanji = KanjiStatistics.default()
        self.separator = separator
        self.compiled_regex_kanji = regex.compile(r"\p{Script=Han}+")

    def _create_divided_name(self, family: str, given: str, score: float = 1.0, algorithm: str = "") -> DividedName:
        """
        Generates DividedName.
        :param family: Family name
        :param given: Given name
        :param score: Confidence level, from 0 to 1
        :param algorithm: The name of dividing algorithm
        :return: Divided name
        :rtype: DividedName
        """
        return DividedName(family, given, separator=self.separator, score=score, algorithm=algorithm)

    @staticmethod
    def _create_order_mask(full_name_length: int, char_idx: int) -> npt.NDArray[np.int32]:
        """
        Create order mask.
        Order mask is one-hot mask for calculate order score.
        :param full_name_length: Length of full name.
        :param char_idx: The order of the character in full name
        :return: Order mask
        :rtype: np.ndarray
        """
        if char_idx == 0 or char_idx == full_name_length - 1:
            raise ValueError("First character and last character must not be created order mask.")

        if full_name_length == 3:
            return np.array([0, 0, 1, 1, 0, 0])

        if char_idx == 1:
            return np.array([0, 1, 1, 1, 0, 0])

        if char_idx == full_name_length - 2:
            return np.array([0, 0, 1, 1, 1, 0])

        return np.array([0, 1, 1, 1, 1, 0])

    @staticmethod
    def _create_length_mask(full_name_length: int, char_idx: int) -> npt.NDArray[np.int32]:
        """
        Create length mask.
        Length mask is one-hot mask for calculate length score.
        :param full_name_length: Length of full name.
        :param char_idx: The order of the character in full name
        :return: Length mask
        :rtype: np.ndarray
        """
        min_family = char_idx + 1
        max_family = full_name_length - 1
        max_family = 4 if max_family > 4 else max_family
        min_given = full_name_length - char_idx
        max_given = full_name_length - 1
        max_given = 4 if max_given > 4 else max_given
        lc_family = np.array([0, 0, 0, 0])
        if min_family <= max_family:
            lc_family[min_family - 1 : max_family] = 1
        lc_given = np.array([0, 0, 0, 0])
        if min_given <= max_given:
            lc_given[min_given - 1 : max_given] = 1
        return np.concatenate([lc_family, lc_given])

    @staticmethod
    def _calc_current_order_status(
        piece_of_divided_name: str, idx_in_piece_of_divided_name: int, is_family: bool
    ) -> int:
        """
        Determine which index of order_counts the kanji corresponds to.
        :param piece_of_divided_name: Family name or given name
        :param idx_in_piece_of_divided_name: Index in family or given name
        :param is_family: True if piece_of_divided_name is family name
        :return: The index of order_counts
        :rtype: int
        """
        if idx_in_piece_of_divided_name == 0:
            return 0 if is_family else 3
        if idx_in_piece_of_divided_name == len(piece_of_divided_name) - 1:
            return 2 if is_family else 5
        else:
            return 1 if is_family else 4

    @staticmethod
    def _calc_current_length_status(piece_of_divided_name: str, is_family: bool) -> int:
        """
        Determine which index of length_counts the kanji corresponds to.
        :param piece_of_divided_name: Family name or given name
        :param is_family: True if piece_of_divided_name is family name
        :return: The index of length_counts
        :rtype: int
        """
        piece_of_divided_name_length = len(piece_of_divided_name) if len(piece_of_divided_name) <= 4 else 4
        return piece_of_divided_name_length - 1 if is_family else piece_of_divided_name_length - 1 + 4

    def _calc_order_score(self, piece_of_divided_name: str, full_name_length: int, start_index: int = 0) -> float:
        """
        Calculates order score.
        Order score is a feature, which is a kind of frequency, calculated from where each kanji in full name is used.
        See this link if you need more explanation: https://rskmoi.hatenablog.com/entry/2017/01/15/190837
        :param piece_of_divided_name: Family name or given name
        :param full_name_length: Length of fullname
        :param start_index: The order of the first charactar of piece_of_divided_name in full name
        :return: Order score
        :rtype: float

        example:
        -----------------------------------------------------
        >>> namedivider = NameDivider()
        >>> # Full name: 新海誠
        >>> namedivider._calc_order_score(piece_of_divided_name='新海', full_name_length=3, start_index=0)
        0.8305084745762712
        >>> namedivider._calc_order_score(piece_of_divided_name='誠', full_name_length=3, start_index=2)
        0
        >>> # Full name: 清武弘嗣
        >>> namedivider._calc_order_score(piece_of_divided_name='清武', full_name_length=4, start_index=0)
        0.2222222222222222
        >>> namedivider._calc_order_score(piece_of_divided_name='弘嗣', full_name_length=4, start_index=2)
        0.9919571045576407
        -----------------------------------------------------
        """
        is_family = True if start_index == 0 else False
        scores = 0
        for idx_in_piece_of_divided_name, _kanji in enumerate(piece_of_divided_name):
            current_idx = start_index + idx_in_piece_of_divided_name
            if current_idx == 0:
                continue
            if current_idx == full_name_length - 1:
                continue
            mask = self._create_order_mask(full_name_length, current_idx)
            current_order_status_idx = self._calc_current_order_status(
                piece_of_divided_name, idx_in_piece_of_divided_name, is_family
            )
            masked_order = self.kanji_dict.get(_kanji, self.default_kanji).order_counts * mask
            if np.sum(masked_order) == 0:
                continue
            scores += masked_order[current_order_status_idx] / np.sum(masked_order)
        return scores

    def _calc_length_score(self, piece_of_divided_name: str, full_name_length: int, start_index: int = 0) -> float:
        """
        Calculates length score.
        Length score is a feature, which is a kind of frequency,
        calculated from how long is family/given name containing the kanji.
        See this link if you need more explanation: https://rskmoi.hatenablog.com/entry/2017/01/15/190837
        :param piece_of_divided_name: Family name or given name
        :param full_name_length: Length of fullname
        :param start_index: The order of the first charactar of piece_of_divided_name in full name
        :return: Length score
        :rtype: float

        example:
        -----------------------------------------------------
        >>> namedivider = NameDivider()
        >>> # Full name: 新海誠
        >>> namedivider._calc_length_score(piece_of_divided_name='新海', full_name_length=3, start_index=0)
        1.6721919841662545
        >>> namedivider._calc_length_score(piece_of_divided_name='誠', full_name_length=3, start_index=2)
        0.5414201183431953
        >>> # Full name: 清武弘嗣
        >>> namedivider._calc_length_score(piece_of_divided_name='清武', full_name_length=4, start_index=0)
        1.9431977559607292
        >>> namedivider._calc_length_score(piece_of_divided_name='弘嗣', full_name_length=4, start_index=2)
        1.982873228774868
        -----------------------------------------------------
        """
        is_family = True if start_index == 0 else False
        scores = 0
        for i, _kanji in enumerate(piece_of_divided_name):
            current_idx = start_index + i
            mask = self._create_length_mask(full_name_length, current_idx)
            current_length_status_idx = self._calc_current_length_status(piece_of_divided_name, is_family)
            masked_length_scores = self.kanji_dict.get(_kanji, self.default_kanji).length_counts * mask
            if np.sum(masked_length_scores) == 0:
                continue
            scores += masked_length_scores[current_length_status_idx] / np.sum(masked_length_scores)
        return scores

    def calc_score(self, family: str, given: str) -> float:
        """
        Calculates the score for correct division.
        :param family: Family name
        :param given: Given name
        :return: Score for correct division
        :rtype: float
        """
        name = family + given
        order_score_family = self._calc_order_score(family, len(name), 0)
        order_score_given = self._calc_order_score(given, len(name), len(family))
        order_score = (order_score_family + order_score_given) / (len(name) - 2)

        # If full name consists of 4 chars, the accuracy is better when using only order score.
        if len(name) == 4:
            return order_score

        length_score_family = self._calc_length_score(family, len(name), 0)
        length_score_given = self._calc_length_score(given, len(name), len(family))
        length_score = (length_score_family + length_score_given) / len(name)

        return (order_score + length_score) / 2

    @staticmethod
    def _validate(undivided_name: str) -> None:
        """
        Determines if it is an assumed input.
        :param undivided_name: Names with no space between the first and last name
        """
        if len(undivided_name) < 2:
            raise ValueError("Name length needs at least 2 chars")

    def _divide_by_rule_base(self, undivided_name: str) -> Optional[DividedName]:
        """
        Divides undivided name without using kanji statistics.
        :param undivided_name: Names with no space between the family name and given name
        :return:
            if fits the rules: Divided name
            else: None
        :rtype:
            if fits the rules: DividedName
            else: None
        """
        # If the undivided name consists of 2 characters,
        # the first characters is family name, and the last characters is given name.
        if len(undivided_name) == 2:
            return self._create_divided_name(family=undivided_name[0], given=undivided_name[-1], algorithm="rule")

        # If the undivided name consists of kanji and other types of characters (hiragana, katakana, etc...),
        # the undivided name will be divided where the kanji and other character types are switched.
        # The criterion for determining switched is whether "two" consecutive characters are having
        # different type of characters from first character type.
        # The reason of "two" is some family names consist of some kanji and one katakana.
        # (ex: "井ノ原", "三ツ又",　"関ヶ原" contains "ノ", "ツ", "ヶ". They are all katakana.)
        is_kanji_list = []
        for i, _char in enumerate(undivided_name):
            is_kanji = True if self.compiled_regex_kanji.fullmatch(_char) else False
            is_kanji_list.append(is_kanji)
            if i >= 2:
                if is_kanji_list[0] != is_kanji and is_kanji_list[-2] == is_kanji:
                    return self._create_divided_name(
                        family=undivided_name[: i - 1], given=undivided_name[i - 1 :], algorithm="rule"
                    )

        return None

    @staticmethod
    def _softmax(x: List[float]) -> List[float]:
        """
        Calculates softmax score
        :param x: array_like
        :return: Softmax scores
        :rtype: np.ndarray
        """
        u = np.sum(np.exp(x))
        softmax_val: List[float] = np.exp(x) / u
        return softmax_val

    def _divide_by_statistics(self, undivided_name: str) -> DividedName:
        """
        Divides undivided name using kanji statistics.
        :param undivided_name: Names with no space between the family name and given name
        :return: Divided name
        :rtype: DividedName
        """
        total_scores = []
        for i in range(1, len(undivided_name)):
            family = undivided_name[:i]
            given = undivided_name[i:]
            score = self.calc_score(family, given)
            total_scores.append(score)

        total_scores = self._softmax(total_scores)
        max_idx = np.argmax(np.array(total_scores)) + 1
        return self._create_divided_name(
            family=undivided_name[:max_idx],
            given=undivided_name[max_idx:],
            score=total_scores[max_idx - 1],
            algorithm="kanji_feature",
        )

    def divide_name(self, undivided_name: str) -> DividedName:
        """
        Divides undivided name.
        :param undivided_name: Names with no space between the family name and given name
        :return: Divided name
        :rtype: DividedName

        example:
        -----------------------------------------------------
        >>> namedivider = NameDivider()
        >>> divided_name = namedivider.divide_name("菅義偉")
        >>> print(divided_name)
        "菅 義偉"
        >>> print(divided_name.to_dict())
        {'family': '菅', 'given': '義偉', 'separator': ' ', 'score': 0.6328842762252201, 'algorithm': 'kanji_feature'}
        -----------------------------------------------------
        """
        self._validate(undivided_name)
        divided_name_by_rule_base = self._divide_by_rule_base(undivided_name)
        if divided_name_by_rule_base:
            return divided_name_by_rule_base
        return self._divide_by_statistics(undivided_name)
