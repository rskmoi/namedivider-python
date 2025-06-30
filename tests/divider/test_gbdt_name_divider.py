from typing import Dict

import pytest

from namedivider.divider.config import NameDividerVersions
from namedivider.divider.gbdt_name_divider import GBDTNameDivider

name_test_data_v1 = [
    # two chars
    ("原敬", {"family": "原", "given": "敬", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    # kana and kanji
    ("中山マサ", {"family": "中山", "given": "マサ", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    ("つるの剛士", {"family": "つるの", "given": "剛士", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    # three chars
    ("菅義偉", {"family": "菅", "given": "義偉", "separator": " ", "score": 0.7300634880343344, "algorithm": "gbdt"}),
    # four chars
    ("阿部晋三", {"family": "阿部", "given": "晋三", "separator": " ", "score": 0.5761118242092244, "algorithm": "gbdt"}),
    # five chars
    ("中曽根康弘", {"family": "中曽根", "given": "康弘", "separator": " ", "score": 0.47535339308928076, "algorithm": "gbdt"}),
    # with no kanji in kanji.txt
    ("蝶院羊", {"family": "蝶院", "given": "羊", "separator": " ", "score": 0.5013754025624984, "algorithm": "gbdt"}),
]


@pytest.mark.parametrize("undivided_name, expect", name_test_data_v1)
def test_divide_name_v1(undivided_name: str, expect: Dict):
    name_divider = GBDTNameDivider.from_version(NameDividerVersions.GBDT_NAME_DIVIDER_V1)
    divided_name = name_divider.divide_name(undivided_name)
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


@pytest.mark.parametrize("undivided_name, expect", name_test_data_v1)
def test_divide_name_latest(undivided_name: str, expect: Dict):
    name_divider = GBDTNameDivider.from_version(NameDividerVersions.GBDT_NAME_DIVIDER_LATEST)
    divided_name = name_divider.divide_name(undivided_name)
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]
