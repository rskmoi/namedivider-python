import pytest

from namedivider.divider.config import BasicNameDividerConfig, GBDTNameDividerConfig


class TestBackendValidation:
    """Test backend validation for NameDivider configs."""

    def test_basic_config_valid_python_backend(self):
        """Test BasicNameDividerConfig with valid python backend."""
        config = BasicNameDividerConfig(backend="python")
        assert config.backend == "python"

    def test_basic_config_valid_rust_backend(self):
        """Test BasicNameDividerConfig with valid rust backend."""
        config = BasicNameDividerConfig(backend="rust")
        assert config.backend == "rust"

    def test_basic_config_invalid_backend(self):
        """Test BasicNameDividerConfig with invalid backend raises ValueError."""
        with pytest.raises(ValueError, match="Invalid backend 'invalid'"):
            BasicNameDividerConfig(backend="invalid")

    def test_gbdt_config_valid_python_backend(self):
        """Test GBDTNameDividerConfig with valid python backend."""
        config = GBDTNameDividerConfig(backend="python")
        assert config.backend == "python"

    def test_gbdt_config_valid_rust_backend(self):
        """Test GBDTNameDividerConfig with valid rust backend."""
        config = GBDTNameDividerConfig(backend="rust")
        assert config.backend == "rust"

    def test_gbdt_config_invalid_backend(self):
        """Test GBDTNameDividerConfig with invalid backend raises ValueError."""
        with pytest.raises(ValueError, match="Invalid backend 'invalid'"):
            GBDTNameDividerConfig(backend="invalid")

    def test_backend_validation_error_message(self):
        """Test that error message contains valid backend options."""
        with pytest.raises(ValueError, match="Valid backends are: python, rust"):
            BasicNameDividerConfig(backend="unknown")

    def test_backend_case_sensitivity(self):
        """Test that backend validation is case sensitive."""
        with pytest.raises(ValueError, match="Invalid backend 'Python'"):
            BasicNameDividerConfig(backend="Python")

        with pytest.raises(ValueError, match="Invalid backend 'RUST'"):
            GBDTNameDividerConfig(backend="RUST")
