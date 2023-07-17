import numpy as np
import pytest

from namedivider.feature.functional import _create_length_mask

test_data = [
    (2, 0, np.array([1, 0, 0, 0, 0, 0, 0, 0])),  # short name
    (5, 3, np.array([0, 0, 0, 1, 0, 1, 1, 1])),  # middle name
    (8, 1, np.array([0, 1, 1, 1, 0, 0, 0, 1])),  # long name
]


@pytest.mark.parametrize("full_name_length, char_idx, expect", test_data)
def test_create_length_mask(full_name_length: int, char_idx: int, expect: np.ndarray):
    mask = _create_length_mask(full_name_length=full_name_length, char_idx=char_idx)
    assert (mask == expect).all()
