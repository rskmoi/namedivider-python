"""
Test Rust backend integration for both BasicNameDivider and GBDTNameDivider
"""
from typing import Dict

import pytest

from namedivider.divider.basic_name_divider import BasicNameDivider
from namedivider.divider.gbdt_name_divider import GBDTNameDivider
from namedivider.divider.config import BasicNameDividerConfig, GBDTNameDividerConfig


# Test data for basic name divider comparison
basic_test_cases = [
    ("原敬", {"family": "原", "given": "敬"}),
    ("中山マサ", {"family": "中山", "given": "マサ"}),
    ("つるの剛士", {"family": "つるの", "given": "剛士"}),
    ("菅義偉", {"family": "菅", "given": "義偉"}),
    ("阿部晋三", {"family": "阿部", "given": "晋三"}),
    ("中曽根康弘", {"family": "中曽根", "given": "康弘"}),
    ("蝶院羊", {"family": "蝶", "given": "院羊"}),
]

# Test data for GBDT name divider comparison
gbdt_test_cases = [
    ("原敬", {"family": "原", "given": "敬"}),
    ("中山マサ", {"family": "中山", "given": "マサ"}),
    ("つるの剛士", {"family": "つるの", "given": "剛士"}),
    ("菅義偉", {"family": "菅", "given": "義偉"}),
    ("阿部晋三", {"family": "阿部", "given": "晋三"}),
    ("中曽根康弘", {"family": "中曽根", "given": "康弘"}),
    ("蝶院羊", {"family": "蝶院", "given": "羊"}),  # Note: Different from basic divider
]


class TestBasicNameDividerRustBackend:
    """Test BasicNameDivider Rust backend against Python backend"""
    
    @pytest.mark.parametrize("undivided_name, expect", basic_test_cases)
    def test_rust_python_parity(self, undivided_name: str, expect: Dict):
        """Test that Rust and Python backends produce identical results"""
        # Python backend
        python_config = BasicNameDividerConfig(backend="python")
        python_divider = BasicNameDivider(python_config)
        python_result = python_divider.divide_name(undivided_name)
        
        # Rust backend
        rust_config = BasicNameDividerConfig(backend="rust")
        rust_divider = BasicNameDivider(rust_config)
        rust_result = rust_divider.divide_name(undivided_name)
        
        # Compare results
        assert python_result.family == rust_result.family, f"Family mismatch for {undivided_name}"
        assert python_result.given == rust_result.given, f"Given mismatch for {undivided_name}"
        assert python_result.separator == rust_result.separator, f"Separator mismatch for {undivided_name}"
        
        # Expected values should match both backends
        assert rust_result.family == expect["family"]
        assert rust_result.given == expect["given"]
    
    def test_rust_backend_info(self):
        """Test that Rust backend reports correct backend info"""
        config = BasicNameDividerConfig(backend="rust")
        divider = BasicNameDivider(config)
        backend_info = divider.get_backend_info()
        
        assert backend_info["backend"] == "rust"
        assert "namedivider-rs" in backend_info["implementation"]
        assert "high_performance" in backend_info["features"]
    


class TestGBDTNameDividerRustBackend:
    """Test GBDTNameDivider Rust backend against Python backend"""
    
    @pytest.mark.parametrize("undivided_name, expect", gbdt_test_cases)
    def test_rust_python_parity(self, undivided_name: str, expect: Dict):
        """Test that Rust and Python backends produce identical results"""
        # Python backend
        python_config = GBDTNameDividerConfig(backend="python")
        python_divider = GBDTNameDivider(python_config)
        python_result = python_divider.divide_name(undivided_name)
        
        # Rust backend
        rust_config = GBDTNameDividerConfig(backend="rust")
        rust_divider = GBDTNameDivider(rust_config)
        rust_result = rust_divider.divide_name(undivided_name)
        
        # Compare results
        assert python_result.family == rust_result.family, f"Family mismatch for {undivided_name}"
        assert python_result.given == rust_result.given, f"Given mismatch for {undivided_name}"
        assert python_result.separator == rust_result.separator, f"Separator mismatch for {undivided_name}"
        
        # Expected values should match both backends
        assert rust_result.family == expect["family"]
        assert rust_result.given == expect["given"]
    
    def test_rust_backend_info(self):
        """Test that Rust backend reports correct backend info"""
        config = GBDTNameDividerConfig(backend="rust")
        divider = GBDTNameDivider(config)
        backend_info = divider.get_backend_info()
        
        assert backend_info["backend"] == "rust"
        assert "namedivider-rs" in backend_info["implementation"]
        assert "gbdt_division" in backend_info["features"]
        assert "high_performance" in backend_info["features"]
    


class TestRustBackendErrors:
    """Test error handling for Rust backends"""
    
    def test_rust_backend_availability(self):
        """Test that Rust backend is available"""
        try:
            config = BasicNameDividerConfig(backend="rust")
            divider = BasicNameDivider(config)
            result = divider.divide_name("田中太郎")
            assert result is not None
        except Exception as e:
            pytest.fail(f"Rust backend should be available: {e}")
    
    def test_invalid_backend_type(self):
        """Test handling of invalid backend type"""
        with pytest.raises((ValueError, TypeError)):
            config = BasicNameDividerConfig(backend="invalid")
            BasicNameDivider(config)