from typing import Union
from enum import Enum, auto
from pathlib import Path
from dataclasses import dataclass
CURRENT_DIR = Path(__file__).resolve().parent
DEFAULT_CACHE_DIR = "~/.cache/namedivider-python"


class NameDividerVersions(Enum):
    BASIC_NAME_DIVIDER_V1 = auto()
    BASIC_NAME_DIVIDER_V2 = auto()
    BASIC_NAME_DIVIDER_LATEST = auto()
    GBDT_NAME_DIVIDER_V1 = auto()
    GBDT_NAME_DIVIDER_LATEST = auto()


@dataclass(frozen=True)
class NameDividerConfigBase:
    separator: str = " "
    normalize_name: bool = True


@dataclass(frozen=True)
class BasicNameDividerConfig(NameDividerConfigBase):
    path_csv: Union[str, Path] = Path(f"{CURRENT_DIR}/../assets/kanji.csv")
    only_order_score_when_4: bool = False


@dataclass(frozen=True)
class GBDTNameDividerConfig(NameDividerConfigBase):
    path_csv: Union[str, Path] = Path(f"{CURRENT_DIR}/../assets/kanji.csv")
    path_family_names: Union[str, Path] = Path(f"{DEFAULT_CACHE_DIR}/family_names.txt").expanduser()
    path_model: Union[str, Path] = Path(f"{DEFAULT_CACHE_DIR}/gbdt_model_v1.txt").expanduser()


def get_config_from_version(version: NameDividerVersions) -> NameDividerConfigBase:
    if version == NameDividerVersions.BASIC_NAME_DIVIDER_V1:
        return BasicNameDividerConfig(
            separator=" ",
            normalize_name=False,
            path_csv=f"{CURRENT_DIR}/../assets/kanji.csv",
            only_order_score_when_4=True
        )
    elif version == NameDividerVersions.BASIC_NAME_DIVIDER_V2:
        return BasicNameDividerConfig(
            separator=" ",
            normalize_name=True,
            path_csv=f"{CURRENT_DIR}/../assets/kanji.csv",
            only_order_score_when_4=False
        )
    elif version == NameDividerVersions.BASIC_NAME_DIVIDER_LATEST:
        return BasicNameDividerConfig()
    elif version == NameDividerVersions.GBDT_NAME_DIVIDER_V1:
        return GBDTNameDividerConfig(
            separator=" ",
            normalize_name=True,
            path_csv=f"{CURRENT_DIR}/../assets/kanji.csv",
            path_family_names=f"{DEFAULT_CACHE_DIR}/family_names.txt",
            path_model=f"{DEFAULT_CACHE_DIR}/gbdt_model_v1.txt"
        )
    elif version == NameDividerVersions.GBDT_NAME_DIVIDER_LATEST:
        return GBDTNameDividerConfig()
    else:
        raise ValueError(f"Version {version} is not in NameDividerVersions.")
