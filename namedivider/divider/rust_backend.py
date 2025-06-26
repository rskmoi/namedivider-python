"""
Rust backend support for namedivider.

This module provides optional Rust backend functionality for improved performance.
The Rust backend is a beta feature and requires the namedivider-core package.
"""
from pathlib import Path
from typing import Any, Optional, Union

from namedivider.divider.config import (
    BasicNameDividerConfig,
    GBDTNameDividerConfig,
    NameDividerConfigBase,
)
from namedivider.divider.divided_name import DividedName


class RustNameDividerWrapper:
    """
    Universal wrapper for Rust namedivider backends that returns Python DividedName objects.

    This wrapper works with both BasicNameDivider and GBDTNameDivider from the Rust backend,
    providing a consistent Python interface.
    """

    def __init__(self, rust_divider: Any):
        self._rust_divider = rust_divider

    def divide_name(self, undivided_name: str) -> DividedName:
        """
        Divides undivided name using Rust backend.

        Args:
            undivided_name: Names with no space between the family name and given name

        Returns:
            Python DividedName object
        """
        rust_result = self._rust_divider.divide_name(undivided_name)
        return DividedName(
            family=rust_result.family,
            given=rust_result.given,
            separator=rust_result.separator,
            score=rust_result.score,
            algorithm=rust_result.algorithm,
        )

    def calc_score(self, family: str, given: str) -> float:
        """
        Calculates the score using Rust backend.

        Args:
            family: Family name
            given: Given name

        Returns:
            Score of dividing
        """
        return float(self._rust_divider.calc_score(family, given))


class RustBackendNotAvailableError(ImportError):
    """
    Raised when rust backend is requested but namedivider_core is not available.

    This error is raised when:
    1. backend="rust" is specified in configuration
    2. namedivider_core package is not installed or not importable

    To fix this error:
    - Install namedivider_core: pip install namedivider-core
    - Or use backend="python" (default)
    """

    def __init__(self, message: Optional[str] = None):
        if message is None:
            message = (
                "Rust backend is not available. "
                "Please install 'namedivider-core' package to use the rust backend, "
                "or use backend='python' (default) instead."
            )
        super().__init__(message)


class RustBackendUnsupportedConfigError(ValueError):
    """
    Raised when unsupported configuration is specified for Rust backend.

    This error is raised when configuration options that are not supported
    by the Rust backend are specified with backend="rust".

    To fix this error:
    - Use backend="python" to access these features
    - Or remove the unsupported configuration options
    """


def _is_non_default_path(provided_path: Union[str, Path], default_path: Union[str, Path]) -> bool:
    """
    Check if provided path differs from default path.

    Args:
        provided_path: Path provided by user
        default_path: Default path for the configuration

    Returns:
        True if paths differ, False if they are the same
    """
    return str(Path(provided_path).resolve()) != str(Path(default_path).resolve())


def validate_rust_basic_config(config: NameDividerConfigBase) -> None:
    """
    Validate BasicNameDivider configuration for Rust backend.

    Args:
        config: Configuration object (must be BasicNameDividerConfig)

    Raises:
        TypeError: If config is not BasicNameDividerConfig
        RustBackendUnsupportedConfigError: If unsupported configuration is specified
    """
    if not isinstance(config, BasicNameDividerConfig):
        raise TypeError(f"Expected BasicNameDividerConfig, got {type(config).__name__}")

    from namedivider.divider.config import KANJI_CSV_DEFAULT_PATH

    errors = []

    if config.custom_rules is not None:
        errors.append("custom_rules")

    if config.cache_mask is True:
        errors.append("cache_mask=True")

    if _is_non_default_path(config.path_csv, KANJI_CSV_DEFAULT_PATH):
        errors.append("custom path_csv")

    if errors:
        raise RustBackendUnsupportedConfigError(
            f"Unsupported configuration for Rust backend: {', '.join(errors)}. "
            "Use backend='python' to access these features."
        )


def validate_rust_gbdt_config(config: NameDividerConfigBase) -> None:
    """
    Validate GBDTNameDivider configuration for Rust backend.

    Args:
        config: Configuration object (must be GBDTNameDividerConfig)

    Raises:
        TypeError: If config is not GBDTNameDividerConfig
        RustBackendUnsupportedConfigError: If unsupported configuration is specified
    """
    if not isinstance(config, GBDTNameDividerConfig):
        raise TypeError(f"Expected GBDTNameDividerConfig, got {type(config).__name__}")

    from namedivider.divider.config import (
        FAMILY_NAME_PKL_DEFAULT_PATH,
        GBDT_MODEL_V1_DEFAULT_PATH,
        KANJI_CSV_DEFAULT_PATH,
    )

    errors = []

    if config.custom_rules is not None:
        errors.append("custom_rules")

    if config.cache_mask is True:
        errors.append("cache_mask=True")

    if _is_non_default_path(config.path_csv, KANJI_CSV_DEFAULT_PATH):
        errors.append("custom path_csv")

    if _is_non_default_path(config.path_family_names, FAMILY_NAME_PKL_DEFAULT_PATH):
        errors.append("custom path_family_names")

    if _is_non_default_path(config.path_model, GBDT_MODEL_V1_DEFAULT_PATH):
        errors.append("custom path_model")

    if errors:
        raise RustBackendUnsupportedConfigError(
            f"Unsupported configuration for Rust backend: {', '.join(errors)}. "
            "Use backend='python' to access these features."
        )


def _try_import_rust_backend() -> Any:
    """
    Attempt to import namedivider_core package.

    Returns:
        namedivider_core module if available

    Raises:
        RustBackendNotAvailableError: If namedivider_core is not available
    """
    try:
        import namedivider_core  # type: ignore[import-untyped]

        return namedivider_core
    except ImportError as e:
        raise RustBackendNotAvailableError() from e


def create_rust_basic_divider(config: NameDividerConfigBase) -> RustNameDividerWrapper:
    """
    Create a Rust-based BasicNameDivider wrapper instance.

    Args:
        config: Configuration object

    Returns:
        RustNameDividerWrapper instance

    Raises:
        RustBackendNotAvailableError: If namedivider_core is not available
        RustBackendUnsupportedConfigError: If unsupported configuration is specified
    """
    # Validate configuration before creating divider
    validate_rust_basic_config(config)

    namedivider_core = _try_import_rust_backend()

    # Create Rust BasicNameDivider with config parameters
    rust_divider = namedivider_core.BasicNameDivider(
        separator=config.separator,
        normalize_name=config.normalize_name,
        only_order_score_when_4=getattr(config, "only_order_score_when_4", False),
    )

    return RustNameDividerWrapper(rust_divider)


def create_rust_gbdt_divider(config: NameDividerConfigBase) -> RustNameDividerWrapper:
    """
    Create a Rust-based GBDTNameDivider wrapper instance.

    Args:
        config: Configuration object

    Returns:
        RustNameDividerWrapper instance

    Raises:
        RustBackendNotAvailableError: If namedivider_core is not available
        RustBackendUnsupportedConfigError: If unsupported configuration is specified
    """
    # Validate configuration before creating divider
    validate_rust_gbdt_config(config)

    namedivider_core = _try_import_rust_backend()

    # Create Rust GBDTNameDivider with config parameters
    rust_divider = namedivider_core.GBDTNameDivider(separator=config.separator, normalize_name=config.normalize_name)

    return RustNameDividerWrapper(rust_divider)
