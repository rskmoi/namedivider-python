from __future__ import annotations

import pytest

from namedivider.divided_name import DividedNameDict
from namedivider.name_divider import NameDivider

name_test_data: list[tuple[str, DividedNameDict]] = [
    (
        "原敬",
        {
            "family": "原",
            "given": "敬",
            "separator": "_",
            "score": 1.0,
            "algorithm": "rule",
        },
    ),
    (
        "菅義偉",
        {
            "family": "菅",
            "given": "義偉",
            "separator": "_",
            "score": 0.6328842762252201,
            "algorithm": "kanji_feature",
        },
    ),
    (
        "阿部晋三",
        {
            "family": "阿部",
            "given": "晋三",
            "separator": "_",
            "score": 0.5745842309372197,
            "algorithm": "kanji_feature",
        },
    ),
    (
        "中曽根康弘",
        {
            "family": "中曽根",
            "given": "康弘",
            "separator": "_",
            "score": 0.3705325993396728,
            "algorithm": "kanji_feature",
        },
    ),
    (
        "中山マサ",
        {
            "family": "中山",
            "given": "マサ",
            "separator": "_",
            "score": 1.0,
            "algorithm": "rule",
        },
    ),
]


@pytest.mark.parametrize("undivided_name, expect", name_test_data)
def test_divide_name(undivided_name: str, expect: DividedNameDict) -> None:
    name_divider = NameDivider(separator="_")
    divided_name = name_divider.divide_name(undivided_name)
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


def test_divide_name_error() -> None:
    name_divider = NameDivider()
    caught_error = False
    try:
        name_divider.divide_name("原")
    except ValueError:
        caught_error = True
    assert caught_error
