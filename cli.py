import click
from tqdm import tqdm
from pathlib import Path
from name_divider import NameDivider
CURRENT_DIR = Path(__file__).resolve().parent


@click.group()
def cmd():
    pass


@cmd.command()
@click.argument("undivided_name")
@click.option("--separator", "-s", default=" ")
def name(undivided_name: str, separator: str):
    name_divider = NameDivider(path_csv=Path(CURRENT_DIR) / "assets/kanji.csv", separator=separator)
    print(name_divider.divide_name(undivided_name))


@cmd.command()
@click.argument("undivided_name_text")
@click.option("--separator", "-s", default=" ")
@click.option("--encoder", "-e", default="utf-8")
def file(undivided_name_text, separator, encoder):
    name_divider = NameDivider(path_csv=Path(CURRENT_DIR) / "assets/kanji.csv", separator=separator)
    with open(undivided_name_text, "rb") as f:
        undivided_names = f.read().decode(encoder).strip().split("\n")
    divided_names = []
    for _undivided_name in tqdm(undivided_names):
        divided_names.append(str(name_divider.divide_name(_undivided_name)))
    print("\n".join(divided_names))


@cmd.command()
@click.argument("divided_name_text")
@click.option("--separator", "-s", default=" ")
@click.option("--encoder", "-e", default="utf-8")
def accuracy(divided_name_text, separator, encoder):
    name_divider = NameDivider(path_csv=Path(CURRENT_DIR) / "assets/kanji.csv", separator=separator)
    with open(divided_name_text, "rb") as f:
        divided_name_text = f.read().decode(encoder).strip().split("\n")
    is_correct_list = []
    wrong_list = []
    for _divided_name in tqdm(divided_name_text):
        _undivided_name = _divided_name.replace(separator, "")
        _divided_name_pred = str(name_divider.divide_name(_undivided_name))
        is_correct = (_divided_name == _divided_name_pred)
        is_correct_list.append(is_correct)
        if not is_correct:
            wrong_list.append(f"True: {_divided_name}, Pred: {_divided_name_pred}")
    print(f"{sum(is_correct_list) / len(is_correct_list):.03}")
    if len(wrong_list) != 0:
        print("\n".join(wrong_list))


if __name__ == '__main__':
    cmd()