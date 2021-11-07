from namedivider import NameDivider, DividedName
from typing import List


def divide(divider: NameDivider, undivided_names: List[str]) -> List[DividedName]:
    divided_names = []
    for _name in undivided_names:
        divided_names.append(divider.divide_name(_name))
    return divided_names
