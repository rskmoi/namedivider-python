from pathlib import Path
CURRENT_DIR = Path(__file__).resolve().parent
DEFAULT_CACHE_DIR = Path("~/.cache/namedivider-python")


def get_kanji_csv_default_path() -> Path:
    return CURRENT_DIR / "assets" / "kanji.csv"


def get_family_name_txt_default_path():
    return (DEFAULT_CACHE_DIR / "family_names.txt").expanduser()