from namedivider import NameDivider
from controller.model import DivisionRequest
from controller import division_controller


def test_division_controller():
    divider = NameDivider()
    undivided_names = ["菅義偉"]
    division_request = DivisionRequest(names=undivided_names)
    res = division_controller.divide(divider=divider, division_request=division_request)
    assert res.divided_names[0].family == "菅"
    assert res.divided_names[0].given == "義偉"
    assert res.divided_names[0].separator == " "
    assert res.divided_names[0].score == 0.6328842762252201
    assert res.divided_names[0].algorithm == "kanji_feature"


if __name__ == '__main__':
    test_division_controller()