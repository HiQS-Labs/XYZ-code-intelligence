"""Smoke tests for the initial package scaffold."""

import xyz
from xyz.cli import main


def test_version() -> None:
    assert xyz.__version__ == "0.5.0.dev0"


def test_cli_without_arguments(capsys: object) -> None:
    assert main([]) == 0


def test_cli_version(capsys: object) -> None:
    assert main(["--version"]) == 0


def test_cli_unknown_subcommand(capsys: object) -> None:
    assert main(["bogus"]) == 2
