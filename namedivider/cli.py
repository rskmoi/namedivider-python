import click
from tqdm import tqdm
from pathlib import Path
from namedivider.name_divider import NameDivider
CURRENT_DIR = Path(__file__).resolve().parent


@click.group()
def cmd():
    pass


@cmd.command()
@click.argument("undivided_name")
@click.option("--separator", "-s", default=" ")
def name(undivided_name: str, separator: str):
    """
    Divides an undivided name.
    :param undivided_name: Undivided name
    :param separator: Separator between family name and given name
    """
    name_divider = NameDivider(path_csv=Path(CURRENT_DIR) / "assets/kanji.csv", separator=separator)
    print(name_divider.divide_name(undivided_name))


@cmd.command()
@click.argument("undivided_name_text")
@click.option("--separator", "-s", default=" ")
@click.option("--encoding", "-e", default="utf-8")
def file(undivided_name_text, separator, encoding):
    """
    Divides names in text file.
    The text file must have one name per line.
    Text file example:
    ```
    原敬
    菅義偉
    阿部晋三
    中曽根康弘
    ```
    :param undivided_name_text: File path of text file
    :param separator: Separator between family name and given name
    :param encoder: Encoding of text file
    :return:
    Prints divided result.
    ```
    100%|███████████████████████████████████████████| 4/4 [00:00<00:00, 4194.30it/s]
    原 敬
    菅 義偉
    阿部 晋三
    中曽根 康弘
    ```
    """
    name_divider = NameDivider(path_csv=Path(CURRENT_DIR) / "assets/kanji.csv", separator=separator)
    with open(undivided_name_text, "rb") as f:
        undivided_names = f.read().decode(encoding).strip().split("\n")
    divided_names = []
    for _undivided_name in tqdm(undivided_names):
        divided_names.append(str(name_divider.divide_name(_undivided_name)))
    print("\n".join(divided_names))


@cmd.command()
@click.argument("divided_name_text")
@click.option("--separator", "-s", default=" ")
@click.option("--encoder", "-e", default="utf-8")
def accuracy(divided_name_text, separator, encoder):
    """
    Check the accuracy of this tool.
    The text file must have one name per line, and name must be divided py separator.
    Text file example:
    ```
    原 敬
    菅 義偉
    阿部 晋三
    中曽根 康弘
    滝 登喜男
    ```
    :param divided_name_text: File path of text file
    :param separator: Separator between family name and given name
    :param encoder: Encoding of text file
    :return:
    Prints accuracy and missed name.
    ```
    100%|███████████████████████████████████████████| 5/5 [00:00<00:00, 3673.41it/s]
    0.8
    True: 滝 登喜男, Pred: 滝登 喜男
    ```
    """
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
