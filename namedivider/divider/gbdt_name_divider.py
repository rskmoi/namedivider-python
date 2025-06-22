import _pickle as pickle  # type: ignore
from dataclasses import asdict
from pathlib import Path
from typing import Optional, cast, List

import lightgbm as lgb

from namedivider.divider.config import GBDTNameDividerConfig
from namedivider.divider.divided_name import DividedName
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
    NameDivider with gradient boosting decision tree supporting multiple backends.
    Supports both Python and Rust backends for improved performance.
    """

    def __init__(self, config: Optional[GBDTNameDividerConfig] = None):
        if config is None:
            config = GBDTNameDividerConfig()
        
        self.config = config
        self._backend = None
        self._python_backend_initialized = False
        
        # Initialize appropriate backend
        if config.backend == "rust":
            self._initialize_rust_backend()
        else:
            self._initialize_python_backend()
        
        # Always call parent constructor for base functionality
        super().__init__(config=config)
    
    def _initialize_rust_backend(self) -> None:
        """Initialize Rust backend - fails with clear error if not available."""
        try:
            from namedivider.divider.rust_backend import RustGBDTNameDivider
            self._backend = RustGBDTNameDivider(self.config)
        except ImportError as e:
            raise RuntimeError(
                f"Rust backend requested but namedivider_core package is not installed or GBDT support is not available. "
                f"Please install the Rust backend package or use backend='python'. "
                f"Error: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Rust GBDT backend: {e}. "
                f"Please check your Rust backend installation or use backend='python'."
            ) from e
    
    def _initialize_python_backend(self) -> None:
        """Initialize Python backend (original implementation)."""
        if not self._python_backend_initialized:
            download_family_name_pickle_if_needed(self.config.path_family_names)
            download_gbdt_model_v1_if_needed(self.config.path_model)
            kanji_statistics_repository = KanjiStatisticsRepository(path_csv=self.config.path_csv)
            if Path(self.config.path_family_names).suffix == ".pickle":
                with open(self.config.path_family_names, "rb") as f:
                    family_name_repository: FamilyNameRepository = pickle.load(f)
            else:
                family_name_repository = FamilyNameRepository(path_txt=self.config.path_family_names)
            self.feature_extractor = FamilyRankingFeatureExtractor(
                kanji_statistics_repository=kanji_statistics_repository, family_name_repository=family_name_repository
            )
            self.model = lgb.Booster(model_file=self.config.path_model)
            self._python_backend_initialized = True

    def calc_score(self, family: str, given: str) -> float:
        """
        Calculates the score. The higher the score, the more likely the division is correct.
        :param family: Family name.
        :param given: Given name.
        :return: Score of dividing.
        """
        # Use Rust backend if available
        if self._backend is not None:
            return self._backend.calc_score(family, given)
        
        # Fallback to Python implementation
        feature = self.feature_extractor.get_features(family=family, given=given)
        feature_list = [list(asdict(feature).values())]
        score_list = self.model.predict(feature_list)
        score = cast(float, score_list[0])
        return score
    
    def divide_name(self, undivided_name: str) -> DividedName:
        """
        Divide a name using the configured backend.
        :param undivided_name: Undivided name to process
        :return: DividedName object with division result
        """
        # Use Rust backend if available
        if self._backend is not None:
            return self._backend.divide_name(undivided_name)
        
        # Fallback to Python implementation
        return super().divide_name(undivided_name)
    
    def get_backend_info(self) -> dict:
        """
        Get information about the current backend.
        :return: Backend metadata
        """
        if self._backend is not None:
            return self._backend.get_backend_info()
        else:
            return {
                "backend": "python",
                "implementation": "namedivider-python",
                "features": ["gbdt_division", "score_calculation"],
                "config": {
                    "separator": self.config.separator,
                    "normalize_name": self.config.normalize_name,
                    "algorithm_name": self.config.algorithm_name,
                }
            }
