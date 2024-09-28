from pathlib import Path

import typer

from namedivider.divider.basic_name_divider import BasicNameDivider
from namedivider.divider.config import BasicNameDividerConfig, GBDTNameDividerConfig
from namedivider.divider.gbdt_name_divider import GBDTNameDivider
from namedivider.divider.name_divider_base import _NameDivider

CURRENT_DIR = Path(__file__).resolve().parent

app = typer.Typer()


def get_divider(mode: str, separator: str) -> _NameDivider:
    if mode == "basic":
        basic_config = BasicNameDividerConfig(separator=separator)
        return BasicNameDivider(config=basic_config)
    elif mode == "gbdt":
        gbdt_config = GBDTNameDividerConfig(separator=separator)
        return GBDTNameDivider(config=gbdt_config)
    else:
        raise ValueError(f"Mode must be in [basic, gbdt], but got {mode}")


@app.command()
def name(
    undivided_name: str = typer.Argument(..., help="Undivided name"),
    separator: str = typer.Option(" ", "--separator", "-s", help="Separator between family name and given name"),
    mode: str = typer.Option("basic", "--mode", "-m", help="Divider Mode. You can choice basic or gbdt."),
) -> None:
    """
    Divides an undivided name.
    :param undivided_name: Undivided name
    :param separator: Separator between family name and given name
    """
    divider = get_divider(mode=mode, separator=separator)
    print(divider.divide_name(undivided_name))


@app.command()
def file(
    undivided_name_text: Path = typer.Argument(
        ..., help="File path of text file", exists=True, dir_okay=False, readable=True
    ),
    separator: str = typer.Option(" ", "--separator", "-s", help="Separator between family name and given name"),
    mode: str = typer.Option("basic", "--mode", "-m", help="Divider Mode. You can choice basic or gbdt."),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="Encoding of text file"),
) -> None:
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
    :param encoding: Encoding of text file
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
    divider = get_divider(mode=mode, separator=separator)
    with open(undivided_name_text, "rb") as f:
        undivided_names = f.read().decode(encoding).strip().split("\n")
    divided_names = []
    with typer.progressbar(undivided_names) as bar:
        for _undivided_name in bar:
            divided_names.append(str(divider.divide_name(_undivided_name)))
    print("\n".join(divided_names))


@app.command()
def accuracy(
    divided_name_text: Path = typer.Argument(
        ..., help="File path of text file", exists=True, dir_okay=False, readable=True
    ),
    separator: str = typer.Option(" ", "--separator", "-s", help="Separator between family name and given name"),
    mode: str = typer.Option("basic", "--mode", "-m", help="Divider Mode. You can choice basic or gbdt."),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="Encoding of text file"),
) -> None:
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
    :param encoding: Encoding of text file
    :return:
    Prints accuracy and missed name.
    ```
    100%|███████████████████████████████████████████| 5/5 [00:00<00:00, 3673.41it/s]
    0.8
    True: 滝 登喜男, Pred: 滝登 喜男
    ```
    """
    divider = get_divider(mode=mode, separator=separator)
    with open(divided_name_text, "rb") as f:
        divided_names = f.read().decode(encoding).strip().split("\n")
    is_correct_list = []
    wrong_list = []
    with typer.progressbar(divided_names) as bar:
        for _divided_name in bar:
            _undivided_name = _divided_name.replace(separator, "")
            _divided_name_pred = str(divider.divide_name(_undivided_name))
            is_correct = _divided_name == _divided_name_pred
            is_correct_list.append(is_correct)
            if not is_correct:
                wrong_list.append(f"True: {_divided_name}, Pred: {_divided_name_pred}")
    print(f"{sum(is_correct_list) / len(is_correct_list):.04}")
    if len(wrong_list) != 0:
        print("\n".join(wrong_list))


if __name__ == "__main__":
    app()
