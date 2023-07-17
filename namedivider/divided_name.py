import warnings
from dataclasses import asdict, dataclass
from typing import Any, Dict


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

    warnings.warn(
        "namedivider.divided_name.DividedName is deprecated in 0.2 and will be removed in 0.4. "
        "Use namedivider.divider.divided_name.DividedName if you want to use DividedName class.",
        category=FutureWarning,
        stacklevel=1,
    )
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

    def to_dict(self) -> Dict[str, Any]:
        """
        :return: Dictionary of divided name
        :rtype: Dict
        """
        return asdict(self)
