from typing import Dict

import pytest

from namedivider.rule.specific_family_name_rule import SpecificFamilyNameRule

name_test_data = [
    ("谷田部太郎", {"family": "谷田部", "given": "太郎", "separator": "/", "score": 1.0, "algorithm": "rule_specific_family"}),
    ("谷田太郎", {"family": "谷田", "given": "太郎", "separator": "/", "score": 1.0, "algorithm": "rule_specific_family"}),
    ("谷太郎", {"family": "谷", "given": "太郎", "separator": "/", "score": 1.0, "algorithm": "rule_specific_family"}),
]


@pytest.mark.parametrize("undivided_name, expect", name_test_data)
def test_divide_if_match(undivided_name: str, expect: Dict):
    rule = SpecificFamilyNameRule(family_names=["谷", "谷田", "谷田部"])
    divided_name = rule.divide(undivided_name=undivided_name, separator="/")
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


def test_divide_if_not_match():
    rule = SpecificFamilyNameRule(family_names=["谷", "谷田", "谷田部"])
    divided_name = rule.divide(undivided_name="水谷太郎", separator="/")
    assert divided_name is None
