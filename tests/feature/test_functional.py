import numpy as np
import pytest

from namedivider.feature.functional import _create_length_mask, _create_order_mask, MaskCache

test_data = [
    (2, 0, np.array([1, 0, 0, 0, 0, 0, 0, 0])),  # short name
    (5, 3, np.array([0, 0, 0, 1, 0, 1, 1, 1])),  # middle name
    (8, 1, np.array([0, 1, 1, 1, 0, 0, 0, 1])),  # long name
]


@pytest.mark.parametrize("full_name_length, char_idx, expect", test_data)
def test_create_length_mask(full_name_length: int, char_idx: int, expect: np.ndarray):
    mask = _create_length_mask(full_name_length=full_name_length, char_idx=char_idx)
    assert (mask == expect).all()


class TestMaskCache:
    def test_init_default_max_length(self):
        cache = MaskCache()
        assert cache.max_length == 10
        assert isinstance(cache.order_masks, dict)
        assert isinstance(cache.length_masks, dict)

    def test_init_custom_max_length(self):
        cache = MaskCache(max_length=5)
        assert cache.max_length == 5

    def test_initialize_cache_precomputes_masks(self):
        cache = MaskCache(max_length=4)
        # Should have masks for lengths 3-4, with char indices 1 to (length-2)
        assert (3, 1) in cache.order_masks
        assert (4, 1) in cache.order_masks
        assert (4, 2) in cache.order_masks
        assert (3, 1) in cache.length_masks
        assert (4, 1) in cache.length_masks
        assert (4, 2) in cache.length_masks

    def test_get_order_mask_from_cache(self):
        cache = MaskCache(max_length=4)
        mask = cache.get_order_mask(3, 1)
        expected = _create_order_mask(3, 1)
        np.testing.assert_array_equal(mask, expected)

    def test_get_order_mask_creates_if_not_cached(self):
        cache = MaskCache(max_length=3)
        # Request mask for length 5, idx 2 - not pre-cached
        mask = cache.get_order_mask(5, 2)
        expected = _create_order_mask(5, 2)
        np.testing.assert_array_equal(mask, expected)
        # Should now be cached
        assert (5, 2) in cache.order_masks

    def test_get_order_mask_invalid_first_char(self):
        cache = MaskCache()
        with pytest.raises(ValueError, match="First character and last character must not be created order mask"):
            cache.get_order_mask(3, 0)

    def test_get_order_mask_invalid_last_char(self):
        cache = MaskCache()
        with pytest.raises(ValueError, match="First character and last character must not be created order mask"):
            cache.get_order_mask(3, 2)

    def test_get_length_mask_from_cache(self):
        cache = MaskCache(max_length=4)
        mask = cache.get_length_mask(3, 1)
        expected = _create_length_mask(3, 1)
        np.testing.assert_array_equal(mask, expected)

    def test_get_length_mask_creates_if_not_cached(self):
        cache = MaskCache(max_length=3)
        # Request mask for length 6, idx 3 - not pre-cached
        mask = cache.get_length_mask(6, 3)
        expected = _create_length_mask(6, 3)
        np.testing.assert_array_equal(mask, expected)
        # Should now be cached
        assert (6, 3) in cache.length_masks

    def test_cache_consistency_order_mask(self):
        cache = MaskCache()
        # Get same mask multiple times - should return same object
        mask1 = cache.get_order_mask(4, 2)
        mask2 = cache.get_order_mask(4, 2)
        assert mask1 is mask2

    def test_cache_consistency_length_mask(self):
        cache = MaskCache()
        # Get same mask multiple times - should return same object
        mask1 = cache.get_length_mask(4, 2)
        mask2 = cache.get_length_mask(4, 2)
        assert mask1 is mask2

    def test_order_mask_correctness(self):
        cache = MaskCache()
        # Test specific cases to ensure correctness
        # Length 3, char index 1 (middle character)
        mask = cache.get_order_mask(3, 1)
        expected = np.array([0, 0, 1, 1, 0, 0])
        np.testing.assert_array_equal(mask, expected)
        
        # Length 4, char index 1 (second character)
        mask = cache.get_order_mask(4, 1)
        expected = np.array([0, 1, 1, 1, 0, 0])
        np.testing.assert_array_equal(mask, expected)

    def test_length_mask_correctness(self):
        cache = MaskCache()
        # Test with known values to ensure correctness
        mask = cache.get_length_mask(3, 1)
        expected = _create_length_mask(3, 1)
        np.testing.assert_array_equal(mask, expected)
