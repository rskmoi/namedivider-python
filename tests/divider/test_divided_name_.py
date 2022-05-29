from namedivider.divider.divided_name import DividedName


def test_divided_name_str():
    divided_name = DividedName(family="菅", given="義偉", separator="/")
    assert str(divided_name) == "菅/義偉"


def test_divided_name_dict():
    divided_name = DividedName(family="菅", given="義偉", separator="/", score=0.5, algorithm="manual")
    divided_name_dict = divided_name.to_dict()
    assert divided_name_dict["family"] == "菅"
    assert divided_name_dict["given"] == "義偉"
    assert divided_name_dict["separator"] == "/"
    assert divided_name_dict["score"] == 0.5
    assert divided_name_dict["algorithm"] == "manual"
