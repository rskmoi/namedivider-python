from pathlib import Path
from typing import Union

CURRENT_DIR = Path(__file__).resolve().parent
DEFAULT_CACHE_DIR = Path("~/.cache/namedivider-python")


# TODO: Add docs, add auto download func


def get_kanji_csv_default_path() -> Path:
    return CURRENT_DIR / "assets" / "kanji.csv"


def get_family_name_pkl_default_path() -> Path:
    return (DEFAULT_CACHE_DIR / "family_names.pickle").expanduser()


def get_gbdt_model_v1_default_path() -> Path:
    return (DEFAULT_CACHE_DIR / "gbdt_model_v1.txt").expanduser()


def download_family_name_pickle_if_needed(path: Union[str, Path]):
    if Path(path) != get_family_name_pkl_default_path():
        return None
    if path.exists():
        return None


def download_gbdt_model_v1_if_needed(path: Union[str, Path]):
    if Path(path) != get_gbdt_model_v1_default_path():
        return None
    if path.exists():
        return None