from controller.model import DivisionRequest


def test_validate_division_request_valid() -> None:
    DivisionRequest(names=["菅義偉"])


def test_validate_division_request_invalid_name_length() -> bool:
    try:
        DivisionRequest(names=["安"])
    except ValueError:
        return True
    return False


def test_validate_division_request_invalid_name_volume() -> bool:
    names = []
    for i in range(1001):
        names.append("菅義偉")
    try:
        DivisionRequest(names=names)
    except ValueError:
        return True
    return False
