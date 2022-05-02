from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
DEFAULT_CACHE_DIR = Path("~/.cache/namedivider-python")


# TODO: Add docs, add auto download func


def get_kanji_csv_default_path() -> Path:
    return CURRENT_DIR / "assets" / "kanji.csv"


def get_family_name_txt_default_path() -> Path:
    return (DEFAULT_CACHE_DIR / "family_names.txt").expanduser()


def get_gbdt_model_v1_default_path() -> Path:
    return (DEFAULT_CACHE_DIR / "gbdt_model_v1.txt").expanduser()
