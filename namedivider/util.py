import urllib.request
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


def download_family_name_pickle_if_needed(path: Union[str, Path]) -> None:
    """
    When a default path is provided, download from the Internet if not already downloaded.
    """
    path = Path(path)
    if path != get_family_name_pkl_default_path():
        return None
    if path.exists():
        return None
    DEFAULT_CACHE_DIR.mkdir(exist_ok=True, parents=True)
    print("Download FamilyNameRepository from GitHub...")
    with urllib.request.urlopen(FAMILY_NAME_REPOSITORY_URL) as response:
        content = response.read()
    with open(path, "wb") as f:
        f.write(content)


def download_gbdt_model_v1_if_needed(path: Union[str, Path]) -> None:
    """
    When a default path is provided, download from the Internet if not already downloaded.
    """
    path = Path(path)
    if path != get_gbdt_model_v1_default_path():
        return None
    if path.exists():
        return None
    DEFAULT_CACHE_DIR.mkdir(exist_ok=True, parents=True)
    print("Download GBDT Model from GitHub...")
    with urllib.request.urlopen(GBDT_MODEL_V1_URL) as response:
        content = response.read()
    with open(path, "wb") as f:
        f.write(content)
