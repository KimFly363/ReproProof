"""Helpers around Python AST inspection."""
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CallInfo:
    name: str
    line: int
    node: ast.Call
    assigned_to: str | None = None


def parse_python(text: str, filename: str = "<unknown>") -> ast.AST | None:
    try:
        return ast.parse(text, filename=filename)
    except SyntaxError:
        return None


def dotted_name(node: ast.AST | None) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    if isinstance(node, ast.Call):
        return dotted_name(node.func)
    return ""


def string_literal(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def assigned_name(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, (ast.Tuple, ast.List)) and node.elts:
        names = [assigned_name(element) for element in node.elts]
        return ",".join(name for name in names if name) or None
    return None


def iter_calls(tree: ast.AST) -> Iterable[CallInfo]:
    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        assigned = None
        parent = parents.get(node)
        if isinstance(parent, ast.Assign):
            assigned = assigned_name(parent.targets[0] if parent.targets else None)
        yield CallInfo(name=dotted_name(node.func), line=getattr(node, "lineno", 0), node=node, assigned_to=assigned)


def expr_names(expr: ast.AST | None) -> set[str]:
    if expr is None:
        return set()
    return {node.id for node in ast.walk(expr) if isinstance(node, ast.Name)}
