import time
from pathlib import Path

import typer

from namedivider.divider.basic_name_divider import BasicNameDivider
from namedivider.divider.config import BasicNameDividerConfig, GBDTNameDividerConfig
from namedivider.divider.gbdt_name_divider import GBDTNameDivider
from namedivider.divider.name_divider_base import _NameDivider

CURRENT_DIR = Path(__file__).resolve().parent

app = typer.Typer()


def get_divider(mode: str, separator: str, use_mask_cache: bool = False, backend: str = "python") -> _NameDivider:
    if mode == "basic":
        basic_config = BasicNameDividerConfig(separator=separator, cache_mask=use_mask_cache, backend=backend)
        return BasicNameDivider(config=basic_config)
    elif mode == "gbdt":
        gbdt_config = GBDTNameDividerConfig(separator=separator, cache_mask=use_mask_cache, backend=backend)
        return GBDTNameDivider(config=gbdt_config)
    else:
        raise ValueError(f"Mode must be in [basic, gbdt], but got {mode}")


@app.command()
def name(
    undivided_name: str = typer.Argument(..., help="Undivided name"),
    separator: str = typer.Option(" ", "--separator", "-s", help="Separator between family name and given name"),
    mode: str = typer.Option("basic", "--mode", "-m", help="Divider Mode. You can choice basic or gbdt."),
    backend: str = typer.Option("python", "--backend", "-b", help="Backend to use. python (default) or rust (beta)."),
) -> None:
    """
    Divides an undivided name.
    :param undivided_name: Undivided name
    :param separator: Separator between family name and given name
    :param backend: Backend to use (python or rust)
    """
    divider = get_divider(mode=mode, separator=separator, backend=backend)
    print(divider.divide_name(undivided_name))


@app.command()
def file(
    undivided_name_text: Path = typer.Argument(
        ..., help="File path of text file", exists=True, dir_okay=False, readable=True
    ),
    separator: str = typer.Option(" ", "--separator", "-s", help="Separator between family name and given name"),
    mode: str = typer.Option("basic", "--mode", "-m", help="Divider Mode. You can choice basic or gbdt."),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="Encoding of text file"),
    backend: str = typer.Option("python", "--backend", "-b", help="Backend to use. python (default) or rust (beta)."),
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
    divider = get_divider(mode=mode, separator=separator, backend=backend)
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
    backend: str = typer.Option("python", "--backend", "-b", help="Backend to use. python (default) or rust (beta)."),
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
    divider = get_divider(mode=mode, separator=separator, backend=backend)
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


@app.command()
def benchmark(
    undivided_name_text: Path = typer.Argument(
        ..., help="File path of text file", exists=True, dir_okay=False, readable=True
    ),
    separator: str = typer.Option(" ", "--separator", "-s", help="Separator between family name and given name"),
    mode: str = typer.Option("basic", "--mode", "-m", help="Divider Mode. You can choice basic or gbdt."),
    encoding: str = typer.Option("utf-8", "--encoding", "-e", help="Encoding of text file"),
    silent: bool = typer.Option(False, "--silent", help="Suppress output for benchmarking"),
    use_mask_cache: bool = typer.Option(True, "--use-mask-cache/--no-mask-cache", help="Enable or disable mask cache"),
    backend: str = typer.Option("python", "--backend", "-b", help="Backend to use. python (default) or rust (beta)."),
) -> None:
    """
    Benchmark the performance of name division on a file (single run).
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
    :param mode: Divider Mode. You can choice basic or gbdt.
    :param encoding: Encoding of text file
    :param silent: Suppress output for benchmarking
    :param use_mask_cache: Enable or disable mask cache
    :return:
    Processes all names and reports timing.
    ```
    Processed 4 names in 0.0123s (325.2 names/sec) [cache enabled]
    ```
    """
    divider = get_divider(mode=mode, separator=separator, use_mask_cache=use_mask_cache, backend=backend)

    with open(undivided_name_text, "rb") as f:
        undivided_names = f.read().decode(encoding).strip().split("\n")

    name_count = len(undivided_names)

    start_time = time.time()
    for _undivided_name in undivided_names:
        divider.divide_name(_undivided_name)
    end_time = time.time()

    elapsed = end_time - start_time
    names_per_sec = name_count / elapsed if elapsed > 0 else float("inf")

    if not silent:
        cache_status = "enabled" if use_mask_cache else "disabled"
        print(
            f"Processed {name_count} names in {elapsed:.4f}s ({names_per_sec:.1f} names/sec) [cache {cache_status}, backend {backend}]"
        )


if __name__ == "__main__":
    app()
