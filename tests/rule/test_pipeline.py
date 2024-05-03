from typing import Optional

from namedivider.divider.divided_name import DividedName
from namedivider.rule.pipeline import Pipeline
from namedivider.rule.rule import Rule


def test_apply_default():
    pipeline = Pipeline(separator="&")
    divided_name = pipeline.apply("中山マサ")
    assert divided_name.family == "中山"
    assert divided_name.given == "マサ"
    assert divided_name.separator == "&"
    assert divided_name.score == 1.0
    assert divided_name.algorithm == "rule"


def test_apply_with_custom_rules():
    class AlreadyExistsSeparatorRule(Rule):
        def __init__(self):
            pass

        def divide(self, undivided_name: str, separator: str = " ") -> Optional[DividedName]:
            if separator in undivided_name:
                divided_name_str = undivided_name.split(separator)
                return DividedName(
                    family=divided_name_str[0],
                    given=divided_name_str[-1],
                    separator=separator,
                    score=1.0,
                    algorithm="rule_already_divided",
                )

    pipeline = Pipeline(separator=" ", custom_rules=[AlreadyExistsSeparatorRule()])
    divided_name = pipeline.apply("菅 義偉")
    assert divided_name.family == "菅"
    assert divided_name.given == "義偉"
    assert divided_name.separator == " "
    assert divided_name.score == 1.0
    assert divided_name.algorithm == "rule_already_divided"


def test_apply_if_not_match():
    pipeline = Pipeline(separator="&")
    divided_name = pipeline.apply("菅義偉")
    assert divided_name is None
