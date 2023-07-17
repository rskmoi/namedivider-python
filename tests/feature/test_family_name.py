from pathlib import Path

import numpy as np

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
