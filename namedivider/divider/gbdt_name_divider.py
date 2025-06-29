from dataclasses import asdict
from pathlib import Path
from typing import Optional, cast

from namedivider.divider.config import GBDTNameDividerConfig
from namedivider.divider.divided_name import DividedName
from namedivider.divider.name_divider_base import _NameDivider
from namedivider.divider.rust_backend import RustNameDividerWrapper
from namedivider.util import (
    download_family_name_pickle_if_needed,
    download_gbdt_model_v1_if_needed,
)


class GBDTNameDivider(_NameDivider):
    """
    NameDivider with gradient boosting decision tree.

    Supports both Python (default) and Rust (beta) backends.
    """

    def __init__(self, config: Optional[GBDTNameDividerConfig] = None):
        if config is None:
            config = GBDTNameDividerConfig()

        # Initialize based on backend selection
        if config.backend == "rust":
            self._init_rust_backend(config)
        else:
            # Default Python backend - preserve existing behavior
            self._init_python_backend(config)

        super().__init__(config=config)

    def _init_python_backend(self, config: GBDTNameDividerConfig) -> None:
        # Local imports to prevent C library conflicts between lightgbm
        # and Rust backend on macOS
        import pickle

        import lightgbm as lgb

        from namedivider.feature.extractor import FamilyRankingFeatureExtractor
        from namedivider.feature.family_name import FamilyNameRepository
        from namedivider.feature.kanji import KanjiStatisticsRepository

        """Initialize Python backend (default behavior)."""
        download_family_name_pickle_if_needed(config.path_family_names)
        download_gbdt_model_v1_if_needed(config.path_model)
        kanji_statistics_repository = KanjiStatisticsRepository(path_csv=config.path_csv)
        if Path(config.path_family_names).suffix == ".pickle":
            with open(config.path_family_names, "rb") as f:
                family_name_repository: FamilyNameRepository = pickle.load(f)
        else:
            family_name_repository = FamilyNameRepository(path_txt=config.path_family_names)
        self.feature_extractor = FamilyRankingFeatureExtractor(
            kanji_statistics_repository=kanji_statistics_repository,
            family_name_repository=family_name_repository,
            cache_mask=config.cache_mask,
        )
        self.model = lgb.Booster(model_file=config.path_model)
        self._rust_divider: Optional[RustNameDividerWrapper] = None

    def _init_rust_backend(self, config: GBDTNameDividerConfig) -> None:
        """Initialize Rust backend (beta feature)."""
        from namedivider.divider.rust_backend import create_rust_gbdt_divider

        self._rust_divider = create_rust_gbdt_divider(config)
        # Python-specific attributes are not set for Rust backend

    def calc_score(self, family: str, given: str) -> float:
        """
        Calculates the score. The higher the score, the more likely the division is correct.
        :param family: Family name.
        :param given: Given name.
        :return: Score of dividing.
        """
        # Use Rust backend if available
        if self._rust_divider is not None:
            return self._rust_divider.calc_score(family, given)

        # Use Python backend (default) - feature_extractor/model are guaranteed to be initialized
        feature = self.feature_extractor.get_features(family=family, given=given)
        feature_list = [list(asdict(feature).values())]
        score_list = self.model.predict(feature_list)
        score = cast(float, score_list[0])
        return score

    def divide_name(self, undivided_name: str) -> DividedName:
        """
        Divides undivided name.
        :param undivided_name: Names with no space between the family name and given name
        :return: Divided name
        :rtype: DividedName
        """
        # Use Rust backend if available
        if self._rust_divider is not None:
            return self._rust_divider.divide_name(undivided_name)

        # Use Python backend (default) - delegate to parent class
        return super().divide_name(undivided_name)
