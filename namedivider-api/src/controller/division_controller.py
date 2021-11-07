from namedivider import NameDivider
from controller.model import DivisionRequest, DivisionResult, ViewDividedName
from service import division_service


def divide(divider: NameDivider, division_request: DivisionRequest) -> DivisionResult:
    divided_names_raw = division_service.divide(divider=divider,
                                                undivided_names=division_request.names)
    divided_names = [ViewDividedName(**_raw.to_dict()) for _raw in divided_names_raw]
    return DivisionResult(divided_names=divided_names)