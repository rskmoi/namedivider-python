from pathlib import Path

from namedivider.feature.extractor import (
    FamilyRankingFeatureExtractor,
    FamilyRankingFeatures,
    SimpleFeatureExtractor,
    SimpleFeatures,
)
from namedivider.feature.family_name import FamilyNameRepository
from namedivider.feature.kanji import KanjiStatisticsRepository

CURRENT_DIR = Path(__file__).resolve().parent


def test_simple_feature_extractor():
    kanji_statistics_repository = KanjiStatisticsRepository(
        path_csv=CURRENT_DIR / ".." / "assets" / "kanji_for_test.csv"
    )
    extractor = SimpleFeatureExtractor(kanji_statistics_repository=kanji_statistics_repository)
    features = extractor.get_features(family="中曽根", given="康弘")
    assert isinstance(features, SimpleFeatures)
    assert features.family_order_score == 1.2952503209242618
    assert features.family_length_score == 1.2075945519196942
    assert features.given_order_score == 1.0
    assert features.given_length_score == 1.9410276679841898


def test_family_name_repository_get_rank_exists():
    kanji_statistics_repository = KanjiStatisticsRepository(
        path_csv=CURRENT_DIR / ".." / "assets" / "kanji_for_test.csv"
    )
    family_name_repository = FamilyNameRepository(path_txt=CURRENT_DIR / ".." / "assets" / "family_name_for_test.txt")
    extractor = FamilyRankingFeatureExtractor(
        kanji_statistics_repository=kanji_statistics_repository, family_name_repository=family_name_repository
    )
    features = extractor.get_features(family="中曽根", given="康弘")
    assert isinstance(features, FamilyRankingFeatures)
    assert features.rank == 3
    assert features.fullname_length == 5
    assert features.family_length == 3
    assert features.given_length == 2
    assert features.family_order_score == 1.2952503209242618
    assert features.family_length_score == 1.2075945519196942
    assert features.given_order_score == 1.0
    assert features.given_length_score == 1.9410276679841898
    assert not features.given_startswith_specific_kanji
