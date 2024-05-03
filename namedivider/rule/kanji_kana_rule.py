from typing import Optional

import regex

from namedivider.divider.divided_name import DividedName
from namedivider.rule.rule import Rule


class KanjiKanaRule(Rule):
    """
    A rule for names containing both kanji and kana(hiragana or katakana).
    """

    def __init__(self) -> None:
        self._compiled_regex_kanji = regex.compile(r"\p{Script=Han}+")

    def divide(self, undivided_name: str, separator: str = " ") -> Optional[DividedName]:
        """
        If the undivided name consists of kanji and other types of characters (hiragana, katakana, etc...),
        the undivided name will be divided where the kanji and other character types are switched.
        For example, "河村たかし" is divided into "河村" for the family name, and "たかし" for the given name.
        This is because "河" and "村" are kanji, while "た", "か" and "し" are hiragana.

        :param undivided_name: Names with no space between the family name and given name
        :param separator: Character for separate family name and given name
        :return:
            if fits the rules: Divided name
            else: None
        :rtype:
            if fits the rules: DividedName
            else: None
        """

        # The criterion for determining switched is whether "two" consecutive characters are having
        # different type of characters from first character type.
        # The reason of "two" is some family names consist of some kanji and one katakana.
        # (ex: "井ノ原", "三ツ又",　"関ヶ原" contains "ノ", "ツ", "ヶ". They are all katakana.)
        is_kanji_list = []
        for i, _char in enumerate(undivided_name):
            is_kanji = True if self._compiled_regex_kanji.fullmatch(_char) else False
            is_kanji_list.append(is_kanji)
            if i >= 2:
                if is_kanji_list[0] != is_kanji and is_kanji_list[-2] == is_kanji:
                    return DividedName(
                        family=undivided_name[: i - 1],
                        given=undivided_name[i - 1 :],
                        separator=separator,
                        score=1.0,
                        algorithm="rule",
                    )

        # If there is only one kanji within the name, and the last character of the name is a kanji,
        # then that last character is considered the given name. (ex: ながつま昭)
        if sum(is_kanji_list) == 1 and is_kanji_list[-1] is True:
            return DividedName(
                family=undivided_name[:-1],
                given=undivided_name[-1:],
                separator=separator,
                score=1.0,
                algorithm="rule",
            )

        return None
