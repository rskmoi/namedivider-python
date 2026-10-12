import hashlib
import io
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import Mock

import pytest

from namedivider import util
from namedivider.divider.config import GBDTNameDividerConfig
from namedivider.divider.gbdt_name_divider import GBDTNameDivider
from namedivider.feature.family_name import FamilyNameRepository


@pytest.fixture
def asset(tmp_path, monkeypatch):
    content = b"test asset"
    monkeypatch.setattr(util, "DEFAULT_CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(util, "FAMILY_NAME_REPOSITORY_SHA256", hashlib.sha256(content).hexdigest())
    response = Mock(side_effect=lambda *a, **kw: io.BytesIO(content))
    monkeypatch.setattr(util.urllib.request, "urlopen", response)
    return util.get_family_name_pkl_default_path(), content, response


@pytest.mark.parametrize("cached", [None, b"test asset"])
def test_missing_or_valid_cache(asset, cached):
    path, content, request = asset
    if cached is not None:
        path.parent.mkdir()
        path.write_bytes(cached)
    assert util.get_verified_family_name_bytes(str(path.parent / ".." / "cache" / path.name)) == content
    assert path.read_bytes() == content
    assert request.call_count == (cached != content)
    if request.called:
        assert request.call_args.kwargs["timeout"] == util.DOWNLOAD_TIMEOUT_SECONDS
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize("failure", ["hash", "network", "timeout", "save", "deadline", "size"])
def test_failure_does_not_publish(asset, monkeypatch, failure):
    path, _, request = asset
    path.parent.mkdir()
    if failure == "hash":
        request.side_effect = lambda *a, **kw: io.BytesIO(b"unverified")
    elif failure == "network":
        request.side_effect = OSError("offline")
    elif failure == "timeout":
        request.side_effect = TimeoutError("timeout")
    elif failure == "save":
        monkeypatch.setattr(util.os, "replace", Mock(side_effect=OSError("cannot save")))
    elif failure == "deadline":
        monkeypatch.setattr(util, "DOWNLOAD_DEADLINE_SECONDS", -1)
    else:
        monkeypatch.setattr(util, "MAX_ASSET_BYTES", 1)
    with pytest.raises(
        util.StandardAssetError,
        match="Cannot save standard asset" if failure == "save" else "Cannot obtain standard asset",
    ):
        util.get_verified_family_name_bytes(path)
    assert request.call_count == (1 if failure == "save" else 2)
    assert not path.exists()
    assert list(path.parent.iterdir()) == []


def test_custom_paths_are_untouched(asset, tmp_path):
    _, _, request = asset
    custom = tmp_path / "family_name_repository.pickle"
    custom.write_bytes(b"custom")
    util.download_family_name_pickle_if_needed(custom)
    util.download_gbdt_model_v1_if_needed(tmp_path / "gbdt_model_v1.txt")
    assert custom.read_bytes() == b"custom"
    request.assert_not_called()


def test_parallel_downloads(asset, monkeypatch):
    path, content, _ = asset
    barrier = threading.Barrier(2)
    original_publish = util._publish_verified_asset
    temporary_paths = []

    def publish(source, destination, expected_sha256):
        temporary_paths.append(source)
        assert Path(source).read_bytes() == content
        assert not path.exists()
        barrier.wait(timeout=10)
        original_publish(source, destination, expected_sha256)

    monkeypatch.setattr(util, "_publish_verified_asset", publish)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(util.get_verified_family_name_bytes, [path, path]))
    assert results == [content, content]
    assert len(set(temporary_paths)) == 2
    assert path.read_bytes() == content
    assert list(path.parent.iterdir()) == [path]


def test_model_cache(asset, monkeypatch):
    _, content, request = asset
    monkeypatch.setattr(util, "GBDT_MODEL_V1_SHA256", hashlib.sha256(content).hexdigest())
    path = util.get_gbdt_model_v1_default_path()
    assert util.get_verified_gbdt_model_bytes(path) == content
    util.download_gbdt_model_v1_if_needed(str(path))
    assert request.call_count == 1


