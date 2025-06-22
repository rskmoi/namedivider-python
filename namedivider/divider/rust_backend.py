"""
Rust backend adapter layer for namedivider.

This module provides adapter classes that bridge the Python configuration system
with the Rust implementation, enabling seamless backend switching.
"""

import warnings
from typing import Optional, List

from namedivider.divider.config import BasicNameDividerConfig, GBDTNameDividerConfig
from namedivider.divider.divided_name import DividedName


class RustBackendError(Exception):
    """Exception raised when Rust backend encounters errors."""
    pass


class RustBasicNameDivider:
    """
    Adapter class for Rust BasicNameDivider implementation.
    
    This class bridges the Python configuration system with the Rust implementation,
    providing the same interface as the Python BasicNameDivider while using
    the high-performance Rust backend.
    """
    
    def __init__(self, config: BasicNameDividerConfig):
        """
        Initialize Rust BasicNameDivider with Python configuration.
        
        Args:
            config: BasicNameDividerConfig with backend="rust"
        
        Raises:
            RustBackendError: If Rust backend initialization fails
        """
        self.config = config
        self._rust_divider = None
        self._initialize_rust_backend()
    
    def _initialize_rust_backend(self) -> None:
        """Initialize the Rust backend with configuration parameters."""
        try:
            # Import the Rust namedivider package (installed as namedivider_core)
            import namedivider_core as rust_namedivider
            
            # Create the Rust divider
            self._rust_divider = rust_namedivider.BasicNameDivider()
            
            # Store config for reference
            self._config_warnings = []
            if self.config.separator != " ":
                self._config_warnings.append(f"Custom separator '{self.config.separator}' not supported by Rust backend (using default ' ')")
            if not self.config.normalize_name:
                self._config_warnings.append("normalize_name=False not supported by Rust backend (using default True)")
            if self.config.only_order_score_when_4:
                self._config_warnings.append("only_order_score_when_4=True not supported by Rust backend (using default False)")
            
            # Warn about unsupported configurations
            if self._config_warnings:
                for warning in self._config_warnings:
                    warnings.warn(warning, UserWarning)
            
        except ImportError as e:
            raise RustBackendError(
                f"Rust namedivider library not found. Please install namedivider_core package. "
                f"Error: {e}"
            ) from e
        except Exception as e:
            raise RustBackendError(
                f"Failed to initialize Rust BasicNameDivider: {e}"
            ) from e
    
    def divide_name(self, undivided_name: str) -> DividedName:
        """
        Divide a name using the Rust backend.
        
        Args:
            undivided_name: The undivided name to process
            
        Returns:
            DividedName: The divided name result
            
        Raises:
            RustBackendError: If division fails
        """
        if not self._rust_divider:
            raise RustBackendError("Rust backend not initialized")
        
        try:
            # Call Rust divider
            rust_result = self._rust_divider.divide_name(undivided_name)
            
            # Convert Rust DividedName to Python DividedName
            return DividedName(
                family=rust_result.family,
                given=rust_result.given,
                separator=rust_result.separator,
                score=rust_result.score,
                algorithm=rust_result.algorithm
            )
            
        except Exception as e:
            raise RustBackendError(f"Rust name division failed: {e}") from e
    
    def calc_score(self, family: str, given: str) -> float:
        """
        Calculate division score using the Rust backend.
        
        Args:
            family: Family name
            given: Given name
            
        Returns:
            float: Division confidence score
            
        Raises:
            RustBackendError: If score calculation fails
        """
        if not self._rust_divider:
            raise RustBackendError("Rust backend not initialized")
        
        try:
            return self._rust_divider.calc_score(family, given)
        except Exception as e:
            raise RustBackendError(f"Rust score calculation failed: {e}") from e
    
    def get_backend_info(self) -> dict:
        """
        Get information about the current backend.
        
        Returns:
            dict: Backend metadata
        """
        return {
            "backend": "rust",
            "implementation": "namedivider-rs",
            "features": ["basic_division", "score_calculation", "high_performance"],
            "config": {
                "separator": self.config.separator,
                "normalize_name": self.config.normalize_name,
                "only_order_score_when_4": self.config.only_order_score_when_4,
            }
        }


