from typing import Iterable, Optional

from namedivider.divider.divided_name import DividedName
from namedivider.rule.rule import Rule


class SpecificGivenNameRule(Rule):
    """
    A rule for specific given names.
    """

    def __init__(self, given_names: Iterable[str]):
        """
        :param given_names: A list of given name.
        Names ends with given name in this given_names will always be split by this given_name.
        """
        self._given_names = set(given_names)

    def divide(self, undivided_name: str, separator: str = " ") -> Optional[DividedName]:
        """
        Divide undivided name.
        If the conditions are met simultaneously, the longer given name will be given priority.

        :param undivided_name: Names with no space between the family name and given name
        :param separator: Character for separate family name and given name

        :example
        -----------------------------------------------------
        >>> from namedivider.rule.specific_given_name_rule import SpecificGivenNameRule
        >>> # Initialize rule
        >>> rule = SpecificGivenNameRule(given_names=["亜実南", "実南", "南"])
        >>> rule.divide("田中亜実南")
        DividedName(family='田中', given='亜実南', separator=' ', score=1.0, algorithm='rule_specific_given')
        >>> rule.divide("田中実南")
        DividedName(family='田中', given='実南', separator=' ', score=1.0, algorithm='rule_specific_given')
        >>> rule.divide("田中亜実南")
        DividedName(family='田中', given='南', separator=' ', score=1.0, algorithm='rule_specific_given')
        >>> # This does not apply
        >>> rule.divide("田中亜実")
        None
        -----------------------------------------------------
        """
        for i in range(len(undivided_name)):
            given_candidate = undivided_name[i + 1 :]
            if given_candidate in self._given_names:
                return DividedName(
                    family=undivided_name[: i + 1],
                    given=undivided_name[i + 1 :],
                    separator=separator,
                    score=1.0,
                    algorithm="rule_specific_given",
                )

        return None