def test_invalid_pickle_never_deserialized(asset, monkeypatch):
    path, _, request = asset
    request.side_effect = lambda *a, **kw: io.BytesIO(b"invalid pickle")
    loads = Mock()
    monkeypatch.setattr(pickle, "loads", loads)
    monkeypatch.setattr(pickle, "load", loads)
    with pytest.raises(util.StandardAssetError, match="SHA-256 mismatch"):
        GBDTNameDivider(GBDTNameDividerConfig(path_family_names=path))
    loads.assert_not_called()


def test_verified_bytes_survive_replacement(asset, tmp_path, monkeypatch):
    import lightgbm

    path, _, request = asset
    text = tmp_path / "names.txt"
    text.write_text("山田\n佐藤", encoding="utf-8")
    content = pickle.dumps(FamilyNameRepository(text))
    monkeypatch.setattr(util, "FAMILY_NAME_REPOSITORY_SHA256", hashlib.sha256(content).hexdigest())
    request.side_effect = lambda *a, **kw: io.BytesIO(content)
    model_path = util.get_gbdt_model_v1_default_path()
    model_content = b"verified model"
    model_path.parent.mkdir()
    model_path.write_bytes(model_content)
    monkeypatch.setattr(util, "GBDT_MODEL_V1_SHA256", hashlib.sha256(model_content).hexdigest())
    original_model = util.get_verified_gbdt_model_bytes

    def read_model_then_replace(filename):
        verified = original_model(filename)
        model_path.write_bytes(b"replaced model")
        return verified

    monkeypatch.setattr("namedivider.divider.gbdt_name_divider.get_verified_gbdt_model_bytes", read_model_then_replace)
    original = util.get_verified_family_name_bytes

    def read_then_replace(filename):
        verified = original(filename)
        path.write_bytes(b"replaced pickle")
        return verified

    monkeypatch.setattr("namedivider.divider.gbdt_name_divider.get_verified_family_name_bytes", read_then_replace)
    booster = Mock()
    monkeypatch.setattr(lightgbm, "Booster", booster)
    divider = GBDTNameDivider(GBDTNameDividerConfig(path_family_names=path, path_model=model_path))
    assert divider.feature_extractor.family_name_repository.get_rank("山田") == 0
    booster.assert_called_once_with(model_str="verified model")


@pytest.mark.parametrize("suffix", [".pickle", ".txt"])
def test_custom_dictionary_and_model(asset, tmp_path, monkeypatch, suffix):
    import lightgbm

    _, _, request = asset
    text = tmp_path / "names.txt"
    text.write_text("山田", encoding="utf-8")
    custom = tmp_path / ("custom" + suffix)
    if suffix == ".pickle":
        custom.write_bytes(pickle.dumps(FamilyNameRepository(text)))
    else:
        custom.write_bytes(text.read_bytes())
    booster = Mock()
    monkeypatch.setattr(lightgbm, "Booster", booster)
    GBDTNameDivider(GBDTNameDividerConfig(path_family_names=custom, path_model="custom-model.txt"))
    request.assert_not_called()
    booster.assert_called_once_with(model_file="custom-model.txt")


@pytest.mark.parametrize("kind", ["family", "model"])
def test_path_checks_have_no_side_effects(asset, monkeypatch, kind):
    path, _, request = asset
    if kind == "model":
        path = util.get_gbdt_model_v1_default_path()
    predicate = util.is_standard_family_name_path if kind == "family" else util.is_standard_gbdt_model_path
    monkeypatch.chdir(path.parent.parent)
    assert predicate(Path("cache") / path.name)
    assert predicate(str(path))
    assert predicate(path.parent / ".." / "cache" / path.name)
    assert not predicate(path.parent.parent / path.name)
    assert not path.parent.exists()
    request.assert_not_called()


