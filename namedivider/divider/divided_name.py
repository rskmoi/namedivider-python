from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import cast

# After 3.7 reached EOL: from typing import TypedDict
from typing_extensions import TypedDict


class DividedNameDict(TypedDict):
    family: str
    given: str
    separator: str
    score: float
    algorithm: str


@dataclass(frozen=True)
class DividedName:
    """
    Divided name.
    :param family: Family name
    :param given: Given name
    :param separator: Character for separate family name and given name.
    :param score: Confidence level, from 0 to 1
    :param algorithm: The name of dividing algorithm
    """

    family: str
    given: str
    separator: str = " "
    score: float = 1.0
    algorithm: str = ""

    def __str__(self) -> str:
        """
        :return: Divided name separated by separator.
        :rtype: str
        """
        return f"{self.family}{self.separator}{self.given}"

    def to_dict(self) -> DividedNameDict:
        """
        :return: Dictionary of divided name
        :rtype: Dict
        """
        return cast(DividedNameDict, asdict(self))
