from enum import Enum, auto
from pathlib import Path
from dataclasses import dataclass
CURRENT_DIR = Path(__file__).resolve().parent


class NameDividerVersions(Enum):
    BASIC_NAME_DIVIDER_V1 = auto()
    BASIC_NAME_DIVIDER_V2 = auto()
    BASIC_NAME_DIVIDER_LATEST = auto()


@dataclass(frozen=True)
class NameDividerConfigBase:
    separator: str = " "
    normalize_name: bool = True


@dataclass(frozen=True)
class BasicNameDividerConfig(NameDividerConfigBase):
    path_csv: str = f"{CURRENT_DIR}/../assets/kanji.csv"
    only_order_score_when_4: bool = False


def get_config_from_version(version: NameDividerVersions):
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
    else:
        raise ValueError(f"Version {version} is not in NameDividerVersions.")
