import pytest

from namedivider.divider.config import BasicNameDividerConfig, GBDTNameDividerConfig
from namedivider.divider.divided_name import DividedName
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
