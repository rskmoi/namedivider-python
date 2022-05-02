import pandas as pd
import lightgbm as lgb
from dataclasses import asdict
from namedivider.divider.config import GBDTNameDividerConfig
from namedivider.divider.name_divider_base import _NameDivider
from namedivider.feature.kanji import KanjiStatisticsRepository
from namedivider.feature.family_name import FamilyNameRepository
from namedivider.feature.extractor import FamilyRankingFeatureExtractor


class GBDTNameDivider(_NameDivider):
    """
    NameDivider with gradient boosting decision tree.
    """

    def __init__(self, config: GBDTNameDividerConfig = None):
        if config is None:
            config = GBDTNameDividerConfig()
        super().__init__(config=config)
        kanji_statistics_repository = KanjiStatisticsRepository(path_csv=config.path_csv)
        family_name_repository = FamilyNameRepository(path_txt=config.path_family_names)
        self.feature_extractor = FamilyRankingFeatureExtractor(kanji_statistics_repository=kanji_statistics_repository,
                                                               family_name_repository=family_name_repository)
        self.model = lgb.Booster(model_file=config.path_model)

    def calc_score(self, family: str, given: str) -> float:
        """
        Calculates the score. The higher the score, the more likely the division is correct.
        :param family: Family name.
        :param given: Given name.
        :return: Score of dividing.
        """
        feature = self.feature_extractor.get_features(family=family, given=given)
        df = pd.DataFrame([asdict(feature)])
        score = self.model.predict(df)
        return score[0]
