from typing import List, Optional

from namedivider.divider.divided_name import DividedName
from namedivider.rule.kanji_kana_rule import KanjiKanaRule
from namedivider.rule.rule import Rule
from namedivider.rule.two_char_rule import TwoCharRule


class Pipeline:
    """
    Pipeline class that connects rule-based algorithms and executes them.
    """

    def __init__(self, separator: str, custom_rules: Optional[List[Rule]] = None) -> None:
        """
        :param separator: Character for separate family name and given name
        :param custom_rules: Optional rules for divide names
        """
        self._separator = separator
        # TwoCharRule and KanjiKanaRule will always be applied.
        self._rules: List[Rule] = [TwoCharRule(), KanjiKanaRule()]
        if custom_rules is not None:
            self._rules += custom_rules

    def apply(self, undivided_name: str) -> Optional[DividedName]:
        """
        Apply rule-based algorithms until a condition is met.
        Return the result if the condition is met; otherwise, return None if no condition is met until the end.

        :param undivided_name: Names with no space between the family name and given name

        :return:
            if fits the rules: Divided name
            else: None
        :rtype:
            if fits the rules: DividedName
            else: None
        """
        for _rule in self._rules:
            divided_name = _rule.divide(undivided_name, self._separator)
            if divided_name is not None:
                return divided_name

        return None
