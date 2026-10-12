import hashlib
import io
import pickle
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

from namedivider import util
from namedivider.feature.family_name import FamilyNameRepository

CURRENT_DIR = Path(__file__).resolve().parent


def test_family_name_repository_exists():
    repo = FamilyNameRepository(path_txt=CURRENT_DIR / ".." / "assets" / "family_name_for_test.txt")
    exists = repo.exists("安倍")
    assert exists
    exists = repo.exists("森")
    assert not exists


def test_family_name_repository_get_rank_exists():
    repo = FamilyNameRepository(path_txt=CURRENT_DIR / ".." / "assets" / "family_name_for_test.txt")
    rank = repo.get_rank("菅")
    assert rank == 1


def test_family_name_repository_get_rank_not_exists():
    repo = FamilyNameRepository(path_txt=CURRENT_DIR / ".." / "assets" / "family_name_for_test.txt")
    rank = repo.get_rank("岸田")
    assert np.isnan(rank)


@pytest.fixture
def family_asset(tmp_path, monkeypatch):
    text = tmp_path / "names.txt"
    text.write_text("山田\n佐藤", encoding="utf-8")
    content = pickle.dumps(FamilyNameRepository(text))
    monkeypatch.setattr(util, "DEFAULT_CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(util, "_FAMILY_NAME_REPOSITORY_SHA256", hashlib.sha256(content).hexdigest())
    request = Mock(side_effect=lambda *a, **kw: io.BytesIO(content))
    monkeypatch.setattr(util.urllib.request, "urlopen", request)
    return util.get_family_name_pkl_default_path(), content, request


def test_from_standard_path(family_asset):
    path, _, _ = family_asset
    repo = FamilyNameRepository.from_path(str(path))
    assert repo.get_rank("山田") == 0
    assert repo.get_rank("佐藤") == 1


@pytest.mark.parametrize("cached", [None, b"modified"])
def test_unverified_dictionary_never_deserialized(family_asset, monkeypatch, cached):
    path, _, request = family_asset
    if cached is not None:
        path.parent.mkdir()
        path.write_bytes(cached)
    request.side_effect = lambda *a, **kw: io.BytesIO(b"invalid download")
    deserialize = Mock()
    monkeypatch.setattr(pickle, "loads", deserialize)
    monkeypatch.setattr(pickle, "load", deserialize)
    with pytest.raises(util._StandardAssetError, match="SHA-256 mismatch"):
        FamilyNameRepository.from_path(path)
    deserialize.assert_not_called()
    assert not path.exists() if cached is None else path.read_bytes() == cached


def test_verified_dictionary_survives_cache_replacement(family_asset, monkeypatch):
    path, content, request = family_asset
    path.parent.mkdir()
    path.write_bytes(content)
    original = util.get_verified_family_name_bytes

    def read_then_replace(filename):
        verified = original(filename)
        path.write_bytes(b"replaced pickle")
        return verified

    monkeypatch.setattr("namedivider.feature.family_name.get_verified_family_name_bytes", read_then_replace)
    repo = FamilyNameRepository.from_path(path)
    assert repo.get_rank("山田") == 0
    assert repo.get_rank("佐藤") == 1
    request.assert_not_called()


@pytest.mark.parametrize("suffix", [".pickle", ".txt"])
def test_from_custom_path(family_asset, tmp_path, suffix):
    _, content, request = family_asset
    custom = tmp_path / ("custom" + suffix)
    content = content if suffix == ".pickle" else (tmp_path / "names.txt").read_bytes()
    custom.write_bytes(content)
    repo = FamilyNameRepository.from_path(custom)
    assert repo.get_rank("山田") == 0
    assert repo.get_rank("佐藤") == 1
    assert custom.read_bytes() == content
    request.assert_not_called()
