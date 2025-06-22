from typing import Optional, List

from namedivider.divider.config import BasicNameDividerConfig
from namedivider.divider.divided_name import DividedName
from namedivider.divider.name_divider_base import _NameDivider
from namedivider.feature.extractor import SimpleFeatureExtractor
from namedivider.feature.kanji import KanjiStatisticsRepository


class BasicNameDivider(_NameDivider):
    """
    NameDivider with basic algorithm supporting multiple backends.
    Prior to v0.1.0, this was provided as a 'NameDivider' class.
    
    Supports both Python and Rust backends for improved performance.
    """

    def __init__(self, config: Optional[BasicNameDividerConfig] = None):
        if config is None:
            config = BasicNameDividerConfig()
        
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
            from namedivider.divider.rust_backend import RustBasicNameDivider
            self._backend = RustBasicNameDivider(self.config)
        except ImportError as e:
            raise RuntimeError(
                f"Rust backend requested but namedivider_core package is not installed. "
                f"Please install the Rust backend package or use backend='python'. "
                f"Error: {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Rust backend: {e}. "
                f"Please check your Rust backend installation or use backend='python'."
            ) from e
    
    def _initialize_python_backend(self) -> None:
        """Initialize Python backend (original implementation)."""
        if not self._python_backend_initialized:
            repository = KanjiStatisticsRepository(path_csv=self.config.path_csv)
            self.only_order_score_when_4 = self.config.only_order_score_when_4
            self.feature_extractor = SimpleFeatureExtractor(kanji_statistics_repository=repository)
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
        name = family + given
        features = self.feature_extractor.get_features(family=family, given=given)
        order_score = (features.family_order_score + features.given_order_score) / (len(name) - 2)
        if self.only_order_score_when_4 and len(family + given) == 4:
            return order_score
        length_score = (features.family_length_score + features.given_length_score) / len(name)

        return (order_score + length_score) / 2.0
    
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
                "features": ["basic_division", "score_calculation"],
                "config": {
                    "separator": self.config.separator,
                    "normalize_name": self.config.normalize_name,
                    "only_order_score_when_4": self.config.only_order_score_when_4,
                }
            }
