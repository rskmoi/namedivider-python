from __future__ import annotations

import random
from typing import cast

import regex
import typer
from tqdm import tqdm


def augment(src: str, dst: str, factor: int = 7) -> None:
    compiled_regex_kanji = regex.compile(r"\p{Script=Han}+")
    with open(src, "rb") as f:
        text = f.read().decode()
    names = text.split("\n")

    names_for_training = []
    family_names = []
    given_names = []
    _names = cast(list[str], tqdm(names))  # type: ignore[abstract]
    for _name in _names:
        if not compiled_regex_kanji.fullmatch(_name.replace(" ", "")):
            continue
        if " " not in _name:
            continue
        names_for_training.append(_name)
        _family, _given = _name.split(" ")
        family_names.append(_family)
        given_names.append(_given)

    for i in range(factor):
        random.shuffle(family_names)
        random.shuffle(given_names)
        for _family, _given in zip(family_names, given_names):
            names_for_training.append(f"{_family} {_given}")

    with open(dst, "wb") as f:
        f.write("\n".join(names_for_training).encode())


if __name__ == "__main__":
    typer.run(augment)
