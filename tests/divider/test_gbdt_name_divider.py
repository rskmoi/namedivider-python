import hashlib
import inspect
import os
import pickle
import warnings
from dataclasses import replace
from pathlib import Path
from typing import Dict
from unittest.mock import Mock

import pytest

from namedivider import util
from namedivider.divider.config import (
    GBDTNameDividerConfig,
    NameDividerVersions,
    get_config_from_version,
)
from namedivider.divider.gbdt_name_divider import GBDTNameDivider
from namedivider.feature.family_name import FamilyNameRepository


@pytest.fixture
def standard_asset_paths(tmp_path, monkeypatch):
    # Real-data score regressions are opt-in; ordinary unit tests never download.
    source = os.environ.get("NAMEDIVIDER_STANDARD_ASSET_TEST_DIR")
    if source is None:
        pytest.skip("Set NAMEDIVIDER_STANDARD_ASSET_TEST_DIR for real-asset score regressions")
    monkeypatch.setattr(util, "DEFAULT_CACHE_DIR", tmp_path)
    paths = {
        "path_family_names": util.get_family_name_pkl_default_path(),
        "path_model": util.get_gbdt_model_v1_default_path(),
    }
    for path in paths.values():
        path.write_bytes((Path(source) / path.name).read_bytes())
    monkeypatch.setattr(util.urllib.request, "urlopen", lambda *a, **kw: pytest.fail("Unexpected network access"))
    return paths


name_test_data_v1 = [
    # two chars
    ("原敬", {"family": "原", "given": "敬", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    # kana and kanji
    ("中山マサ", {"family": "中山", "given": "マサ", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    ("つるの剛士", {"family": "つるの", "given": "剛士", "separator": " ", "score": 1.0, "algorithm": "rule"}),
    # three chars
    ("菅義偉", {"family": "菅", "given": "義偉", "separator": " ", "score": 0.7300634880343344, "algorithm": "gbdt"}),
    # four chars
    (
        "阿部晋三",
        {"family": "阿部", "given": "晋三", "separator": " ", "score": 0.5761118242092244, "algorithm": "gbdt"},
    ),
    # five chars
    (
        "中曽根康弘",
        {"family": "中曽根", "given": "康弘", "separator": " ", "score": 0.47535339308928076, "algorithm": "gbdt"},
    ),
    # with no kanji in kanji.txt
    ("蝶院羊", {"family": "蝶院", "given": "羊", "separator": " ", "score": 0.5013754025624984, "algorithm": "gbdt"}),
]


@pytest.mark.parametrize("undivided_name, expect", name_test_data_v1)
def test_divide_name_v1(undivided_name: str, expect: Dict, standard_asset_paths):
    name_divider = GBDTNameDivider(
        replace(get_config_from_version(NameDividerVersions.GBDT_NAME_DIVIDER_V1), **standard_asset_paths)
    )
    divided_name = name_divider.divide_name(undivided_name)
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


@pytest.mark.parametrize("undivided_name, expect", name_test_data_v1)
def test_divide_name_latest(undivided_name: str, expect: Dict, standard_asset_paths):
    name_divider = GBDTNameDivider(
        replace(get_config_from_version(NameDividerVersions.GBDT_NAME_DIVIDER_LATEST), **standard_asset_paths)
    )
    divided_name = name_divider.divide_name(undivided_name)
    assert divided_name.family == expect["family"]
    assert divided_name.given == expect["given"]
    assert divided_name.separator == expect["separator"]
    assert divided_name.score == expect["score"]
    assert divided_name.algorithm == expect["algorithm"]


def test_custom_model_uses_configured_path(tmp_path, monkeypatch):
    import lightgbm

    monkeypatch.setattr(util, "DEFAULT_CACHE_DIR", tmp_path)
    request = Mock(side_effect=AssertionError("Unexpected network"))
    monkeypatch.setattr(util.urllib.request, "urlopen", request)
    booster = Mock()
    monkeypatch.setattr(lightgbm, "Booster", booster)
    dictionary = Path(__file__).parent.parent / "assets" / "family_name_for_test.txt"
    GBDTNameDivider(GBDTNameDividerConfig(path_family_names=dictionary, path_model="custom-model.txt"))
    booster.assert_called_once_with(model_file=Path("custom-model.txt"))
    request.assert_not_called()


@pytest.mark.parametrize("as_string", [False, True])
@pytest.mark.parametrize("kind", ["custom_pickle", "text", "standard", "standard_equivalent"])
def test_dictionary_deprecation_at_loading(tmp_path, monkeypatch, kind, as_string):
    import lightgbm

    monkeypatch.setattr(util, "DEFAULT_CACHE_DIR", tmp_path / "cache")
    request = Mock(side_effect=AssertionError("Unexpected network"))
    monkeypatch.setattr(util.urllib.request, "urlopen", request)
    monkeypatch.setattr(lightgbm, "Booster", Mock())
    text = tmp_path / "family_names.txt"
    text.write_text("佐藤\n鈴木\n高橋\n", encoding="utf-8")
    content = pickle.dumps(FamilyNameRepository(text))
    if kind.startswith("standard"):
        path = util.get_family_name_pkl_default_path()
        path.parent.mkdir()
        path.write_bytes(content)
        monkeypatch.setattr(util, "_FAMILY_NAME_REPOSITORY_SHA256", hashlib.sha256(content).hexdigest())
        verified = Mock(wraps=util.get_verified_family_name_bytes)
        monkeypatch.setattr("namedivider.feature.family_name.get_verified_family_name_bytes", verified)
        if kind == "standard_equivalent":
            path = path.parent / ".." / "cache" / path.name
    elif kind == "custom_pickle":
        # Same basename as the standard asset must still be classified as custom.
        path = tmp_path / "family_name_repository.pickle"
        path.write_bytes(content)
    else:
        path = text

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        config = GBDTNameDividerConfig(path_family_names=str(path) if as_string else path, path_model="custom.txt")
        assert not caught
        call_line = inspect.currentframe().f_lineno + 1
        divider = GBDTNameDivider(config)
        loading_warnings = list(caught)
        divider.divide_name("原敬")
        divider.divide_name("原敬")
        assert caught == loading_warnings

    if kind == "custom_pickle":
        assert len(caught) == 1
        warning = caught[0]
        assert warning.category is DeprecationWarning
        assert "Custom pickle family dictionaries are deprecated" in str(warning.message)
        assert "UTF-8 text dictionary with one family name per line" in str(warning.message)
        assert warning.filename == __file__
        assert warning.lineno == call_line
        assert path.read_bytes() == content
    else:
        assert not caught
    if kind.startswith("standard"):
        verified.assert_called_once_with(config.path_family_names)
    for rank, family in enumerate(["佐藤", "鈴木", "高橋"]):
        assert divider.feature_extractor.family_name_repository.get_rank(family) == rank
    request.assert_not_called()