def test_handles_closed_before_replace(asset, monkeypatch):
    path, content, request = asset
    response = io.BytesIO(content)
    request.side_effect = None
    request.return_value = response
    factory = util.tempfile.NamedTemporaryFile
    replace = util.os.replace
    handles = []

    def temporary(**kwargs):
        handle = factory(**kwargs)
        handles.append(handle)
        return handle

    def checked_replace(source, destination):
        assert response.closed
        assert all(handle.closed for handle in handles)
        replace(source, destination)

    monkeypatch.setattr(util.tempfile, "NamedTemporaryFile", temporary)
    monkeypatch.setattr(util.os, "replace", checked_replace)
    assert util.get_verified_family_name_bytes(path) == content


def test_write_failure_cleans_temporary(asset, monkeypatch):
    path, _, _ = asset
    factory = util.tempfile.NamedTemporaryFile

    def temporary(**kwargs):
        handle = factory(**kwargs)
        handle.write = Mock(side_effect=OSError("disk full"))
        return handle

    monkeypatch.setattr(util.tempfile, "NamedTemporaryFile", temporary)
    with pytest.raises(util.StandardAssetError, match="disk full"):
        util.get_verified_family_name_bytes(path)
    assert list(path.parent.iterdir()) == []


@pytest.mark.parametrize("kind", ["family", "model"])
@pytest.mark.parametrize("cached", [b"", b"test", b"changed"])
def test_invalid_existing_cache_is_recovered(asset, monkeypatch, kind, cached):
    path, content, request = asset
    if kind == "model":
        path = util.get_gbdt_model_v1_default_path()
        monkeypatch.setattr(util, "GBDT_MODEL_V1_SHA256", hashlib.sha256(content).hexdigest())
    path.parent.mkdir()
    path.write_bytes(cached)
    getter = util.get_verified_family_name_bytes if kind == "family" else util.get_verified_gbdt_model_bytes
    assert getter(path) == content
    assert path.read_bytes() == content
    assert list(path.parent.iterdir()) == [path]
    assert request.call_count == 1


def test_modified_pickle_never_deserialized(asset, monkeypatch):
    path, _, request = asset
    path.parent.mkdir()
    path.write_bytes(b"modified pickle")
    request.side_effect = lambda *a, **kw: io.BytesIO(b"invalid download")
    loads = Mock()
    monkeypatch.setattr(pickle, "loads", loads)
    monkeypatch.setattr(pickle, "load", loads)
    with pytest.raises(util.StandardAssetError, match="SHA-256 mismatch"):
        GBDTNameDivider(GBDTNameDividerConfig(path_family_names=path))
    loads.assert_not_called()
    assert request.call_count == 2
    assert path.read_bytes() == b"modified pickle"


