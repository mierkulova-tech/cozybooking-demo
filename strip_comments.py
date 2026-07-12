#!/usr/bin/env python3
"""
strip_comments.py

Убирает # -комментарии из Python-кода, не трогая:
  - строки/докстроки (даже если внутри есть символ #)
  - шебанг-строку (#!/usr/bin/env python) в самом начале файла
  - сам код

Используется как git clean-фильтр: читает исходник из stdin,
пишет "очищенную" версию в stdout. git вызывает это ТОЛЬКО в момент
git add / commit — файл в рабочей папке при этом не меняется.

Запуск вручную (для проверки):
    python strip_comments.py < apartment.py
"""

import sys
import io
import tokenize
import ast


def strip_docstrings(source: str) -> str:
    # ------------------------------------------------------------------
    # Удаляет докстринги (строки в """ / ''' в начале модуля/класса/
    # функции). Если докстринг был ЕДИНСТВЕННЫМ содержимым функции
    # или класса — на его место ставим "pass", иначе код будет
    # синтаксически невалидным (пустое тело def/class запрещено).
    # ------------------------------------------------------------------
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)

    to_delete = set()
    insertions = {}
    # ^ строка (0-индекс) -> текст "pass", который нужно вставить
    # ПЕРЕД удалением докстринга, если тело иначе станет пустым

    # ВАЖНО: проверяем ТОЛЬКО эти типы узлов. У ast.Lambda и ast.IfExp
    # тоже есть атрибут .body, но это ОДНО выражение, а не список
    # statement'ов — из-за этого раньше падало с TypeError на лямбдах.
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

        # если это был единственный statement в def/class (не в модуле
        # целиком — пустой файл это нормально) — нужен pass
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
    # ^ строки, которые ПОЛНОСТЬЮ состоят из комментария —
    # их удаляем целиком, а не оставляем пустыми (меньше мусора)

    tokens = tokenize.generate_tokens(io.StringIO(source).readline)

    for tok in tokens:
        if tok.type != tokenize.COMMENT:
            continue

        srow, scol = tok.start

        # шебанг в самой первой строке — не трогаем
        if srow == 1 and lines[0].startswith("#!"):
            continue

        line = lines[srow - 1]
        before_comment = line[:scol]

        if before_comment.strip() == "":
            # строка ЦЕЛИКОМ была комментарием -> удаляем строку
            lines_to_delete.add(srow - 1)
        else:
            # комментарий ПОСЛЕ кода на той же строке -> обрезаем
            # только хвост, код и перевод строки оставляем
            newline = ""
            if line.endswith("\r\n"):
                newline = "\r\n"
            elif line.endswith("\n"):
                newline = "\n"
            lines[srow - 1] = before_comment.rstrip() + newline

    result_lines = [
        line for i, line in enumerate(lines) if i not in lines_to_delete
    ]
    return "".join(result_lines)


def strip_all(source: str) -> str:
    # сначала докстринги (нужен рабочий ast.parse -> должен идти
    # ДО удаления # -комментариев, чтобы не путать номера строк)
    source = strip_docstrings(source)
    source = strip_hash_comments(source)
    return source


def main() -> None:
    args = sys.argv[1:]

    if not args:
        # РЕЖИМ 1: git-фильтр — читаем из stdin, пишем в stdout
        source = sys.stdin.buffer.read().decode("utf-8")
        cleaned = strip_all(source)
        sys.stdout.buffer.write(cleaned.encode("utf-8"))
        return

    # РЕЖИМ 2: ручная чистка конкретных файлов (перезаписывает их!)
    # пример: python strip_comments.py apartment.py address.py
    for path in args:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        cleaned = strip_all(source)
        with open(path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"Очищено: {path}")


if __name__ == "__main__":
    main()
