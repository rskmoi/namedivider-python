from typing import Optional

from namedivider.divider.config import BasicNameDividerConfig
from namedivider.divider.name_divider_base import _NameDivider
from namedivider.feature.extractor import SimpleFeatureExtractor
from namedivider.feature.kanji import KanjiStatisticsRepository


class BasicNameDivider(_NameDivider):
    """
    NameDivider with basic algorithm.
    Prior to v0.1.0, this was provided as a 'NameDivider' class.
    """

    def __init__(self, config: Optional[BasicNameDividerConfig] = None):
        if config is None:
            config = BasicNameDividerConfig()
        super().__init__(config=config)
        repository = KanjiStatisticsRepository(path_csv=config.path_csv)
        self.only_order_score_when_4 = config.only_order_score_when_4
        self.feature_extractor = SimpleFeatureExtractor(kanji_statistics_repository=repository)

    def calc_score(self, family: str, given: str) -> float:
        """
        Calculates the score. The higher the score, the more likely the division is correct.
        :param family: Family name.
        :param given: Given name.
        :return: Score of dividing.
        """
        name = family + given
        features = self.feature_extractor.get_features(family=family, given=given)
        order_score = (features.family_order_score + features.given_order_score) / (len(name) - 2)
        if self.only_order_score_when_4 and len(family + given) == 4:
            return order_score
        length_score = (features.family_length_score + features.given_length_score) / len(name)

        return (order_score + length_score) / 2.0
