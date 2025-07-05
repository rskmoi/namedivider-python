from typing import Optional

from namedivider.divider.config import BasicNameDividerConfig
from namedivider.divider.divided_name import DividedName
from namedivider.divider.name_divider_base import _NameDivider
from namedivider.divider.rust_backend import RustNameDividerWrapper
from namedivider.feature.extractor import SimpleFeatureExtractor
from namedivider.feature.kanji import KanjiStatisticsRepository


class BasicNameDivider(_NameDivider):
    """
    NameDivider with basic algorithm.
    Prior to v0.1.0, this was provided as a 'NameDivider' class.

    Supports both Python (default) and Rust (beta) backends.
    """

    def __init__(self, config: Optional[BasicNameDividerConfig] = None):
        if config is None:
            config = BasicNameDividerConfig()

        # Initialize based on backend selection
        if config.backend == "rust":
            self._init_rust_backend(config)
        else:
            # Default Python backend - preserve existing behavior
            self._init_python_backend(config)

        super().__init__(config=config)

    def _init_python_backend(self, config: BasicNameDividerConfig) -> None:
        """Initialize Python backend (default behavior)."""
        repository = KanjiStatisticsRepository(path_csv=config.path_csv)
        self.only_order_score_when_4 = config.only_order_score_when_4
        self.feature_extractor = SimpleFeatureExtractor(
            kanji_statistics_repository=repository, cache_mask=config.cache_mask
        )
        self._rust_divider: Optional[RustNameDividerWrapper] = None

    def _init_rust_backend(self, config: BasicNameDividerConfig) -> None:
        """Initialize Rust backend (beta feature)."""
        from namedivider.divider.rust_backend import create_rust_basic_divider

        self._rust_divider = create_rust_basic_divider(config)
        self.only_order_score_when_4 = config.only_order_score_when_4
        # Python-specific feature_extractor is not set for Rust backend

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

        # Use Python backend (default) - feature_extractor is guaranteed to be initialized
        name = family + given
        features = self.feature_extractor.get_features(family=family, given=given)
        order_score = (features.family_order_score + features.given_order_score) / (len(name) - 2)
        if self.only_order_score_when_4 and len(family + given) == 4:
            return order_score
        length_score = (features.family_length_score + features.given_length_score) / len(name)

        return (order_score + length_score) / 2.0

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
