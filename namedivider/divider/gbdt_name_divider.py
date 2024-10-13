import _pickle as pickle  # type: ignore
from dataclasses import asdict
from pathlib import Path
from typing import Optional, cast

import lightgbm as lgb

from namedivider.divider.config import GBDTNameDividerConfig
from namedivider.divider.name_divider_base import _NameDivider
from namedivider.feature.extractor import FamilyRankingFeatureExtractor
from namedivider.feature.family_name import FamilyNameRepository
from namedivider.feature.kanji import KanjiStatisticsRepository
from namedivider.util import (
    download_family_name_pickle_if_needed,
    download_gbdt_model_v1_if_needed,
)


class GBDTNameDivider(_NameDivider):
    """
    NameDivider with gradient boosting decision tree.
    """

    def __init__(self, config: Optional[GBDTNameDividerConfig] = None):
        if config is None:
            config = GBDTNameDividerConfig()
        super().__init__(config=config)
        download_family_name_pickle_if_needed(config.path_family_names)
        download_gbdt_model_v1_if_needed(config.path_model)
        kanji_statistics_repository = KanjiStatisticsRepository(path_csv=config.path_csv)
        if Path(config.path_family_names).suffix == ".pickle":
            with open(config.path_family_names, "rb") as f:
                family_name_repository: FamilyNameRepository = pickle.load(f)
        else:
            family_name_repository = FamilyNameRepository(path_txt=config.path_family_names)
        self.feature_extractor = FamilyRankingFeatureExtractor(
            kanji_statistics_repository=kanji_statistics_repository, family_name_repository=family_name_repository
        )
        self.model = lgb.Booster(model_file=config.path_model)

    def calc_score(self, family: str, given: str) -> float:
        """
        Calculates the score. The higher the score, the more likely the division is correct.
        :param family: Family name.
        :param given: Given name.
        :return: Score of dividing.
        """
        feature = self.feature_extractor.get_features(family=family, given=given)
        feature_list = [list(asdict(feature).values())]
        score_list = self.model.predict(feature_list)
        score = cast(float, score_list[0])
        return score
