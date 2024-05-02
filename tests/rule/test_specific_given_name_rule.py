from typing import Dict

import pytest

from namedivider.rule.specific_given_name_rule import SpecificGivenNameRule

name_test_data = [
    ("田中亜実南", {"family": "田中", "given": "亜実南", "separator": "/", "score": 1.0, "algorithm": "rule_specific_given"}),
    ("田中実南", {"family": "田中", "given": "実南", "separator": "/", "score": 1.0, "algorithm": "rule_specific_given"}),
    ("田中南", {"family": "田中", "given": "南", "separator": "/", "score": 1.0, "algorithm": "rule_specific_given"}),
]


@pytest.mark.parametrize("undivided_name, expect", name_test_data)
def test_divide_if_match(undivided_name: str, expect: Dict):
    rule = SpecificGivenNameRule(given_names=["亜実南", "実南", "南"])
    divided_name = rule.divide(undivided_name=undivided_name, separator="/")
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


def test_divide_if_not_match():
    rule = SpecificGivenNameRule(given_names=["亜実南", "実南", "南"])
    divided_name = rule.divide(undivided_name="田中亜実", separator="/")
    assert divided_name is None
