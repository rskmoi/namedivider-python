from pathlib import Path

import numpy as np

from namedivider.feature.kanji import KanjiStatistics, KanjiStatisticsRepository

CURRENT_DIR = Path(__file__).resolve().parent


def test_kanji_statistics_default():
    kanji_statistics_default = KanjiStatistics.default()
    assert kanji_statistics_default.kanji == "default"
    np.testing.assert_equal(kanji_statistics_default.order_counts, np.array([0, 0, 0, 0, 0, 0]))
    np.testing.assert_equal(kanji_statistics_default.length_counts, np.array([0, 0, 0, 0, 0, 0, 0, 0]))


def test_get_exists():
    repo = KanjiStatisticsRepository(path_csv=CURRENT_DIR / ".." / "assets" / "kanji_for_test.csv")
    kanji_statistics = repo.get("菅")
    assert kanji_statistics.kanji == "菅"
    np.testing.assert_equal(kanji_statistics.order_counts, np.array([151, 0, 6, 0, 0, 0]))
    np.testing.assert_equal(kanji_statistics.length_counts, np.array([22, 134, 1, 0, 0, 0, 0, 0]))


def test_get_not_exists():
    repo = KanjiStatisticsRepository(path_csv=CURRENT_DIR / ".." / "assets" / "kanji_for_test.csv")
    kanji_statistics = repo.get("岸")
    assert kanji_statistics.kanji == "default"
    np.testing.assert_equal(kanji_statistics.order_counts, np.array([0, 0, 0, 0, 0, 0]))
    np.testing.assert_equal(kanji_statistics.length_counts, np.array([0, 0, 0, 0, 0, 0, 0, 0]))