@pytest.mark.parametrize("kind", ["family", "model"])
@pytest.mark.parametrize("cached", [None, b"corrupt"])
@pytest.mark.parametrize("first_failure", ["hash", "network", "timeout"])
def test_download_recovers_on_second_attempt(asset, monkeypatch, kind, cached, first_failure):
    path, content, request = asset
    if kind == "model":
        path = util.get_gbdt_model_v1_default_path()
        monkeypatch.setattr(util, "GBDT_MODEL_V1_SHA256", hashlib.sha256(content).hexdigest())
    if cached is not None:
        path.parent.mkdir()
        path.write_bytes(cached)
    first = {"hash": io.BytesIO(b"invalid"), "network": OSError("offline"), "timeout": TimeoutError("timeout")}
    request.side_effect = [first[first_failure], io.BytesIO(content)]
    getter = util.get_verified_family_name_bytes if kind == "family" else util.get_verified_gbdt_model_bytes
    assert getter(path) == content
    assert request.call_count == 2
    assert path.read_bytes() == content
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize("kind", ["family", "model"])
@pytest.mark.parametrize("failure", ["hash", "network"])
def test_exhausted_recovery_preserves_existing_cache(asset, monkeypatch, kind, failure):
    path, content, request = asset
    if kind == "model":
        path = util.get_gbdt_model_v1_default_path()
        monkeypatch.setattr(util, "GBDT_MODEL_V1_SHA256", hashlib.sha256(content).hexdigest())
    path.parent.mkdir()
    path.write_bytes(b"original corrupt cache")
    request.side_effect = OSError("offline") if failure == "network" else lambda *a, **kw: io.BytesIO(b"bad")
    getter = util.get_verified_family_name_bytes if kind == "family" else util.get_verified_gbdt_model_bytes
    with pytest.raises(util.StandardAssetError, match="after 2 attempts"):
        getter(path)
    assert request.call_count == 2
    assert path.read_bytes() == b"original corrupt cache"
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize("kind", ["family", "model"])
def test_save_failure_preserves_existing_cache_without_redownload(asset, monkeypatch, kind):
    path, content, request = asset
    if kind == "model":
        path = util.get_gbdt_model_v1_default_path()
        monkeypatch.setattr(util, "GBDT_MODEL_V1_SHA256", hashlib.sha256(content).hexdigest())
    path.parent.mkdir()
    path.write_bytes(b"old cache")
    monkeypatch.setattr(util.os, "replace", Mock(side_effect=OSError("cannot save")))
    getter = util.get_verified_family_name_bytes if kind == "family" else util.get_verified_gbdt_model_bytes
    with pytest.raises(util.StandardAssetError, match="Cannot save standard asset"):
        getter(path)
    assert request.call_count == 1
    assert path.read_bytes() == b"old cache"
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize("kind", ["family", "model"])
def test_cache_migration_warning_precedes_download(asset, monkeypatch, kind):
    import warnings

    path, content, request = asset
    if kind == "model":
        path = util.get_gbdt_model_v1_default_path()
        monkeypatch.setattr(util, "GBDT_MODEL_V1_SHA256", hashlib.sha256(content).hexdigest())
    path.parent.mkdir()
    path.write_bytes(b"custom data")
    getter = util.get_verified_family_name_bytes if kind == "family" else util.get_verified_gbdt_model_bytes
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")

        def download(*args, **kwargs):
            assert len(recorded) == 1
            assert path.read_bytes() == b"custom data"
            return io.BytesIO(content)

        request.side_effect = download
        assert getter(path) == content
    message = str(recorded[0].message)
    assert recorded[0].category is RuntimeWarning
    assert str(path) in message
    assert "Starting with v0.4.2" in message
    assert "replace this file" in message
    assert "move it to a different path" in message
    assert "path_family_names or path_model" in message


@pytest.mark.parametrize("cached", [None, b"test asset"])
def test_missing_or_valid_cache_does_not_warn(asset, cached):
    import warnings

    path, _, _ = asset
    if cached is not None:
        path.parent.mkdir()
        path.write_bytes(cached)
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        util.get_verified_family_name_bytes(path)
    assert recorded == []


@pytest.mark.parametrize("published", [None, b"incorrect", b"test asset"])
def test_publication_conflict_requires_verified_cache(asset, monkeypatch, published):
    path, content, request = asset

    def competing_replace(source, destination):
        if published is not None:
            destination.write_bytes(published)
        raise PermissionError("concurrent replacement denied")

    monkeypatch.setattr(util.os, "replace", competing_replace)
    if published == content:
        assert util.get_verified_family_name_bytes(path) == content
    else:
        with pytest.raises(util.StandardAssetError, match="concurrent replacement denied"):
            util.get_verified_family_name_bytes(path)
    assert request.call_count == 1
    assert not path.exists() if published is None else path.read_bytes() == published
    assert list(path.parent.iterdir()) == ([] if published is None else [path])
