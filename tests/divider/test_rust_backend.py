import pytest

from namedivider.divider.basic_name_divider import BasicNameDivider
from namedivider.divider.config import BasicNameDividerConfig, GBDTNameDividerConfig
from namedivider.divider.divided_name import DividedName
from namedivider.divider.gbdt_name_divider import GBDTNameDivider
from namedivider.divider.rust_backend import (
    RustBackendNotAvailableError,
    RustBackendUnsupportedConfigError,
    RustNameDividerWrapper,
    create_rust_basic_divider,
    create_rust_gbdt_divider,
    validate_rust_basic_config,
    validate_rust_gbdt_config,
)
from namedivider.rule.two_char_rule import TwoCharRule

# Test data for consistency checks
backend_consistency_test_data = [
    "菅義偉",
    "田中太郎",
    "佐藤花子",
    "鈴木一郎",
    "中曽根康弘",
    "阿部晋三",
]

calc_score_test_data = [
    ("菅", "義偉"),
    ("田中", "太郎"),
    ("佐藤", "花子"),
]

# Expected results from Python implementations for Rust backend validation
basic_expected_results = [
    (
        "菅義偉",
        {"family": "菅", "given": "義偉", "separator": " ", "score": 0.6328842762252201, "algorithm": "kanji_feature"},
    ),
    (
        "阿部晋三",
        {"family": "阿部", "given": "晋三", "separator": " ", "score": 0.5440120391041745, "algorithm": "kanji_feature"},
    ),
    (
        "中曽根康弘",
        {"family": "中曽根", "given": "康弘", "separator": " ", "score": 0.3705325993396728, "algorithm": "kanji_feature"},
    ),
]

gbdt_expected_results = [
    ("菅義偉", {"family": "菅", "given": "義偉", "separator": " ", "score": 0.7300634880343344, "algorithm": "gbdt"}),
    ("阿部晋三", {"family": "阿部", "given": "晋三", "separator": " ", "score": 0.5761118242092244, "algorithm": "gbdt"}),
    ("中曽根康弘", {"family": "中曽根", "given": "康弘", "separator": " ", "score": 0.47535339308928076, "algorithm": "gbdt"}),
]


