from typing import Dict, Tuple

import numpy as np
import numpy.typing as npt


class MaskCache:
    """
    Cache for order and length masks to improve performance.
    """

    def __init__(self, max_length: int = 10):
        """
        Initialize the mask cache.
        :param max_length: Maximum name length to pre-compute masks for.
        """
        self.order_masks: Dict[Tuple[int, int], npt.NDArray[np.int32]] = {}
        self.length_masks: Dict[Tuple[int, int], npt.NDArray[np.int32]] = {}
        self.max_length = max_length
        self._initialize_cache()

    def _initialize_cache(self) -> None:
        """
        Pre-compute masks for common name lengths.
        """
        for length in range(3, self.max_length + 1):
            for idx in range(1, length - 1):
                self.order_masks[(length, idx)] = self._create_order_mask(length, idx)
                self.length_masks[(length, idx)] = self._create_length_mask(length, idx)

    def get_order_mask(self, full_name_length: int, char_idx: int) -> npt.NDArray[np.int32]:
        """
        Get order mask from cache or create it if not cached.
        :param full_name_length: Length of full name.
        :param char_idx: The order of the character in full name.
        :return: Order mask.
        """
        if char_idx == 0 or char_idx == full_name_length - 1:
            raise ValueError("First character and last character must not be created order mask.")

        key = (full_name_length, char_idx)
        if key not in self.order_masks:
            self.order_masks[key] = self._create_order_mask(full_name_length, char_idx)
        return self.order_masks[key]

    def get_length_mask(self, full_name_length: int, char_idx: int) -> npt.NDArray[np.int32]:
        """
        Get length mask from cache or create it if not cached.
        :param full_name_length: Length of full name.
        :param char_idx: The order of the character in full name.
        :return: Length mask.
        """
        key = (full_name_length, char_idx)
        if key not in self.length_masks:
            self.length_masks[key] = self._create_length_mask(full_name_length, char_idx)
        return self.length_masks[key]

    @staticmethod
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

    @staticmethod
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
