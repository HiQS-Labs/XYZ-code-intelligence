"""Language-aware source chunking with deterministic hard bounds."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from tree_sitter import Node
from tree_sitter_language_pack import get_parser


MAX_CHARS = 6000
SPLIT_SEARCH_CHARS = 1500
SPLIT_OVERLAP_CHARS = 150


@dataclass(frozen=True)
class Chunk:
    repo: str
    path: str
    kind: str
    qualified_name: str
    start_line: int
    end_line: int
    text: str
    embedded_text: str
    content_sha: str


@dataclass(frozen=True)
class ChunkResult:
    chunks: list[Chunk]
    warnings: list[str]


@dataclass(frozen=True)
class _Draft:
    kind: str
    qualified_name: str
    text: str
    line_map: tuple[int, ...]


_LANGUAGES = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".php": "php",
}

_TOP_LEVEL_TYPES = {
    "python": {"function_definition": "function", "class_definition": "class"},
    "javascript": {"function_declaration": "function", "class_declaration": "class"},
    "typescript": {"function_declaration": "function", "class_declaration": "class"},
    "tsx": {"function_declaration": "function", "class_declaration": "class"},
    "php": {"function_definition": "function", "class_declaration": "class"},
}


def _line_map(text: str, start_line: int) -> tuple[int, ...]:
    line = start_line
    result: list[int] = []
    for char in text:
        result.append(line)
        if char == "\n":
            line += 1
    return tuple(result)


def _line_at(source: bytes, byte_offset: int) -> int:
    """Return a one-based line without trusting parser point metadata."""
    return source[:byte_offset].count(b"\n") + 1


def _draft(kind: str, qualified_name: str, text: str, start_line: int) -> _Draft:
    return _Draft(kind, qualified_name, text, _line_map(text, start_line))


def _trim(text: str, line_map: tuple[int, ...]) -> tuple[str, tuple[int, ...]]:
    left = len(text) - len(text.lstrip())
    right = len(text.rstrip())
    return text[left:right], line_map[left:right]


def _node_name(node: Node) -> str | None:
    name = node.child_by_field_name("name")
    if name is None:
        return None
    return name.text.decode("utf-8", errors="replace")


def _unwrap_definition(node: Node, language: str) -> Node | None:
    wanted = _TOP_LEVEL_TYPES[language]
    if node.type in wanted:
        return node
    if node.type in {"decorated_definition", "export_statement"}:
        return next((child for child in node.named_children if child.type in wanted), None)
    return None


def _method_nodes(class_node: Node, language: str) -> list[Node]:
    if language == "python":
        body = class_node.child_by_field_name("body")
        method_type = "function_definition"
        wrappers = {"decorated_definition"}
    elif language == "php":
        body = class_node.child_by_field_name("body")
        if body is None:
            body = next((child for child in class_node.named_children if child.type == "declaration_list"), None)
        method_type = "method_declaration"
        wrappers = set()
    else:
        body = class_node.child_by_field_name("body")
        method_type = "method_definition"
        wrappers = set()
    if body is None:
        return []

    methods: list[Node] = []
    for child in body.named_children:
        if child.type == method_type:
            methods.append(child)
        elif child.type in wrappers:
            wrapped = next((item for item in child.named_children if item.type == method_type), None)
            if wrapped is not None:
                methods.append(child)
    return methods


def _ast_drafts(rel_path: str, source: bytes, language: str) -> list[_Draft]:
    tree = get_parser(language).parse(source)
    if tree.root_node.has_error:
        raise ValueError("syntax tree contains parse errors")

    drafts: list[_Draft] = []
    occupied: list[tuple[int, int]] = []
    for outer in tree.root_node.named_children:
        definition = _unwrap_definition(outer, language)
        if definition is None:
            continue
        name = _node_name(definition)
        if not name:
            continue
        kind = _TOP_LEVEL_TYPES[language][definition.type]
        text = source[outer.start_byte : outer.end_byte].decode("utf-8", errors="replace")
        drafts.append(_draft(kind, name, text, _line_at(source, outer.start_byte)))
        occupied.append((outer.start_byte, outer.end_byte))

        if kind == "class":
            for method in _method_nodes(definition, language):
                method_definition = method
                if method.type == "decorated_definition":
                    method_definition = next(
                        child for child in method.named_children if child.type == "function_definition"
                    )
                method_name = _node_name(method_definition)
                if method_name:
                    method_text = source[method.start_byte : method.end_byte].decode(
                        "utf-8", errors="replace"
                    )
                    drafts.append(
                        _draft(
                            "method",
                            f"{name}.{method_name}",
                            method_text,
                            _line_at(source, method.start_byte),
                        )
                    )

    residual_parts: list[tuple[str, tuple[int, ...]]] = []
    cursor = 0
    for start, end in sorted(occupied):
        if start > cursor:
            raw = source[cursor:start].decode("utf-8", errors="replace")
            mapped = _line_map(raw, _line_at(source, cursor))
            part = _trim(raw, mapped)
            if part[0]:
                residual_parts.append(part)
        cursor = max(cursor, end)
    if cursor < len(source):
        raw = source[cursor:].decode("utf-8", errors="replace")
        mapped = _line_map(raw, _line_at(source, cursor))
        part = _trim(raw, mapped)
        if part[0]:
            residual_parts.append(part)

    if residual_parts:
        text_bits: list[str] = []
        map_bits: list[int] = []
        for index, (text, mapped) in enumerate(residual_parts):
            if index:
                marker_line = map_bits[-1] if map_bits else mapped[0]
                marker = "\n# …\n"
                text_bits.append(marker)
                map_bits.extend([marker_line] * len(marker))
            text_bits.append(text)
            map_bits.extend(mapped)
        drafts.append(_Draft("module", rel_path, "".join(text_bits), tuple(map_bits)))

    drafts.sort(key=lambda item: (item.line_map[0], {"module": 0, "class": 1, "function": 1, "method": 2}.get(item.kind, 3), item.qualified_name))
    return drafts


_HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*#*\s*$")


def _markdown_drafts(rel_path: str, text: str) -> list[_Draft]:
    lines = text.splitlines(keepends=True)
    headings: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = _HEADING.match(line.rstrip("\r\n"))
        if match:
            headings.append((index, len(match.group(1)), match.group(2).strip()))

    boundaries = [item[0] for item in headings]
    drafts: list[_Draft] = []
    if not headings:
        body = text.rstrip()
        return [_draft("file", rel_path, body, 1)] if body else []

    first_heading = headings[0][0]
    if first_heading:
        preamble = "".join(lines[:first_heading]).rstrip()
        if preamble:
            drafts.append(_draft("preamble", rel_path, preamble, 1))

    path: list[str] = []
    for position, (start, level, title) in enumerate(headings):
        path = path[: level - 1]
        path.append(title)
        end = boundaries[position + 1] if position + 1 < len(boundaries) else len(lines)
        body = "".join(lines[start:end]).rstrip()
        if body:
            drafts.append(_draft("section", " > ".join(path), body, start + 1))
    return drafts


def _file_drafts(rel_path: str, text: str) -> list[_Draft]:
    body = text.rstrip()
    return [_draft("file", rel_path, body, 1)] if body else []


def _split_draft(draft: _Draft) -> list[_Draft]:
    if len(draft.text) <= MAX_CHARS:
        return [draft]

    result: list[_Draft] = []
    start = 0
    part_number = 1
    while len(draft.text) - start > MAX_CHARS:
        limit = start + MAX_CHARS
        blank = draft.text.rfind("\n\n", limit - SPLIT_SEARCH_CHARS, limit)
        cut = blank + 2 if blank >= start else limit
        name = draft.qualified_name if part_number == 1 else f"{draft.qualified_name}#{part_number}"
        result.append(_Draft(draft.kind, name, draft.text[start:cut], draft.line_map[start:cut]))
        next_start = max(cut - SPLIT_OVERLAP_CHARS, start + 1)
        start = next_start
        part_number += 1
    name = draft.qualified_name if part_number == 1 else f"{draft.qualified_name}#{part_number}"
    result.append(_Draft(draft.kind, name, draft.text[start:], draft.line_map[start:]))
    return result


def _materialise(repo: str, rel_path: str, draft: _Draft) -> Chunk:
    embedded_text = f"{rel_path}\n\n{draft.text}"
    non_newline = [line for char, line in zip(draft.text, draft.line_map) if char not in "\r\n"]
    start_line = non_newline[0] if non_newline else draft.line_map[0]
    end_line = non_newline[-1] if non_newline else draft.line_map[-1]
    return Chunk(
        repo=repo,
        path=rel_path,
        kind=draft.kind,
        qualified_name=draft.qualified_name,
        start_line=start_line,
        end_line=end_line,
        text=draft.text,
        embedded_text=embedded_text,
        content_sha=hashlib.sha256(embedded_text.encode("utf-8")).hexdigest(),
    )


def chunk_file(repo: str, rel_path: str, source: bytes) -> ChunkResult:
    """Chunk one source file, falling back to file chunks after parse errors."""

    rel_path = rel_path.replace("\\", "/")
    suffix = PurePosixPath(rel_path).suffix.lower()
    text = source.decode("utf-8", errors="replace")
    warnings: list[str] = []

    if suffix in _LANGUAGES:
        try:
            drafts = _ast_drafts(rel_path, source, _LANGUAGES[suffix])
        except Exception as exc:
            warnings.append(f"{rel_path}: parse failed; used file chunker ({type(exc).__name__}: {exc})")
            drafts = _file_drafts(rel_path, text)
    elif suffix in {".md", ".markdown"}:
        drafts = _markdown_drafts(rel_path, text)
    else:
        drafts = _file_drafts(rel_path, text)

    chunks = [
        _materialise(repo, rel_path, part)
        for draft in drafts
        for part in _split_draft(draft)
        if part.text
    ]
    return ChunkResult(chunks, warnings)
