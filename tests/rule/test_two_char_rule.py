from namedivider.rule.two_char_rule import TwoCharRule


def test_divide_if_match():
    rule = TwoCharRule()
    divided_name = rule.divide(undivided_name="原敬", separator="/")
    assert divided_name.family == "原"
    assert divided_name.given == "敬"
    assert divided_name.separator == "/"
    assert divided_name.score == 1.0
    assert divided_name.algorithm == "rule"


def test_divide_if_not_match():
    rule = TwoCharRule()
    divided_name = rule.divide(undivided_name="原太郎", separator="/")
    assert divided_name is None
