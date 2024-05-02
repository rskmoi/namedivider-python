from typing import Dict

import pytest

from namedivider.rule.kanji_kana_rule import KanjiKanaRule

name_test_data = [
    ("中山マサ", {"family": "中山", "given": "マサ", "separator": "/", "score": 1.0, "algorithm": "rule"}),
    ("つるの剛士", {"family": "つるの", "given": "剛士", "separator": "/", "score": 1.0, "algorithm": "rule"}),
    ("ながつま昭", {"family": "ながつま", "given": "昭", "separator": "/", "score": 1.0, "algorithm": "rule"}),
]


@pytest.mark.parametrize("undivided_name, expect", name_test_data)
def test_divide_if_match(undivided_name: str, expect: Dict):
    rule = KanjiKanaRule()
    divided_name = rule.divide(undivided_name=undivided_name, separator="/")
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


def test_divide_if_not_match():
    rule = KanjiKanaRule()
    divided_name = rule.divide(undivided_name="井ノ原快彦", separator="/")
    assert divided_name is None
