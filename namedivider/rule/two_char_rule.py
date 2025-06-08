from typing import Optional

from namedivider.divider.divided_name import DividedName
from namedivider.rule.rule import Rule


class TwoCharRule(Rule):
    """
    A rule for 2-letter names.
    """

    def __init__(self) -> None:
        pass

    def divide(self, undivided_name: str, separator: str = " ") -> Optional[DividedName]:
        """
        :param undivided_name: Names with no space between the family name and given name
        :param separator: Character for separate family name and given name
        :return:
            if fits the rules: Divided name
            else: None
        :rtype:
            if fits the rules: DividedName
            else: None
        """

        # If the undivided name consists of 2 characters,
        # the first characters is family name, and the last characters is given name.
        if len(undivided_name) == 2:
            return DividedName(
                family=undivided_name[0], given=undivided_name[-1], separator=separator, score=1.0, algorithm="rule"
            )

        return None