class TestRustBackend:
    """Test Rust backend functionality."""

    def test_rust_backend_not_available_error(self):
        """Test RustBackendNotAvailableError message and inheritance."""
        error = RustBackendNotAvailableError()
        assert "Rust backend is not available" in str(error)
        assert "namedivider-core" in str(error)
        assert isinstance(error, ImportError)

        # Test custom message
        custom_error = RustBackendNotAvailableError("Custom message")
        assert str(custom_error) == "Custom message"

    def test_create_rust_basic_divider(self):
        """Test create_rust_basic_divider factory function."""
        config = BasicNameDividerConfig(backend="rust")
        wrapper = create_rust_basic_divider(config)
        assert isinstance(wrapper, RustNameDividerWrapper)

    def test_create_rust_gbdt_divider(self):
        """Test create_rust_gbdt_divider factory function."""
        config = GBDTNameDividerConfig(backend="rust")
        wrapper = create_rust_gbdt_divider(config)
        assert isinstance(wrapper, RustNameDividerWrapper)

    def test_rust_name_divider_wrapper(self):
        """Test RustNameDividerWrapper functionality."""
        config = BasicNameDividerConfig(backend="rust")
        wrapper = create_rust_basic_divider(config)

        # Test divide_name
        result = wrapper.divide_name("菅義偉")
        assert isinstance(result, DividedName)
        assert hasattr(result, "family")
        assert hasattr(result, "given")
        assert hasattr(result, "separator")
        assert hasattr(result, "score")
        assert hasattr(result, "algorithm")

        # Test calc_score
        score = wrapper.calc_score("菅", "義偉")
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestBackendConsistency:
    """Test consistency between Python and Rust backends."""

    @pytest.mark.parametrize("undivided_name, expected", basic_expected_results)
    def test_basic_name_divider_rust_backend(self, undivided_name: str, expected: dict):
        """Test that Rust Basic backend produces expected results (avoiding Python/Rust conflicts)."""
        rust_divider = BasicNameDivider(BasicNameDividerConfig(backend="rust"))
        rust_result = rust_divider.divide_name(undivided_name)

        # Check family and given names match expected results
        assert rust_result.family == expected["family"], f"Family name mismatch for {undivided_name}"
        assert rust_result.given == expected["given"], f"Given name mismatch for {undivided_name}"
        assert rust_result.separator == expected["separator"], f"Separator mismatch for {undivided_name}"

        # Scores should be very close (allowing for minor floating point differences)
        score_diff = abs(rust_result.score - expected["score"])
        assert (
            score_diff < 0.1
        ), f"Score difference too large for {undivided_name}: expected {expected['score']}, got {rust_result.score}"

    @pytest.mark.parametrize("undivided_name, expected", gbdt_expected_results)
    def test_gbdt_name_divider_rust_backend(self, undivided_name: str, expected: dict):
        """Test Rust GBDT backend via subprocess with base64 encoding for Windows compatibility."""
        import subprocess
        import sys
        import json
        import base64

        # base64 encode for japanese chars
        encoded_name = base64.b64encode(undivided_name.encode('utf-8')).decode('ascii')
        code = f"import namedivider, json, base64; from namedivider.divider.gbdt_name_divider import GBDTNameDivider; from namedivider.divider.config import GBDTNameDividerConfig; name = base64.b64decode('{encoded_name}').decode('utf-8'); divider = GBDTNameDivider(GBDTNameDividerConfig(backend='rust')); result = divider.divide_name(name); output = {{'family': result.family, 'given': result.given, 'separator': result.separator, 'score': result.score}}; print(json.dumps(output, ensure_ascii=False))"

        result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding='utf-8')
        assert result.returncode == 0, f"Subprocess failed: {result.stderr}"

        rust_result = json.loads(result.stdout.strip())

        assert rust_result["family"] == expected["family"]
        assert rust_result["given"] == expected["given"]
        assert rust_result["separator"] == expected["separator"]

        score_diff = abs(rust_result["score"] - expected["score"])
        assert score_diff < 0.1, f"Score difference too large for {undivided_name}"

    @pytest.mark.parametrize("family, given", calc_score_test_data)
    def test_calc_score_consistency(self, family: str, given: str):
        """Test that calc_score produces consistent results across backends."""
        python_divider = BasicNameDivider(BasicNameDividerConfig(backend="python"))
        rust_divider = BasicNameDivider(BasicNameDividerConfig(backend="rust"))

        python_score = python_divider.calc_score(family, given)
        rust_score = rust_divider.calc_score(family, given)

        # Scores should be very close
        score_diff = abs(python_score - rust_score)
        assert score_diff < 0.1, f"Score difference too large for {family} {given}: {score_diff}"

    def test_backend_type_safety(self):
        """Test that both backends return proper DividedName objects."""
        python_divider = BasicNameDivider(BasicNameDividerConfig(backend="python"))
        rust_divider = BasicNameDivider(BasicNameDividerConfig(backend="rust"))

        test_name = "菅義偉"

        python_result = python_divider.divide_name(test_name)
        rust_result = rust_divider.divide_name(test_name)

        # Both should return DividedName instances
        assert isinstance(python_result, DividedName)
        assert isinstance(rust_result, DividedName)

        # Both should have all required attributes
        for result in [python_result, rust_result]:
            assert hasattr(result, "family")
            assert hasattr(result, "given")
            assert hasattr(result, "separator")
            assert hasattr(result, "score")
            assert hasattr(result, "algorithm")
            assert isinstance(result.score, (int, float))

    def test_backend_configuration(self):
        """Test that backend configuration works correctly."""
        # Test default backend (python)
        default_divider = BasicNameDivider()
        assert default_divider._rust_divider is None
        assert default_divider.feature_extractor is not None

        # Test explicit python backend
        python_config = BasicNameDividerConfig(backend="python")
        python_divider = BasicNameDivider(python_config)
        assert python_divider._rust_divider is None
        assert python_divider.feature_extractor is not None

        # Test rust backend
        rust_config = BasicNameDividerConfig(backend="rust")
        rust_divider = BasicNameDivider(rust_config)
        assert rust_divider._rust_divider is not None
        assert isinstance(rust_divider._rust_divider, RustNameDividerWrapper)

    def test_error_handling_with_invalid_backend(self):
        """Test error handling with invalid backend specification."""
        # Invalid backend should use python as fallback
        config = BasicNameDividerConfig(backend="invalid")
        divider = BasicNameDivider(config)

        # Should fall back to Python backend
        assert divider._rust_divider is None
        assert divider.feature_extractor is not None

        # Should still work
        result = divider.divide_name("菅義偉")
        assert isinstance(result, DividedName)


