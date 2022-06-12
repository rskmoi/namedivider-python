import typer
import pandas as pd
import _pickle as pickle
from tqdm import tqdm
from dataclasses import asdict
from namedivider.feature.extractor import FamilyRankingFeatureExtractor
from namedivider.feature.kanji import KanjiStatisticsRepository
from namedivider.feature.family_name import FamilyNameRepository
from namedivider.util import get_kanji_csv_default_path, get_family_name_pkl_default_path
import regex


def extract_feature(src: str, dst: str):
    compiled_regex_kanji = regex.compile(r'\p{Script=Han}+')
    kanji_statistics_repository = KanjiStatisticsRepository(path_csv=get_kanji_csv_default_path())
    path_pickle = get_family_name_pkl_default_path()
    with open(path_pickle, "rb") as f:
        family_name_repository: FamilyNameRepository = pickle.load(f)
    extractor = FamilyRankingFeatureExtractor(kanji_statistics_repository=kanji_statistics_repository,
                                              family_name_repository=family_name_repository)
    with open(src, "rb") as f:
        text = f.read().decode()
    names = text.split("\n")

    features = []
    for _name in tqdm(names):
        if not compiled_regex_kanji.fullmatch(_name.replace(" ", "")):
            continue
        if " " not in _name:
            continue
        undivided_name = _name.replace(" ", "")
        for i in range(len(undivided_name) - 1):
            _family = undivided_name[:i + 1]
            _given = undivided_name[i + 1:]
            target = f"{_family} {_given}" == _name
            _feature_base = {"name": f"{_family} {_given}", "target": target}
            _feature = asdict(extractor.get_features(_family, _given))
            _feature_base.update(_feature)
            features.append(_feature_base)

    pd.DataFrame(features).to_csv(dst, index=False)


if __name__ == '__main__':
    typer.run(extract_feature)