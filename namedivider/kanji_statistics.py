import warnings
from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass(frozen=True)
class KanjiStatistics:
    """
    Statistics for a single kanji.
    :param kanji: A kanji.
    :param order_counts:
        Statistics of where the kanji is used in full name.
        order_counts is an array with six components.
        We use the following two perspectives to obtain statistical information from many names.
        - The kanji is in the family name or in the given name?
        - The order in which the kanji appear in the family/given name is first, last or other?

        So six components means as:
            [family_first, family_other, family_last, given_first, given_other, given_last]

        example:
        Let's take the famous Japanese scientist "北里柴三郎" ("北里" is family name, "柴三郎" is given name) as an example.
        "北" in "北里柴三郎" is in family name, and first character of family name.
        "里" in "北里柴三郎" is in family name, and last character of family name.
        "柴" in "北里柴三郎" is in given name, and first character of given name.
        "三" in "北里柴三郎" is in given name, and is not first nor last character, so this is other.
        "郎" in "北里柴三郎" is in given name, and last character of given name.

        If the statistics are taken from only him, then each order_counts would look like this:
            "北": [1, 0, 0, 0, 0, 0]
            "里": [0, 0, 1, 0, 0, 0]
            "柴": [0, 0, 0, 1, 0, 0]
            "三": [0, 0, 0, 0, 1, 0]
            "郎": [0, 0, 0, 0, 0, 1]

        If the statistics are taken from only him and "柴田錬三郎", then each order_counts would look like this:
            "北": [1, 0, 0, 0, 0, 0]
            "里": [0, 0, 1, 0, 0, 0]
            "柴": [1, 0, 0, 1, 0, 0]
            "三": [0, 0, 0, 0, 2, 0]
            "郎": [0, 0, 0, 0, 0, 2]
            "田": [0, 0, 1, 0, 0, 0]
            "錬": [0, 0, 0, 1, 0, 0]

    :param length_counts:
        Statistics of how long is the family/given name containing the kanji.
        length_counts is an array with eight components.
        We use the following two perspectives to obtain statistical information from many names.
        - The kanji is in the family name or in the given name?
        - The length of family/given name containing the kanji is 1, 2, 3, or over 4?

        So eight components means as:
            [family_1, family_2, family_3, family_over_4, given_1, given_2, given_3, given_4]

        example:
        Let's take the famous Japanese scientist "北里柴三郎" ("北里" is family name, "柴三郎" is given name) as an example.
        "北" in "北里柴三郎" is in family name, and "北里" consists of 2 characters.
        "里" in "北里柴三郎" is in family name, and "北里" consists of 2 characters.
        "柴" in "北里柴三郎" is in given name, and "柴三郎" consists of 3 characters.
        "三" in "北里柴三郎" is in given name, and "柴三郎" consists of 3 characters.
        "郎" in "北里柴三郎" is in given name, and "柴三郎" consists of 3 characters.

        If the statistics are taken from only him, then each order_counts would look like this:
            "北": [0, 1, 0, 0, 0, 0, 0, 0]
            "里": [0, 1, 0, 0, 0, 0, 0, 0]
            "柴": [0, 0, 0, 0, 0, 0, 1, 0]
            "三": [0, 0, 0, 0, 0, 0, 1, 0]
            "郎": [0, 0, 0, 0, 0, 0, 1, 0]

        If the statistics are taken from only him and "柴田錬三郎", then each order_counts would look like this:
            "北": [0, 1, 0, 0, 0, 0, 0, 0]
            "里": [0, 1, 0, 0, 0, 0, 0, 0]
            "柴": [0, 1, 0, 0, 0, 0, 1, 0]
            "三": [0, 0, 0, 0, 0, 0, 2, 0]
            "郎": [0, 0, 0, 0, 0, 0, 2, 0]
            "田": [0, 1, 0, 0, 0, 0, 0, 0]
            "錬": [0, 0, 0, 0, 0, 0, 1, 0]
    """

    warnings.warn(
        "namedivider.kanji_statistics.KanjiStatistics is deprecated in 0.2 and will be removed in 0.4. "
        "Use namedivider.feature.kanji.KanjiStatistics if you want to use KanjiStatistics class.",
        category=FutureWarning,
        stacklevel=1,
    )
    kanji: str
    order_counts: npt.NDArray[np.int32]
    length_counts: npt.NDArray[np.int32]

    @classmethod
    def default(cls) -> "KanjiStatistics":
        """
        Returns default kanji.
        :return: Default kanji
        :rtype: KanjiStatistics
        """
        return cls(
            kanji="default", order_counts=np.array([0, 0, 0, 0, 0, 0]), length_counts=np.array([0, 0, 0, 0, 0, 0, 0, 0])
        )