class TestRustBackendConfigurationValidation:
    """Test Rust backend configuration validation."""

    def test_rust_backend_unsupported_config_error(self):
        """Test RustBackendUnsupportedConfigError message and inheritance."""
        error = RustBackendUnsupportedConfigError()
        assert isinstance(error, ValueError)

        # Test custom message
        custom_error = RustBackendUnsupportedConfigError("Custom error message")
        assert str(custom_error) == "Custom error message"

    def test_validate_rust_basic_config_with_custom_rules(self):
        """Test validation fails with custom_rules."""
        custom_rule = TwoCharRule()
        config = BasicNameDividerConfig(backend="rust", custom_rules=[custom_rule])

        with pytest.raises(RustBackendUnsupportedConfigError) as exc_info:
            validate_rust_basic_config(config)

        assert "custom_rules" in str(exc_info.value)
        assert "Use backend='python'" in str(exc_info.value)

    def test_validate_rust_basic_config_with_cache_mask_true(self):
        """Test validation fails with cache_mask=True."""
        config = BasicNameDividerConfig(backend="rust", cache_mask=True)

        with pytest.raises(RustBackendUnsupportedConfigError) as exc_info:
            validate_rust_basic_config(config)

        assert "cache_mask=True" in str(exc_info.value)
        assert "Use backend='python'" in str(exc_info.value)

    def test_validate_rust_basic_config_with_custom_path_csv(self):
        """Test validation fails with custom path_csv."""
        custom_path = "/tmp/custom_kanji.csv"
        config = BasicNameDividerConfig(backend="rust", path_csv=custom_path)

        with pytest.raises(RustBackendUnsupportedConfigError) as exc_info:
            validate_rust_basic_config(config)

        assert "custom path_csv" in str(exc_info.value)

    def test_validate_rust_basic_config_with_multiple_errors(self):
        """Test validation fails with multiple unsupported configurations."""
        custom_rule = TwoCharRule()
        config = BasicNameDividerConfig(
            backend="rust", custom_rules=[custom_rule], cache_mask=True, path_csv="/tmp/custom.csv"
        )

        with pytest.raises(RustBackendUnsupportedConfigError) as exc_info:
            validate_rust_basic_config(config)

        error_message = str(exc_info.value)
        assert "custom_rules" in error_message
        assert "cache_mask=True" in error_message
        assert "custom path_csv" in error_message

    def test_validate_rust_basic_config_with_supported_settings(self):
        """Test validation passes with supported configurations only."""
        config = BasicNameDividerConfig(
            backend="rust", separator="　", normalize_name=False, only_order_score_when_4=True  # Full-width space
        )

        # Should not raise any exception
        validate_rust_basic_config(config)

    def test_validate_rust_basic_config_with_wrong_type(self):
        """Test validation fails with wrong config type."""
        gbdt_config = GBDTNameDividerConfig(backend="rust")

        with pytest.raises(TypeError) as exc_info:
            validate_rust_basic_config(gbdt_config)

        assert "Expected BasicNameDividerConfig, got GBDTNameDividerConfig" in str(exc_info.value)

    def test_validate_rust_gbdt_config_with_custom_rules(self):
        """Test GBDT validation fails with custom_rules."""
        custom_rule = TwoCharRule()
        config = GBDTNameDividerConfig(backend="rust", custom_rules=[custom_rule])

        with pytest.raises(RustBackendUnsupportedConfigError) as exc_info:
            validate_rust_gbdt_config(config)

        assert "custom_rules" in str(exc_info.value)

    def test_validate_rust_gbdt_config_with_custom_paths(self):
        """Test GBDT validation fails with custom paths."""
        config = GBDTNameDividerConfig(
            backend="rust",
            path_csv="/tmp/custom_kanji.csv",
            path_family_names="/tmp/custom_family.pkl",
            path_model="/tmp/custom_model.lgb",
        )

        with pytest.raises(RustBackendUnsupportedConfigError) as exc_info:
            validate_rust_gbdt_config(config)

        error_message = str(exc_info.value)
        assert "custom path_csv" in error_message
        assert "custom path_family_names" in error_message
        assert "custom path_model" in error_message

    def test_validate_rust_gbdt_config_with_supported_settings(self):
        """Test GBDT validation passes with supported configurations only."""
        config = GBDTNameDividerConfig(backend="rust", separator="　", normalize_name=False)  # Full-width space

        # Should not raise any exception
        validate_rust_gbdt_config(config)

    def test_validate_rust_gbdt_config_with_wrong_type(self):
        """Test GBDT validation fails with wrong config type."""
        basic_config = BasicNameDividerConfig(backend="rust")

        with pytest.raises(TypeError) as exc_info:
            validate_rust_gbdt_config(basic_config)

        assert "Expected GBDTNameDividerConfig, got BasicNameDividerConfig" in str(exc_info.value)

    def test_create_rust_basic_divider_with_invalid_config(self):
        """Test create_rust_basic_divider fails with invalid configuration."""
        custom_rule = TwoCharRule()
        config = BasicNameDividerConfig(backend="rust", custom_rules=[custom_rule])

        with pytest.raises(RustBackendUnsupportedConfigError):
            create_rust_basic_divider(config)

    def test_create_rust_gbdt_divider_with_invalid_config(self):
        """Test create_rust_gbdt_divider fails with invalid configuration."""
        config = GBDTNameDividerConfig(backend="rust", cache_mask=True, path_csv="/tmp/custom.csv")

        with pytest.raises(RustBackendUnsupportedConfigError):
            create_rust_gbdt_divider(config)

    def test_create_rust_basic_divider_with_wrong_config_type(self):
        """Test create_rust_basic_divider fails with wrong config type."""
        gbdt_config = GBDTNameDividerConfig(backend="rust")

        with pytest.raises(TypeError) as exc_info:
            create_rust_basic_divider(gbdt_config)

        assert "Expected BasicNameDividerConfig, got GBDTNameDividerConfig" in str(exc_info.value)

    def test_create_rust_gbdt_divider_with_wrong_config_type(self):
        """Test create_rust_gbdt_divider fails with wrong config type."""
        basic_config = BasicNameDividerConfig(backend="rust")

        with pytest.raises(TypeError) as exc_info:
            create_rust_gbdt_divider(basic_config)

        assert "Expected GBDTNameDividerConfig, got BasicNameDividerConfig" in str(exc_info.value)
