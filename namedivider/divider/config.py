from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional, Union

from namedivider.rule.rule import Rule
from namedivider.util import (
    get_family_name_pkl_default_path,
    get_gbdt_model_v1_default_path,
    get_kanji_csv_default_path,
)

KANJI_CSV_DEFAULT_PATH = get_kanji_csv_default_path()
FAMILY_NAME_PKL_DEFAULT_PATH = get_family_name_pkl_default_path()
GBDT_MODEL_V1_DEFAULT_PATH = get_gbdt_model_v1_default_path()


class NameDividerVersions(Enum):
    BASIC_NAME_DIVIDER_V1 = auto()
    BASIC_NAME_DIVIDER_V2 = auto()
    BASIC_NAME_DIVIDER_LATEST = auto()
    GBDT_NAME_DIVIDER_V1 = auto()
    GBDT_NAME_DIVIDER_LATEST = auto()


@dataclass(frozen=True)
class NameDividerConfigBase:
    """
    separator: Characters to separate a family name and a given name.
    normalize_name: Flag whether or not to normalize Kanji characters.
    'normalize' here means to internally convert old character form(旧字体) or variant character form(異字体)
    into orthographic character form(正字体) before processing them.
    algorithm_name: Name of algorithm.
    """

    separator: str = " "
    normalize_name: bool = True
    algorithm_name: str = "unknown_algorithm"
    custom_rules: Optional[List[Rule]] = None


@dataclass(frozen=True)
class BasicNameDividerConfig(NameDividerConfigBase):
    """
    path_csv: Path of the file containing the kanji information.
    only_order_score_when_4: If True, only order score is used for 4-character names. Not recommended to be True.
    """

    path_csv: Union[str, Path] = KANJI_CSV_DEFAULT_PATH
    only_order_score_when_4: bool = False
    algorithm_name: str = "kanji_feature"


@dataclass(frozen=True)
class GBDTNameDividerConfig(NameDividerConfigBase):
    """
    path_csv: Path of the file containing the kanji information.
    path_family_names: Allows .pickle file or text file(like .txt, .log, etc...)
    - .pickle file
    Pickled object must be instance of FamilyNameRepository.
    - text file
    Path of a file with multiple family names enumerated.
    path_model: Path of a GBDT model.
    """

    path_csv: Union[str, Path] = KANJI_CSV_DEFAULT_PATH
    path_family_names: Union[str, Path] = FAMILY_NAME_PKL_DEFAULT_PATH
    path_model: Union[str, Path] = GBDT_MODEL_V1_DEFAULT_PATH
    algorithm_name: str = "gbdt"


def get_config_from_version(version: NameDividerVersions) -> NameDividerConfigBase:
    if version == NameDividerVersions.BASIC_NAME_DIVIDER_V1:
        return BasicNameDividerConfig(
            separator=" ", normalize_name=False, path_csv=KANJI_CSV_DEFAULT_PATH, only_order_score_when_4=True
        )
    elif version == NameDividerVersions.BASIC_NAME_DIVIDER_V2:
        return BasicNameDividerConfig(
            separator=" ", normalize_name=True, path_csv=KANJI_CSV_DEFAULT_PATH, only_order_score_when_4=False
        )
    elif version == NameDividerVersions.BASIC_NAME_DIVIDER_LATEST:
        return BasicNameDividerConfig()
    elif version == NameDividerVersions.GBDT_NAME_DIVIDER_V1:
        return GBDTNameDividerConfig(
            separator=" ",
            normalize_name=True,
            path_csv=KANJI_CSV_DEFAULT_PATH,
            path_family_names=FAMILY_NAME_PKL_DEFAULT_PATH,
            path_model=GBDT_MODEL_V1_DEFAULT_PATH,
        )
    elif version == NameDividerVersions.GBDT_NAME_DIVIDER_LATEST:
        return GBDTNameDividerConfig()
    else:
        raise ValueError(f"Version {version} is not in NameDividerVersions.")
