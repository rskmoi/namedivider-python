from pathlib import Path

import numpy as np
import pytest

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


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("trailing_newline", [False, True])
def test_newlines_and_blank_lines(tmp_path, newline, trailing_newline):
    path = tmp_path / "families.txt"
    content = newline.join(["", "佐藤", "", " \t　", "鈴木", "高橋"])
    path.write_bytes((content + (newline if trailing_newline else "")).encode())
    repo = FamilyNameRepository(path)
    for rank, family in enumerate(["佐藤", "鈴木", "高橋"]):
        assert repo.exists(family)
        assert repo.get_rank(family) == rank
    assert not repo.exists("")
    assert not repo.exists(" \t　")


@pytest.mark.parametrize("content", [b"", b"\n\n", b"\r\n\r\n", b" \t\r\n"])
def test_empty_dictionary(tmp_path, content):
    path = tmp_path / "families.txt"
    path.write_bytes(content)
    repo = FamilyNameRepository(path)
    assert not repo.exists("")
    assert not repo.exists("佐藤")
    assert np.isnan(repo.get_rank("佐藤"))


def test_whitespace_and_duplicate_ranks_are_preserved(tmp_path):
    path = tmp_path / "families.txt"
    path.write_bytes(" 佐藤 \r\n鈴木\r\n 佐藤 \r\n高 橋".encode())
    repo = FamilyNameRepository(path)
    assert not repo.exists("佐藤")
    assert repo.get_rank(" 佐藤 ") == 2
    assert repo.get_rank("鈴木") == 1
    assert repo.get_rank("高 橋") == 3
