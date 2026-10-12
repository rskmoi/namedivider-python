import hashlib
import http.client
import os
import tempfile
import threading
import time
import urllib.request
import warnings
from pathlib import Path
from typing import Union

CURRENT_DIR = Path(__file__).resolve().parent
DEFAULT_CACHE_DIR = Path("~/.cache/namedivider-python").expanduser()
GBDT_MODEL_V1_URL = "https://github.com/rskmoi/namedivider-python/releases/download/Models/gbdt_model_v1.txt"
FAMILY_NAME_REPOSITORY_URL = (
    "https://github.com/rskmoi/namedivider-python/releases/download/Models/family_name_repository.pickle"
)


def get_kanji_csv_default_path() -> Path:
    """
    Returns the default path of kanji.csv.
    """
    return CURRENT_DIR / "assets" / "kanji.csv"


def get_family_name_pkl_default_path() -> Path:
    """
    Returns the default path of family_name_repository.pickle.
    """
    return (DEFAULT_CACHE_DIR / "family_name_repository.pickle").expanduser()


def get_gbdt_model_v1_default_path() -> Path:
    """
    Returns the default path of gbdt_model_v1.txt
    """
    return (DEFAULT_CACHE_DIR / "gbdt_model_v1.txt").expanduser()


# Pinned from rskmoi's Models release via the HTTPS URLs above on 2026-10-12.
# https://github.com/rskmoi/namedivider-python/releases/tag/Models
# GitHub asset IDs / sizes: dictionary 66928540 / 495221 bytes,
# model 66925476 / 931415 bytes (both published 2022-05-29).
# Distribution updates require verifying provenance/content and updating these
# hashes in a package release; older packages will reject changed assets.
# Hash verification establishes identity with these assets, not pickle safety.
FAMILY_NAME_REPOSITORY_SHA256 = "789444cb3222f18199bd7e2916fa038741b414f0a113d75f13abfc704cb107df"
GBDT_MODEL_V1_SHA256 = "68307290a459b2b440988d576da9f04801819642fba04642b86d00ace8115c22"
# Per attempt: 60-second deadline plus at most one in-flight 30-second read.
# Two attempts allow roughly 180 seconds of network waiting per asset.
DOWNLOAD_ATTEMPTS = 2
DOWNLOAD_TIMEOUT_SECONDS = 30
DOWNLOAD_DEADLINE_SECONDS = 60
MAX_ASSET_BYTES = 16 * 1024 * 1024
# Windows can reject overlapping replacement operations on the same target.
# Downloads remain concurrent; only cache reads and publication are serialized.
_CACHE_IO_LOCK = threading.Lock()


class StandardAssetError(RuntimeError):
    """A standard asset could not be obtained, verified, or saved."""


def is_standard_family_name_path(path: Union[str, Path]) -> bool:
    """Compare normalized paths without creating directories or accessing the network."""
    return Path(path).expanduser().resolve() == get_family_name_pkl_default_path().resolve()


def is_standard_gbdt_model_path(path: Union[str, Path]) -> bool:
    return Path(path).expanduser().resolve() == get_gbdt_model_v1_default_path().resolve()


def _verified_asset_bytes(path: Union[str, Path], url: str, expected_sha256: str) -> bytes:
    path = Path(path).expanduser()
    try:
        with _CACHE_IO_LOCK:
            content = path.read_bytes()
        actual_sha256 = hashlib.sha256(content).hexdigest()
        if actual_sha256 == expected_sha256:
            return content
        warnings.warn(
            f"Standard cache {path} does not match the official distribution. "
            "Starting with v0.4.2, standard cache files are verified and custom data at these paths "
            "is no longer supported. The official asset will be downloaded and will replace this file "
            "if verification succeeds. To use a custom dictionary or model, move it to a different "
            "path and set GBDTNameDividerConfig.path_family_names or path_model accordingly.",
            RuntimeWarning,
            stacklevel=3,
        )
    except FileNotFoundError:
        pass
    except OSError as exc:
        raise StandardAssetError(f"Cannot read standard asset {path}: {exc}") from exc

    # Standard paths are managed caches: unexpected content is replaced only
    # after an official download verifies successfully. Custom paths never get here.
    content = _download_verified_bytes(path, url, expected_sha256)
    temporary_path = None
    try:
        path.parent.mkdir(exist_ok=True, parents=True)
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
        # Close the handle before replacement, including on Windows.
        _publish_verified_asset(temporary_path, path, expected_sha256)
        return content
    except OSError as exc:
        # Retrying network acquisition cannot repair a local storage failure.
        raise StandardAssetError(f"Cannot save standard asset {path}: {exc}") from exc
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _publish_verified_asset(source: Path, destination: Path, expected_sha256: str) -> None:
    with _CACHE_IO_LOCK:
        try:
            os.replace(source, destination)
        except PermissionError as exc:
            # Another process may have already published the same official asset.
            # Accept that outcome only after verifying its content; otherwise
            # propagate the storage failure without another network acquisition.
            try:
                content = destination.read_bytes()
            except OSError as read_error:
                raise exc from read_error
            if hashlib.sha256(content).hexdigest() != expected_sha256:
                raise


def _download_verified_bytes(path: Path, url: str, expected_sha256: str) -> bytes:
    for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
        try:
            deadline = time.monotonic() + DOWNLOAD_DEADLINE_SECONDS
            with urllib.request.urlopen(url, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
                chunks = []
                size = 0
                while True:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("download deadline exceeded")
                    chunk = response.read1(64 * 1024)
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > MAX_ASSET_BYTES:
                        raise ValueError("download exceeds standard asset size limit")
                    chunks.append(chunk)
                content = b"".join(chunks)
                actual_sha256 = hashlib.sha256(content).hexdigest()
                if actual_sha256 != expected_sha256:
                    raise ValueError(f"SHA-256 mismatch (expected {expected_sha256}, got {actual_sha256})")
            return content
        except (OSError, ValueError, http.client.HTTPException) as exc:
            if attempt == DOWNLOAD_ATTEMPTS:
                raise StandardAssetError(
                    f"Cannot obtain standard asset {path} from {url} after {attempt} attempts: {exc}"
                ) from exc
    raise AssertionError("DOWNLOAD_ATTEMPTS must be positive")


def get_verified_family_name_bytes(path: Union[str, Path]) -> Union[bytes, None]:
    """Return verified standard bytes, or None for a custom path."""
    if not is_standard_family_name_path(path):
        return None
    return _verified_asset_bytes(path, FAMILY_NAME_REPOSITORY_URL, FAMILY_NAME_REPOSITORY_SHA256)


def get_verified_gbdt_model_bytes(path: Union[str, Path]) -> Union[bytes, None]:
    """Return verified standard bytes, or None for a custom path."""
    if not is_standard_gbdt_model_path(path):
        return None
    return _verified_asset_bytes(path, GBDT_MODEL_V1_URL, GBDT_MODEL_V1_SHA256)


def download_family_name_pickle_if_needed(path: Union[str, Path]) -> None:
    """Verify the standard cache; recover missing or corrupt data with bounded downloads."""
    get_verified_family_name_bytes(path)


def download_gbdt_model_v1_if_needed(path: Union[str, Path]) -> None:
    """Verify the standard cache; recover missing or corrupt data with bounded downloads."""
    get_verified_gbdt_model_bytes(path)
