from typing import Dict

import pytest

from namedivider.divider.basic_name_divider import BasicNameDivider
from namedivider.divider.config import NameDividerVersions

name_test_data_v1 = [
    # two chars
    ("原敬", {"family": "原", "given": "敬", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    # kana and kanji
    ("中山マサ", {"family": "中山", "given": "マサ", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    ("つるの剛士", {"family": "つるの", "given": "剛士", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    # three chars
    (
        "菅義偉",
        {"family": "菅", "given": "義偉", "separator": " ", "score": 0.6328842762252201, "algorithm": "kanji_feature"},
    ),
    # four chars
    (
        "阿部晋三",
        {"family": "阿部", "given": "晋三", "separator": " ", "score": 0.5745842309372197, "algorithm": "kanji_feature"},
    ),
    # five chars
    (
        "中曽根康弘",
        {"family": "中曽根", "given": "康弘", "separator": " ", "score": 0.3705325993396728, "algorithm": "kanji_feature"},
    ),
    # with no kanji in kanji.txt
    (
        "蝶院羊",
        {"family": "蝶", "given": "院羊", "separator": " ", "score": 0.5, "algorithm": "kanji_feature"},
    ),
]


name_test_data_v2 = [
    # two chars
    ("原敬", {"family": "原", "given": "敬", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    # kana and kanji
    ("中山マサ", {"family": "中山", "given": "マサ", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    ("つるの剛士", {"family": "つるの", "given": "剛士", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    # three chars
    (
        "菅義偉",
        {"family": "菅", "given": "義偉", "separator": " ", "score": 0.6328842762252201, "algorithm": "kanji_feature"},
    ),
    # four chars
    (
        "阿部晋三",
        {"family": "阿部", "given": "晋三", "separator": " ", "score": 0.5440120391041745, "algorithm": "kanji_feature"},
    ),
    # five chars
    (
        "中曽根康弘",
        {"family": "中曽根", "given": "康弘", "separator": " ", "score": 0.3705325993396728, "algorithm": "kanji_feature"},
    ),
    # with no kanji in kanji.txt
    (
        "蝶院羊",
        {"family": "蝶", "given": "院羊", "separator": " ", "score": 0.5, "algorithm": "kanji_feature"},
    ),
]


@pytest.mark.parametrize("undivided_name, expect", name_test_data_v1)
def test_divide_name_v1(undivided_name: str, expect: Dict):
    name_divider = BasicNameDivider.from_version(NameDividerVersions.BASIC_NAME_DIVIDER_V1)
    divided_name = name_divider.divide_name(undivided_name)
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


@pytest.mark.parametrize("undivided_name, expect", name_test_data_v2)
def test_divide_name_v2(undivided_name: str, expect: Dict):
    name_divider = BasicNameDivider.from_version(NameDividerVersions.BASIC_NAME_DIVIDER_V2)
    divided_name = name_divider.divide_name(undivided_name)
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


@pytest.mark.parametrize("undivided_name, expect", name_test_data_v2)
def test_divide_name_latest(undivided_name: str, expect: Dict):
    name_divider = BasicNameDivider.from_version(NameDividerVersions.BASIC_NAME_DIVIDER_LATEST)
    divided_name = name_divider.divide_name(undivided_name)
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]
