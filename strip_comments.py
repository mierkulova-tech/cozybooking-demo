#!/usr/bin/env python3

import sys
import io
import tokenize
import ast


def strip_docstrings(source: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)

    to_delete = set()
    insertions = {}

    DOCSTRING_HOLDERS = (
        ast.Module,
        ast.ClassDef,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
    )

    for node in ast.walk(tree):
        if not isinstance(node, DOCSTRING_HOLDERS):
            continue

        body = node.body
        if not body:
            continue

        first = body[0]
        is_docstring = (
            isinstance(first, ast.Expr)
            and isinstance(getattr(first, "value", None), ast.Constant)
            and isinstance(first.value.value, str)
        )
        if not is_docstring:
            continue

        start = first.lineno - 1
        end = first.end_lineno - 1
        for i in range(start, end + 1):
            to_delete.add(i)

        if len(body) == 1 and not isinstance(node, ast.Module):
            indent = " " * first.col_offset
            insertions[start] = indent + "pass\n"

    result = []
    for i, line in enumerate(lines):
        if i in insertions:
            result.append(insertions[i])
        if i not in to_delete:
            result.append(line)

    return "".join(result)


def strip_hash_comments(source: str) -> str:
    lines = source.splitlines(keepends=True)
    lines_to_delete = set()

    tokens = tokenize.generate_tokens(io.StringIO(source).readline)

    for tok in tokens:
        if tok.type != tokenize.COMMENT:
            continue

        srow, scol = tok.start

        if srow == 1 and lines[0].startswith("#!"):
            continue

        line = lines[srow - 1]
        before_comment = line[:scol]

        if before_comment.strip() == "":
            lines_to_delete.add(srow - 1)
        else:
            newline = ""
            if line.endswith("\r\n"):
                newline = "\r\n"
            elif line.endswith("\n"):
                newline = "\n"
            lines[srow - 1] = before_comment.rstrip() + newline

    result_lines = [line for i, line in enumerate(lines) if i not in lines_to_delete]
    return "".join(result_lines)


def strip_all(source: str) -> str:
    source = strip_docstrings(source)
    source = strip_hash_comments(source)
    return source


def main() -> None:
    args = sys.argv[1:]

    if not args:
        source = sys.stdin.buffer.read().decode("utf-8")
        cleaned = strip_all(source)
        sys.stdout.buffer.write(cleaned.encode("utf-8"))
        return

    for path in args:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        cleaned = strip_all(source)
        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"Очищено: {path}")


if __name__ == "__main__":
    main()
