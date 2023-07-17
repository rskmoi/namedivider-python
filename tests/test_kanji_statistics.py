import numpy as np

from namedivider.kanji_statistics import KanjiStatistics


def test_kanji_statistics_default():
    kanji_statistics_default = KanjiStatistics.default()
    assert kanji_statistics_default.kanji == "default"
    np.testing.assert_equal(kanji_statistics_default.order_counts, np.array([0, 0, 0, 0, 0, 0]))
    np.testing.assert_equal(kanji_statistics_default.length_counts, np.array([0, 0, 0, 0, 0, 0, 0, 0]))
