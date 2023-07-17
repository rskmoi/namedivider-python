import numpy as np
import numpy.typing as npt

from namedivider.feature.kanji import KanjiStatisticsRepository


def _create_order_mask(full_name_length: int, char_idx: int) -> npt.NDArray[np.int32]:
    """
    Create order mask.
    Order mask is one-hot mask for calculate order score.
    :param full_name_length: Length of full name.
    :param char_idx: The order of the character in full name
    :return: Order mask
    :rtype: np.ndarray
    """
    if char_idx == 0 or char_idx == full_name_length - 1:
        raise ValueError("First character and last character must not be created order mask.")

    if full_name_length == 3:
        return np.array([0, 0, 1, 1, 0, 0])

    if char_idx == 1:
        return np.array([0, 1, 1, 1, 0, 0])

    if char_idx == full_name_length - 2:
        return np.array([0, 0, 1, 1, 1, 0])

    return np.array([0, 1, 1, 1, 1, 0])


def _create_length_mask(full_name_length: int, char_idx: int) -> npt.NDArray[np.int32]:
    """
    Create length mask.
    Length mask is one-hot mask for calculate length score.
    :param full_name_length: Length of full name.
    :param char_idx: The order of the character in full name
    :return: Length mask
    :rtype: np.ndarray
    """
    min_family = char_idx + 1
    min_family_idx = 4 if min_family > 4 else min_family
    max_family = full_name_length - 1
    max_family_idx = 4 if max_family > 4 else max_family
    min_given = full_name_length - char_idx
    min_given_idx = 4 if min_given > 4 else min_given
    max_given = full_name_length - 1
    max_given_idx = 4 if max_given > 4 else max_given
    lc_family = np.array([0, 0, 0, 0])
    if min_family <= max_family:
        lc_family[min_family_idx - 1 : max_family_idx] = 1
    lc_given = np.array([0, 0, 0, 0])
    if min_given <= max_given:
        lc_given[min_given_idx - 1 : max_given_idx] = 1
    return np.concatenate([lc_family, lc_given])


def _calc_current_order_status(piece_of_divided_name: str, idx_in_piece_of_divided_name: int, is_family: bool) -> int:
    """
    Determine which index of order_counts the kanji corresponds to.
    :param piece_of_divided_name: Family name or given name
    :param idx_in_piece_of_divided_name: Index in family or given name
    :param is_family: True if piece_of_divided_name is family name
    :return: The index of order_counts
    :rtype: int
    """
    if idx_in_piece_of_divided_name == 0:
        return 0 if is_family else 3
    if idx_in_piece_of_divided_name == len(piece_of_divided_name) - 1:
        return 2 if is_family else 5
    else:
        return 1 if is_family else 4


def _calc_current_length_status(piece_of_divided_name: str, is_family: bool) -> int:
    """
    Determine which index of length_counts the kanji corresponds to.
    :param piece_of_divided_name: Family name or given name
    :param is_family: True if piece_of_divided_name is family name
    :return: The index of length_counts
    :rtype: int
    """
    piece_of_divided_name_length = len(piece_of_divided_name) if len(piece_of_divided_name) <= 4 else 4
    return piece_of_divided_name_length - 1 if is_family else piece_of_divided_name_length - 1 + 4


def calc_order_score(
    kanji_statistics_repository: KanjiStatisticsRepository,
    piece_of_divided_name: str,
    full_name_length: int,
    start_index: int = 0,
) -> float:
    """
    Calculates order score.
    Order score is a feature, which is a kind of frequency, calculated from where each kanji in full name is used.
    See this link if you need more explanation: https://rskmoi.hatenablog.com/entry/2017/01/15/190837
    :param kanji_statistics_repository: Class for managing Kanji statistics.
    :param piece_of_divided_name: Family name or given name
    :param full_name_length: Length of fullname
    :param start_index: The order of the first charactar of piece_of_divided_name in full name
    :return: Order score
    :rtype: float

    example:
    -----------------------------------------------------
    >>> import namedivider.feature.functional as F
    >>> # Full name: 新海誠
    >>> F.calc_order_score(piece_of_divided_name='新海', full_name_length=3, start_index=0)
    0.8305084745762712
    >>> F.calc_order_score(piece_of_divided_name='誠', full_name_length=3, start_index=2)
    0
    >>> # Full name: 清武弘嗣
    >>> F.calc_order_score(piece_of_divided_name='清武', full_name_length=4, start_index=0)
    0.2222222222222222
    >>> F.calc_order_score(piece_of_divided_name='弘嗣', full_name_length=4, start_index=2)
    0.9919571045576407
    -----------------------------------------------------
    """
    is_family = True if start_index == 0 else False
    scores = 0
    for idx_in_piece_of_divided_name, _kanji in enumerate(piece_of_divided_name):
        current_idx = start_index + idx_in_piece_of_divided_name
        if current_idx == 0:
            continue
        if current_idx == full_name_length - 1:
            continue
        mask = _create_order_mask(full_name_length, current_idx)
        current_order_status_idx = _calc_current_order_status(
            piece_of_divided_name, idx_in_piece_of_divided_name, is_family
        )
        masked_order = kanji_statistics_repository.get(_kanji).order_counts * mask
        if np.sum(masked_order) == 0:
            continue
        cur_score = masked_order[current_order_status_idx] / np.sum(masked_order)
        scores += cur_score
    return scores


def calc_length_score(
    kanji_statistics_repository: KanjiStatisticsRepository,
    piece_of_divided_name: str,
    full_name_length: int,
    start_index: int = 0,
) -> float:
    """
    Calculates length score.
    Length score is a feature, which is a kind of frequency,
    calculated from how long is family/given name containing the kanji.
    See this link if you need more explanation: https://rskmoi.hatenablog.com/entry/2017/01/15/190837
    :param kanji_statistics_repository: Class for managing Kanji statistics.
    :param piece_of_divided_name: Family name or given name
    :param full_name_length: Length of fullname
    :param start_index: The order of the first charactar of piece_of_divided_name in full name
    :return: Length score
    :rtype: float

    example:
    -----------------------------------------------------
    >>> import namedivider.feature.functional as F
    >>> # Full name: 新海誠
    >>> F.calc_length_score(piece_of_divided_name='新海', full_name_length=3, start_index=0)
    1.6721919841662545
    >>> F.calc_length_score(piece_of_divided_name='誠', full_name_length=3, start_index=2)
    0.5414201183431953
    >>> # Full name: 清武弘嗣
    >>> F.calc_length_score(piece_of_divided_name='清武', full_name_length=4, start_index=0)
    1.9431977559607292
    >>> F.calc_length_score(piece_of_divided_name='弘嗣', full_name_length=4, start_index=2)
    1.982873228774868
    -----------------------------------------------------
    """
    is_family = True if start_index == 0 else False
    scores = 0
    for i, _kanji in enumerate(piece_of_divided_name):
        current_idx = start_index + i
        mask = _create_length_mask(full_name_length, current_idx)
        current_length_status_idx = _calc_current_length_status(piece_of_divided_name, is_family)
        masked_length_scores = kanji_statistics_repository.get(_kanji).length_counts * mask
        if np.sum(masked_length_scores) == 0:
            continue
        cur_score = masked_length_scores[current_length_status_idx] / np.sum(masked_length_scores)
        scores += cur_score
    return scores
