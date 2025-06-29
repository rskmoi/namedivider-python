import pytest

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


class TestBackendConsistency:
    """Test consistency between Python and Rust backends."""

    @pytest.mark.forked
    @pytest.mark.parametrize("undivided_name, expected", basic_expected_results)
    def test_basic_name_divider_rust_backend(self, undivided_name: str, expected: dict):
        from namedivider.divider.basic_name_divider import BasicNameDivider
        from namedivider.divider.config import BasicNameDividerConfig

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

    @pytest.mark.forked
    @pytest.mark.parametrize("undivided_name, expected", gbdt_expected_results)
    def test_gbdt_name_divider_rust_backend(self, undivided_name: str, expected: dict):
        from namedivider.divider.config import GBDTNameDividerConfig
        from namedivider.divider.gbdt_name_divider import GBDTNameDivider

        """Test that Rust GBDT backend produces expected results (avoiding Python/Rust lightgbm conflicts)."""
        rust_divider = GBDTNameDivider(GBDTNameDividerConfig(backend="rust"))
        rust_result = rust_divider.divide_name(undivided_name)

        # Check family and given names match expected results
        assert rust_result.family == expected["family"], f"Family name mismatch for {undivided_name}"
        assert rust_result.given == expected["given"], f"Given name mismatch for {undivided_name}"
        assert rust_result.separator == expected["separator"], f"Separator mismatch for {undivided_name}"

        # For GBDT, scores might differ slightly between Python and Rust implementations
        # Allow reasonable tolerance
        score_diff = abs(rust_result.score - expected["score"])
        assert (
            score_diff < 0.1
        ), f"Score difference too large for {undivided_name}: expected {expected['score']}, got {rust_result.score}"

    @pytest.mark.forked
    @pytest.mark.parametrize("family, given", calc_score_test_data)
    def test_calc_score_consistency(self, family: str, given: str):
        from namedivider.divider.basic_name_divider import BasicNameDivider
        from namedivider.divider.config import BasicNameDividerConfig

        """Test that calc_score produces consistent results across backends."""
        python_divider = BasicNameDivider(BasicNameDividerConfig(backend="python"))
        rust_divider = BasicNameDivider(BasicNameDividerConfig(backend="rust"))

        python_score = python_divider.calc_score(family, given)
        rust_score = rust_divider.calc_score(family, given)

        # Scores should be very close
        score_diff = abs(python_score - rust_score)
        assert score_diff < 0.1, f"Score difference too large for {family} {given}: {score_diff}"

    @pytest.mark.forked
    def test_backend_type_safety(self):
        from namedivider.divider.basic_name_divider import BasicNameDivider
        from namedivider.divider.config import BasicNameDividerConfig
        from namedivider.divider.divided_name import DividedName

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

    @pytest.mark.forked
    def test_backend_configuration(self):
        from namedivider.divider.basic_name_divider import BasicNameDivider
        from namedivider.divider.config import BasicNameDividerConfig
        from namedivider.divider.rust_backend import RustNameDividerWrapper

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

    @pytest.mark.forked
    def test_error_handling_with_invalid_backend(self):
        from namedivider.divider.basic_name_divider import BasicNameDivider
        from namedivider.divider.config import BasicNameDividerConfig
        from namedivider.divider.divided_name import DividedName

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
