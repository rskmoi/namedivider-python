from typing import NamedTuple, Dict


class DividedName(NamedTuple):
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
    score: float = 1.
    algorithm: str = ""

    def __str__(self) -> str:
        """
        :return: Divided name separated by separator.
        :rtype: str
        """
        return f"{self.family}{self.separator}{self.given}"

    def to_dict(self) -> Dict:
        """
        :return: Dictionary of divided name
        :rtype: Dict
        """
        return {"family": self.family,
                "given": self.given,
                "separator": self.separator,
                "score": self.score,
                "algorithm": self.algorithm}
