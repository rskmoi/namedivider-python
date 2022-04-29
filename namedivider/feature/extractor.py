from pathlib import Path
from typing import Union
from dataclasses import dataclass
import namedivider.feature.functional as F
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


class SimpleFeatureExtractor:
    """
    Feature extractor.Calculate the order score and the length score for each of family and given name.
    These four features are the foundation of NameDivider.
    """
    def __init__(self, kanji_statistics_repository: KanjiStatisticsRepository):
        self.repository = kanji_statistics_repository

    def get_features(self, family: str, given: str) -> SimpleFeatures:
        """
        Calculates features.
        :param family: family name.
        :param given: given name.
        :return: Features calculated by input name.
        :rtype: SimpleFeature
        """
        fullname_length = len(family + given)
        family_order_score = F.calc_order_score(self.repository, family, fullname_length, 0)
        family_length_score = F.calc_length_score(self.repository, family, fullname_length, 0)
        given_order_score = F.calc_order_score(self.repository, given, fullname_length, len(family))
        given_length_score = F.calc_length_score(self.repository, given, fullname_length, len(family))
        return SimpleFeatures(family_order_score=family_order_score,
                              family_length_score=family_length_score,
                              given_order_score=given_order_score,
                              given_length_score=given_length_score)