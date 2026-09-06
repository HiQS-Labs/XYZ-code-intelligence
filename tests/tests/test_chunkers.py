"""Contract tests for repository walking and source chunking."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from xyz.ingest import chunk_file, chunk_repo, walk_repo


FIXTURE = Path(__file__).parent / "fixtures" / "mini-repo"


def _copy_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "mini-repo"
    shutil.copytree(FIXTURE, root)
    (root / "binary.py").write_bytes(b"print('before nul')\0ignored")
    (root / "long.txt").write_text("x" * 6001, encoding="utf-8")
    (root / "docs" / "long.md").write_text("# Long\n\n" + "word " * 1400, encoding="utf-8")
    return root


def test_walk_filters_and_is_deterministic(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    first_errors: list[str] = []
    second_errors: list[str] = []
    first = list(walk_repo(root, errors=first_errors))
    second = list(walk_repo(root, errors=second_errors))

    assert first == second
    assert first_errors == second_errors == []
    paths = [path for path, _ in first]
    assert paths == sorted(paths)
    assert "config.yml" in paths
    assert "Dockerfile" in paths
    assert "binary.py" not in paths
    assert "node_modules/ignored.js" not in paths


def test_include_prefixes_keep_root_relative_paths(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    errors: list[str] = []
    paths = [path for path, _ in walk_repo(root, include_prefixes=("app/",), errors=errors)]
    assert paths == ["app/example.php", "app/example.py", "app/example.ts"]
    assert errors == []


def test_missing_root_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        list(walk_repo(tmp_path / "missing", errors=[]))


def test_python_chunks_and_lines() -> None:
    path = FIXTURE / "app" / "example.py"
    result = chunk_file("mini", "app/example.py", path.read_bytes())
    by_name = {chunk.qualified_name: chunk for chunk in result.chunks}

    assert set(by_name) == {"app/example.py", "alpha", "beta", "Worker", "Worker.run", "Worker.stop"}
    assert by_name["alpha"].kind == "function"
    assert (by_name["alpha"].start_line, by_name["alpha"].end_line) == (6, 7)
    assert (by_name["Worker.run"].start_line, by_name["Worker.run"].end_line) == (17, 18)
    assert by_name["app/example.py"].kind == "module"
    assert by_name["app/example.py"].start_line == 1
    assert by_name["app/example.py"].end_line == 3
    assert result.warnings == []


def test_typescript_and_php_chunks() -> None:
    ts = chunk_file("mini", "app/example.ts", (FIXTURE / "app" / "example.ts").read_bytes())
    php = chunk_file("mini", "app/example.php", (FIXTURE / "app" / "example.php").read_bytes())

    assert {chunk.qualified_name for chunk in ts.chunks} == {"greet", "Greeter", "Greeter.greet"}
    assert {chunk.qualified_name for chunk in php.chunks} == {"app/example.php", "Greeter", "Greeter.greet"}
    ts_method = next(chunk for chunk in ts.chunks if chunk.qualified_name == "Greeter.greet")
    php_method = next(chunk for chunk in php.chunks if chunk.qualified_name == "Greeter.greet")
    assert (ts_method.start_line, ts_method.end_line) == (6, 8)
    assert (php_method.start_line, php_method.end_line) == (4, 6)


def test_markdown_sections_and_file_chunks() -> None:
    markdown = chunk_file("mini", "docs/guide.md", (FIXTURE / "docs" / "guide.md").read_bytes())
    assert [chunk.qualified_name for chunk in markdown.chunks] == [
        "docs/guide.md",
        "Guide",
        "Guide > Install",
        "Guide > Install > Options",
    ]
    assert [(chunk.start_line, chunk.end_line) for chunk in markdown.chunks] == [
        (1, 1),
        (3, 5),
        (7, 9),
        (11, 13),
    ]

    yaml = chunk_file("mini", "config.yml", (FIXTURE / "config.yml").read_bytes())
    docker = chunk_file("mini", "Dockerfile", (FIXTURE / "Dockerfile").read_bytes())
    assert len(yaml.chunks) == len(docker.chunks) == 1
    assert yaml.chunks[0].kind == docker.chunks[0].kind == "file"


def test_all_embedded_text_is_path_prefixed_and_hashed(tmp_path: Path) -> None:
    result = chunk_repo("mini", _copy_fixture(tmp_path))
    assert result.chunks
    for chunk in result.chunks:
        assert chunk.embedded_text.startswith(chunk.path + "\n\n")
        assert len(chunk.content_sha) == 64


def test_oversize_single_line_and_markdown_split(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    single = chunk_file("mini", "long.txt", (root / "long.txt").read_bytes()).chunks
    markdown = chunk_file("mini", "docs/long.md", (root / "docs" / "long.md").read_bytes()).chunks

    assert len(single) >= 2
    assert [chunk.qualified_name for chunk in single][:2] == ["long.txt", "long.txt#2"]
    assert len(single[0].text) == 6000
    assert single[0].text[-150:] == single[1].text[:150]
    assert len(markdown) >= 2
    assert [chunk.qualified_name for chunk in markdown][:2] == ["Long", "Long#2"]
    assert all(len(chunk.text) <= 6000 for chunk in single + markdown)
    assert all(chunk.start_line <= chunk.end_line for chunk in single + markdown)


def test_broken_parse_falls_back_with_warning() -> None:
    result = chunk_file("mini", "broken.py", (FIXTURE / "broken.py").read_bytes())
    assert len(result.chunks) == 1
    assert result.chunks[0].kind == "file"
    assert result.chunks[0].qualified_name == "broken.py"
    assert len(result.warnings) == 1
    assert "broken.py" in result.warnings[0]


def test_scandir_error_is_recorded_after_other_yields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "a.py").write_text("VALUE = 1\n", encoding="utf-8")
    blocked = root / "blocked"
    blocked.mkdir()
    (blocked / "hidden.py").write_text("VALUE = 2\n", encoding="utf-8")
    (root / "node_modules").mkdir()
    (root / "node_modules" / "ignored.py").write_text("VALUE = 3\n", encoding="utf-8")
    (root / "binary.py").write_bytes(b"ok\0binary")

    real_scandir = os.scandir

    def guarded_scandir(path: str | os.PathLike[str]):
        if Path(path) == blocked:
            raise PermissionError("blocked for test")
        return real_scandir(path)

    monkeypatch.setattr(os, "scandir", guarded_scandir)
    errors: list[str] = []
    iterator = walk_repo(root, errors=errors)
    assert next(iterator)[0] == "a.py"
    assert list(iterator) == []
    assert len(errors) == 1
    assert "blocked" in errors[0]


def test_chunk_repo_is_deterministic(tmp_path: Path) -> None:
    root = _copy_fixture(tmp_path)
    assert chunk_repo("mini", root) == chunk_repo("mini", root)
