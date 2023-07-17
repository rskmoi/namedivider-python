from typing import Dict

import pytest

from namedivider.divider.config import NameDividerConfigBase
from namedivider.divider.name_divider_base import _NameDivider


class NameDividerForTest(_NameDivider):
    def __init__(self, config: NameDividerConfigBase = None):
        if config is None:
            config = NameDividerConfigBase()
        super().__init__(config=config)

    def calc_score(self, family: str, given: str) -> float:
        plus_score = 0.0
        if "𠮷" in family + given:
            plus_score = 10.0 * len(family)
        score = len(family) + plus_score
        return score


def test_set_separator():
    undivided_name = "手須戸𠮷郎"
    separator = "/"
    config = NameDividerConfigBase(separator=separator)
    divider = NameDividerForTest(config=config)
    divided_name = divider.divide_name(undivided_name)
    assert divided_name.separator == separator


def test_set_normalize_name():
    undivided_name = "手須戸𠮷郎"
    config = NameDividerConfigBase(normalize_name=True)
    divider = NameDividerForTest(config=config)
    divided_name = divider.divide_name(undivided_name)
    assert divided_name.score == 0.6439142598879722

    config = NameDividerConfigBase(normalize_name=False)
    divider = NameDividerForTest(config=config)
    divided_name = divider.divide_name(undivided_name)
    assert divided_name.score == 0.9999832982992098


def test_is_original_when_normalize_mode():
    undivided_name = "手須戸𠮷郎"
    config = NameDividerConfigBase(normalize_name=True)
    divider = NameDividerForTest(config=config)
    divided_name = divider.divide_name(undivided_name)
    assert divided_name.family + divided_name.given == undivided_name


name_test_data = [
    ("原敬", {"family": "原", "given": "敬", "separator": "_", "score": 1.0, "algorithm": "rule"}),
    ("中山マサ", {"family": "中山", "given": "マサ", "separator": "_", "score": 1.0, "algorithm": "rule"}),
    (
        "菅義偉",
        {"family": "菅義", "given": "偉", "separator": "_", "score": 0.7310585786300049, "algorithm": "unknown_algorithm"},
    ),
]


@pytest.mark.parametrize("undivided_name, expect", name_test_data)
def test_divide_name(undivided_name: str, expect: Dict):
    config = NameDividerConfigBase(separator="_")
    name_divider = NameDividerForTest(config=config)
    divided_name = name_divider.divide_name(undivided_name)
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


def test_divide_name_error():
    config = NameDividerConfigBase(separator="_")
    name_divider = NameDividerForTest(config=config)
    caught_error = False
    try:
        name_divider.divide_name("原")
    except ValueError:
        caught_error = True
    assert caught_error
