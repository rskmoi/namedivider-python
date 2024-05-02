from typing import Iterable, Optional

from namedivider.divider.divided_name import DividedName
from namedivider.rule.rule import Rule


class SpecificFamilyNameRule(Rule):
    """
    A rule for specific family names.
    """

    def __init__(self, family_names: Iterable[str]):
        """
        :param family_names: A list of family name.
        Names starts with family name in this family_names will always be split by this family_name.
        """
        self._family_names = set(family_names)

    def divide(self, undivided_name: str, separator: str = " ") -> Optional[DividedName]:
        """
        Divide undivided name.
        If the conditions are met simultaneously, the longer family name will be given priority.

        :param undivided_name: Names with no space between the family name and given name
        :param separator: Character for separate family name and given name

        :example
        -----------------------------------------------------
        >>> from namedivider.rule.specific_family_name_rule import SpecificFamilyNameRule
        >>> # Initialize rule
        >>> rule = SpecificFamilyNameRule(family_names=["谷", "谷田", "谷田部"])
        >>> rule.divide("谷田部太郎")
        DividedName(family='谷田部', given='太郎', separator=' ', score=1.0, algorithm='rule_specific_family')
        >>> rule.divide("谷田太郎")
        DividedName(family='谷田', given='太郎', separator=' ', score=1.0, algorithm='rule_specific_family')
        >>> rule.divide("谷太郎")
        DividedName(family='谷', given='太郎', separator=' ', score=1.0, algorithm='rule_specific_family')
        >>> # This does not apply
        >>> rule.divide("水谷太郎")
        None
        -----------------------------------------------------
        """
        for i in range(len(undivided_name)):
            family_candidate = undivided_name[:-i]
            if family_candidate in self._family_names:
                return DividedName(
                    family=undivided_name[:-i],
                    given=undivided_name[-i:],
                    separator=separator,
                    score=1.0,
                    algorithm="rule_specific_family",
                )

        return None
