import abc
import warnings
from typing import List, Optional

import numpy as np
import regex

from namedivider.divider.config import (
    NameDividerConfigBase,
    NameDividerVersions,
    get_config_from_version,
)
from namedivider.divider.divided_name import DividedName
from namedivider.rule.pipeline import Pipeline


class _UndividedNameHolder:
    def __init__(self, original_name: str):
        """
        Class to hold original and normalized name for dividing.
        :param original_name: Original name
        """
        self.original_name = original_name
        self.normalized_name = self._normalize(original_name)

    @staticmethod
    def _normalize(original_name: str) -> str:
        """
        Normalize name.
        'Normalize' here means to convert old character form(旧字体) or variant character form(異字体)
        into orthographic character form(正字体).
        :param original_name: Original name
        :return: str: Normalized name.
        """
        name = original_name
        old_new_pairs = [("髙", "高"), ("𠮷", "吉")]
        for _old, _new in old_new_pairs:
            name = name.replace(_old, _new)
        return name

    def get_divided_original_name(self, divided_normalized_name: DividedName) -> DividedName:
        """
        Get divided original name using divided normalize name.
        :param divided_normalized_name: Divided name by normalized name.
        :return: Divided name by original name.
        """
        _family_length = len(divided_normalized_name.family)
        _family = self.original_name[:_family_length]
        _given = self.original_name[_family_length:]
        return DividedName(
            _family,
            _given,
            separator=divided_normalized_name.separator,
            score=divided_normalized_name.score,
            algorithm=divided_normalized_name.algorithm,
        )


class _NameDivider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, config: Optional[NameDividerConfigBase] = None):
        """
        Base Class for dividing an undivided name.
        ("undivided name" means names with no space between the family name and given name.)
        All NameDividers inherit this class.
        :param config: Configuration of NameDivider.
        """
        if config is None:
            config = NameDividerConfigBase()
        self.separator = config.separator
        self.normalize_name = config.normalize_name
        self.algorithm_name = config.algorithm_name
        self._rule_pipeline = Pipeline(separator=self.separator, custom_rules=config.custom_rules)
        self._compiled_regex_kanji = regex.compile(r"\p{Script=Han}+")

    @abc.abstractmethod
    def calc_score(self, family: str, given: str) -> float:
        """
        Calculates the score. The higher the score, the more likely the division is correct.
        :param family: Family name.
        :param given: Given name.
        :return: Score of dividing.
        """
        pass

    @classmethod
    def from_version(cls, version: NameDividerVersions) -> "_NameDivider":
        """
        Create instance by model version.
        :param version: Version of divider.
        :return: NameDivider instance constructed by model version.
        :rtype: _NameDivider
        """
        config = get_config_from_version(version)
        return cls(config=config)

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
    def _validate(undivided_name: str) -> None:
        """
        Determines if it is an assumed input.
        :param undivided_name: Names with no space between the first and last name
        """
        if len(undivided_name) < 2:
            raise ValueError("Name length needs at least 2 chars")

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

    @property
    def compiled_regex_kanji(self):  # type: ignore
        """
        This property was added for only backward compatibility.
        """
        warnings.warn(
            "_NameDivider.compiled_regex_kanji is deprecated in 0.3 and will be removed in 0.4. "
            "Use regex.compile if you want to use compiled_regex_kanji.",
            category=FutureWarning,
            stacklevel=1,
        )
        return self._compiled_regex_kanji

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
        divided_name_or_none = self._rule_pipeline.apply(undivided_name)

        return divided_name_or_none

    def _divide_by_algorithm(self, undivided_name: str) -> DividedName:
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
            algorithm=self.algorithm_name,
        )

    def _divide_name(self, undivided_name: str) -> DividedName:
        """
        Divides undivided name.
        :param undivided_name: Names with no space between the family name and given name
        :return: Divided name
        :rtype: DividedName
        """
        divided_name_by_rule_base = self._divide_by_rule_base(undivided_name)
        if divided_name_by_rule_base:
            return divided_name_by_rule_base
        return self._divide_by_algorithm(undivided_name)

    def divide_name(self, undivided_name: str) -> DividedName:
        """
        Divides undivided name.
        :param undivided_name: Names with no space between the family name and given name
        :return: Divided name
        :rtype: DividedName
        """
        self._validate(undivided_name)
        if self.normalize_name:
            holder = _UndividedNameHolder(undivided_name)
            divided_name = self._divide_name(holder.normalized_name)
            return holder.get_divided_original_name(divided_name)
        else:
            return self._divide_name(undivided_name)
