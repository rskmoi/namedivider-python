import abc
from typing import Optional

from namedivider.divider.divided_name import DividedName


class Rule(metaclass=abc.ABCMeta):
    """
    Base class for rule-based algorithms.
    """

    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def divide(self, undivided_name: str, separator: str = " ") -> Optional[DividedName]:
        pass
