from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from namedivider import cli

runner = CliRunner()


@pytest.fixture
def divider(monkeypatch):
    divider = Mock()
    divider.divide_name.side_effect = lambda name: name[0] + "|" + name[1:]
    factory = Mock(return_value=divider)
    monkeypatch.setattr(cli, "get_divider", factory)
    ticks = iter([10.0, 12.0])
    monkeypatch.setattr(cli.time, "time", lambda: next(ticks))
    return divider, factory


@pytest.mark.parametrize("command", ["file", "accuracy", "benchmark"])
@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("trailing_newline", [False, True])
@pytest.mark.parametrize("encoding", ["utf-8", "cp932"])
def test_input_lines(tmp_path, divider, command, newline, trailing_newline, encoding):
    names = ["原|敬", "林|洋"] if command == "accuracy" else ["原敬", "林洋"]
    lines = ["", names[0], "", " \t　", names[1]]
    content = newline.join(lines) + (newline if trailing_newline else "")
    path = tmp_path / "names.txt"
    path.write_bytes(content.encode(encoding))
    result = runner.invoke(cli.app, [command, str(path), "--encoding", encoding, "--separator", "|"])
    assert result.exit_code == 0, result.output
    assert [call.args[0] for call in divider[0].divide_name.call_args_list] == ["原敬", "林洋"]
    assert divider[1].call_args.kwargs["separator"] == "|"
    if command == "file":
        assert result.stdout.splitlines()[-2:] == ["原|敬", "林|洋"]
    elif command == "accuracy":
        assert result.stdout.strip() == "1.0"
    else:
        assert "Processed 2 names in 2.0000s (1.0 names/sec)" in result.stdout


@pytest.mark.parametrize("command", ["file", "accuracy", "benchmark"])
@pytest.mark.parametrize("content", [b"", b"\n\n", b"\r\n\r\n", " \t　\r\n".encode()])
def test_empty_input(tmp_path, divider, command, content):
    path = tmp_path / "empty.txt"
    path.write_bytes(content)
    result = runner.invoke(cli.app, [command, str(path)])
    assert result.exit_code == 0
    assert result.output == ""
    divider[1].assert_not_called()


@pytest.mark.parametrize("command", ["file", "accuracy", "benchmark"])
def test_name_whitespace_is_preserved(tmp_path, divider, command):
    path = tmp_path / "names.txt"
    path.write_bytes(" 原 敬 \r\n\t林洋　".encode())
    result = runner.invoke(cli.app, [command, str(path), "--separator", "|"])
    assert result.exit_code == 0, result.output
    assert [call.args[0] for call in divider[0].divide_name.call_args_list] == [" 原 敬 ", "\t林洋　"]


def test_benchmark_silent(tmp_path, divider):
    path = tmp_path / "names.txt"
    path.write_bytes("原敬\r\n\r\n".encode())
    result = runner.invoke(cli.app, ["benchmark", str(path), "--silent"])
    assert result.exit_code == 0
    assert result.stdout == ""
    divider[0].divide_name.assert_called_once_with("原敬")
