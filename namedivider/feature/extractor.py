from dataclasses import dataclass

import namedivider.feature.functional as F
from namedivider.feature.family_name import FamilyNameRepository
from namedivider.feature.functional import MaskCache
from namedivider.feature.kanji import KanjiStatisticsRepository


@dataclass(frozen=True)
class SimpleFeatures:
    """
    Features for SimpleFeatureExtractor.
    """

    family_order_score: float
    family_length_score: float
    given_order_score: float
    given_length_score: float


@dataclass(frozen=True)
class FamilyRankingFeatures:
    rank: float
    fullname_length: int
    family_length: int
    given_length: int
    family_order_score: float
    given_order_score: float
    family_length_score: float
    given_length_score: float
    given_startswith_specific_kanji: bool


class SimpleFeatureExtractor:
    """
    Feature extractor.Calculate the order score and the length score for each of family and given name.
    These four features are the foundation of NameDivider.
    """

    def __init__(self, kanji_statistics_repository: KanjiStatisticsRepository, cache_mask: bool = False):
        self.kanji_statistics_repository = kanji_statistics_repository
        self.mask_cache = MaskCache() if cache_mask else None

    def get_features(self, family: str, given: str) -> SimpleFeatures:
        """
        Calculates features.
        :param family: family name.
        :param given: given name.
        :return: Features calculated by input name.
        :rtype: SimpleFeature
        """
        fullname_length = len(family + given)
        family_order_score = F.calc_order_score(
            self.kanji_statistics_repository, family, fullname_length, 0, self.mask_cache
        )
        family_length_score = F.calc_length_score(
            self.kanji_statistics_repository, family, fullname_length, 0, self.mask_cache
        )
        given_order_score = F.calc_order_score(
            self.kanji_statistics_repository, given, fullname_length, len(family), self.mask_cache
        )
        given_length_score = F.calc_length_score(
            self.kanji_statistics_repository, given, fullname_length, len(family), self.mask_cache
        )
        return SimpleFeatures(
            family_order_score=family_order_score,
            family_length_score=family_length_score,
            given_order_score=given_order_score,
            given_length_score=given_length_score,
        )


class FamilyRankingFeatureExtractor:
    """
    Feature extractor.Calculate the order score and the length score for each of family and given name.
    """

    def __init__(
        self,
        kanji_statistics_repository: KanjiStatisticsRepository,
        family_name_repository: FamilyNameRepository,
        cache_mask: bool = False,
    ):
        self.kanji_statistics_repository = kanji_statistics_repository
        self.family_name_repository = family_name_repository
        self.mask_cache = MaskCache() if cache_mask else None

    def get_features(self, family: str, given: str) -> FamilyRankingFeatures:
        """
        Calculates features.
        :param family: family name.
        :param given: given name.
        :return: Features calculated by input name.
        :rtype: FamilyRankingFeatures
        """
        rank = self.family_name_repository.get_rank(family)
        fullname_length = len(family + given)
        family_length = len(family)
        given_length = len(given)
        family_order_score = F.calc_order_score(
            self.kanji_statistics_repository, family, fullname_length, 0, self.mask_cache
        )
        family_length_score = F.calc_length_score(
            self.kanji_statistics_repository, family, fullname_length, 0, self.mask_cache
        )
        given_order_score = F.calc_order_score(
            self.kanji_statistics_repository, given, fullname_length, len(family), self.mask_cache
        )
        given_length_score = F.calc_length_score(
            self.kanji_statistics_repository, given, fullname_length, len(family), self.mask_cache
        )
        # Selected 10 Kanji chars, especially those that rarely come at the beginning of a given name.
        given_startswith_specific_kanji = given.startswith(("田", "谷", "川", "島", "原", "村", "塚", "森", "井", "子"))
        return FamilyRankingFeatures(
            rank=rank,
            fullname_length=fullname_length,
            family_length=family_length,
            given_length=given_length,
            family_order_score=family_order_score,
            given_order_score=given_order_score,
            family_length_score=family_length_score,
            given_length_score=given_length_score,
            given_startswith_specific_kanji=given_startswith_specific_kanji,
        )
