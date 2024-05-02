import regex

from namedivider.beta_bert_divider.bert_name_divider_only_katakana import (
    BERTNameDividerOnlyKatakana,
)
from namedivider.divider.divided_name import DividedName
from namedivider.divider.name_divider_base import _NameDivider


class CombinedNameDivider:
    def __init__(self, base_divider: _NameDivider, katakana_divider: BERTNameDividerOnlyKatakana) -> None:
        self.base_divider = base_divider
        self.katakana_divider = katakana_divider
        self.compiled_regex_katakana = regex.compile("[\u30A1-\u30FF]+")

    def divide_name(self, undivided_name: str) -> DividedName:
        if len(undivided_name) < 15 and self.compiled_regex_katakana.fullmatch(undivided_name):
            return self.katakana_divider.divide_name(undivided_name)
        return self.base_divider.divide_name(undivided_name)