class RustGBDTNameDivider:
    """
    Adapter class for Rust GBDTNameDivider implementation.
    
    This class bridges the Python configuration system with the Rust GBDT implementation,
    providing the same interface as the Python GBDTNameDivider while using
    the high-performance Rust backend.
    """
    
    def __init__(self, config: GBDTNameDividerConfig):
        """
        Initialize Rust GBDTNameDivider with Python configuration.
        
        Args:
            config: GBDTNameDividerConfig with backend="rust"
        
        Raises:
            RustBackendError: If Rust backend initialization fails
        """
        self.config = config
        self._rust_divider = None
        self._initialize_rust_backend()
    
    def _initialize_rust_backend(self) -> None:
        """Initialize the Rust GBDT backend with configuration parameters."""
        try:
            # Import the Rust namedivider package (installed as namedivider_rust)
            import namedivider_rust as rust_namedivider
            
            # Check if GBDT support is available in Rust backend
            if not hasattr(rust_namedivider, 'GBDTNameDivider'):
                raise RustBackendError(
                    "GBDT support not available in the installed Rust backend. "
                    "Please ensure you have the latest version with GBDT support installed."
                )
            
            # Create the Rust GBDT divider
            # For now, we'll use the basic constructor - in production this would
            # accept configuration parameters for model paths, etc.
            self._rust_divider = rust_namedivider.GBDTNameDivider()
            
            # Store config warnings for unsupported parameters
            self._config_warnings = []
            if self.config.separator != " ":
                self._config_warnings.append(f"Custom separator '{self.config.separator}' not supported by Rust GBDT backend (using default ' ')")
            if not self.config.normalize_name:
                self._config_warnings.append("normalize_name=False not supported by Rust GBDT backend (using default True)")
            
            # Warn about unsupported configurations
            if self._config_warnings:
                for warning in self._config_warnings:
                    warnings.warn(warning, UserWarning)
            
        except ImportError as e:
            raise RustBackendError(
                f"Rust namedivider library not found. Please install namedivider_core package with GBDT support. "
                f"Error: {e}"
            ) from e
        except Exception as e:
            raise RustBackendError(
                f"Failed to initialize Rust GBDTNameDivider: {e}"
            ) from e
    
    def divide_name(self, undivided_name: str) -> DividedName:
        """
        Divide a name using the Rust GBDT backend.
        
        Args:
            undivided_name: The undivided name to process
            
        Returns:
            DividedName: The divided name result
            
        Raises:
            RustBackendError: If division fails
        """
        if not self._rust_divider:
            raise RustBackendError("Rust GBDT backend not initialized")
        
        try:
            # Call Rust GBDT divider
            rust_result = self._rust_divider.divide_name(undivided_name)
            
            # Convert Rust DividedName to Python DividedName
            return DividedName(
                family=rust_result.family,
                given=rust_result.given,
                separator=rust_result.separator,
                score=rust_result.score,
                algorithm=rust_result.algorithm
            )
            
        except Exception as e:
            raise RustBackendError(f"Rust GBDT name division failed: {e}") from e
    
    def calc_score(self, family: str, given: str) -> float:
        """
        Calculate division score using the Rust GBDT backend.
        
        Args:
            family: Family name
            given: Given name
            
        Returns:
            float: Division confidence score
            
        Raises:
            RustBackendError: If score calculation fails
        """
        if not self._rust_divider:
            raise RustBackendError("Rust GBDT backend not initialized")
        
        try:
            return self._rust_divider.calc_score(family, given)
        except Exception as e:
            raise RustBackendError(f"Rust GBDT score calculation failed: {e}") from e
    
    def get_backend_info(self) -> dict:
        """
        Get information about the current backend.
        
        Returns:
            dict: Backend metadata
        """
        return {
            "backend": "rust",
            "implementation": "namedivider-rs",
            "features": ["gbdt_division", "score_calculation", "high_performance"],
            "config": {
                "separator": self.config.separator,
                "normalize_name": self.config.normalize_name,
                "algorithm_name": self.config.algorithm_name,
                "path_model": str(self.config.path_model),
                "path_family_names": str(self.config.path_family_names),
                "path_csv": str(self.config.path_csv),
            }
        }


