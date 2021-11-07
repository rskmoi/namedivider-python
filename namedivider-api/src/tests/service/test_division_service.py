from namedivider import NameDivider
from service import division_service


def test_division_servise():
    divider = NameDivider()
    divided_names = division_service.divide(divider=divider, undivided_names=["菅義偉"])
    assert divided_names[0].family == "菅"
    assert divided_names[0].given == "義偉"
    assert divided_names[0].separator == " "
    assert divided_names[0].score == 0.6328842762252201
    assert divided_names[0].algorithm == "kanji_feature"