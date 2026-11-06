#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""统计 Java 源码与 res 资源。结构数字来自 javalang 0.13.0，行数字来自本文件里的扫描器。

行口径
    wc_newlines
        文件中字符 '\\n' 的个数。以换行结尾时等于 GNU wc -l。
    logical_lines
        读者看到的行数。若文件非空且最后一行没有换行，比 wc_newlines 多 1。
        本仓库只有 DateTimePickerDialog.java 属于这种情况（基线核对时）。
    blank_lines
        logical 行去掉空白后为空，且该行不在块注释内部。
    comment_lines
        去掉字符串、字符字面量之后，该行剩余的非空白内容全部在 // 或 /* */ 中。
        字符串里的注释符号不计。同一行既有代码又有行尾注释时，整行算 code_lines。
    code_lines
        logical_lines - blank_lines - comment_lines。

结构口径
    使用 javalang 语法树，不手写方法名正则。
    types_named
        class、interface、enum，含内部具名类型，不含匿名类。
    types_top_level
        编译单元直接声明的类型。
    methods_named_types
        具名类型体内直接声明的 MethodDeclaration，不含构造方法，
        也不含匿名类里的方法。
    methods_anonymous
        出现在 ClassCreator（匿名类）里的 MethodDeclaration。
    constructors
        具名类型的 ConstructorDeclaration。
    匿名类方法的 declaring_type 写成「外层具名类型#anonymous」。

本脚本不填写业务释义。类职责见 class-responsibility.csv（手工）。
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import javalang
from javalang.tree import (
    ClassDeclaration,
    ConstructorDeclaration,
    EnumDeclaration,
    InterfaceDeclaration,
    MethodDeclaration,
)

TYPE_NODES = (ClassDeclaration, InterfaceDeclaration, EnumDeclaration)


def wc_newlines(text: str) -> int:
    return text.count("\n")


def logical_line_count(text: str) -> int:
    if text == "":
        return 0
    extra = 0 if text.endswith("\n") else 1
    return text.count("\n") + extra


def classify_lines(text: str) -> dict:
    logical = logical_line_count(text)
    blank = comment = code = 0
    i = 0
    n = len(text)
    in_block = False
    line_has_code = False
    line_has_comment = False
    line_has_nonblank = False

    def end_line() -> None:
        nonlocal blank, comment, code, line_has_code, line_has_comment, line_has_nonblank
        if line_has_code:
            code += 1
        elif line_has_comment or (in_block and line_has_nonblank):
            comment += 1
        elif in_block:
            comment += 1
        else:
            blank += 1
        line_has_code = False
        line_has_comment = False
        line_has_nonblank = False

    while i < n:
        ch = text[i]
        if ch == "\n":
            end_line()
            i += 1
            continue
        if in_block:
            line_has_nonblank = True
            line_has_comment = True
            if ch == "*" and i + 1 < n and text[i + 1] == "/":
                in_block = False
                i += 2
            else:
                i += 1
            continue
        if ch in " \t\r\f":
            i += 1
            continue
        line_has_nonblank = True
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            line_has_comment = True
            i += 2
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            line_has_comment = True
            in_block = True
            i += 2
            continue
        if ch == '"' or ch == "'":
            quote = ch
            line_has_code = True
            i += 1
            while i < n and text[i] != "\n":
                if text[i] == "\\":
                    i += 2
                    continue
                if text[i] == quote:
                    i += 1
                    break
                i += 1
            continue
        line_has_code = True
        i += 1
    if text and not text.endswith("\n"):
        end_line()
    return {
        "wc_newlines": wc_newlines(text),
        "logical_lines": logical,
        "blank_lines": blank,
        "comment_lines": comment,
        "code_lines": code,
    }


def type_kind(node: object) -> str:
    if isinstance(node, ClassDeclaration):
        return "class"
    if isinstance(node, InterfaceDeclaration):
        return "interface"
    if isinstance(node, EnumDeclaration):
        return "enum"
    return node.__class__.__name__


def type_name_of(type_node) -> str:
    if type_node is None:
        return ""
    name = getattr(type_node, "name", "") or ""
    dims = "[]" * len(getattr(type_node, "dimensions", None) or [])
    return name + dims


def walk_named(node, package: str, enclosing_fqn: str, file_rel: str, class_rows: list, method_rows: list) -> None:
    fqn = f"{enclosing_fqn}.{node.name}" if enclosing_fqn else (
        f"{package}.{node.name}" if package else node.name
    )
    class_rows.append(
        {
            "file": file_rel,
            "package": package,
            "type": node.name,
            "fqn": fqn,
            "kind": type_kind(node),
            "top_level": "yes" if enclosing_fqn == "" else "no",
            "line": "" if node.position is None else node.position.line,
        }
    )
    for member in getattr(node, "body", None) or []:
        if isinstance(member, TYPE_NODES):
            walk_named(member, package, fqn, file_rel, class_rows, method_rows)
        elif isinstance(member, (MethodDeclaration, ConstructorDeclaration)):
            method_rows.append(method_row(member, package, fqn, file_rel, anonymous="no"))


def method_row(member, package: str, declaring: str, file_rel: str, anonymous: str) -> dict:
    params = []
    for param in member.parameters or []:
        params.append(type_name_of(param.type) + " " + param.name)
    return_type = ""
    if isinstance(member, MethodDeclaration):
        return_type = type_name_of(member.return_type) or "void"
    return {
        "file": file_rel,
        "package": package,
        "declaring_type": declaring,
        "anonymous": anonymous,
        "kind": "constructor" if isinstance(member, ConstructorDeclaration) else "method",
        "name": member.name,
        "return_type": return_type,
        "parameters": ", ".join(params),
        "line": "" if member.position is None else member.position.line,
    }


def collect_anonymous_methods(tree, package: str, file_rel: str, method_rows: list) -> None:
    for path, node in tree.filter(MethodDeclaration):
        creator_seen = False
        enclosing = ""
        for ancestor in path:
            if isinstance(ancestor, TYPE_NODES):
                if enclosing == "":
                    enclosing = f"{package}.{ancestor.name}" if package else ancestor.name
                elif not creator_seen:
                    enclosing = enclosing + "." + ancestor.name
            if ancestor.__class__.__name__ == "ClassCreator":
                creator_seen = True
        if creator_seen:
            owner = (enclosing or package or file_rel) + "#anonymous"
            method_rows.append(method_row(node, package, owner, file_rel, anonymous="yes"))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: count_sources.py SRC_ROOT OUT_DIR", file=sys.stderr)
        return 2
    src_root = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve()
    repo = Path("/workspace")
    java_files = sorted(src_root.rglob("*.java"))
    file_rows = []
    class_rows = []
    method_rows = []
    packages = []

    for path in java_files:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(repo))
        stats = classify_lines(text)
        tree = javalang.parse.parse(text)
        package = tree.package.name if tree.package else ""
        if package and package not in packages:
            packages.append(package)
        file_rows.append({"file": rel, "package": package, **stats})
        for typ in tree.types or []:
            walk_named(typ, package, "", rel, class_rows, method_rows)
        collect_anonymous_methods(tree, package, rel, method_rows)

    res_rows = []
    res_root = repo / "res"
    for path in sorted(p for p in res_root.rglob("*") if p.is_file()):
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
            stats = classify_lines(text)
        except UnicodeDecodeError:
            stats = {
                "wc_newlines": raw.count(b"\n"),
                "logical_lines": "",
                "blank_lines": "",
                "comment_lines": "",
                "code_lines": "",
            }
        res_rows.append({"file": str(path.relative_to(repo)), "bytes": len(raw), **stats})

    write_csv(out_dir / "java-files.csv", file_rows)
    write_csv(out_dir / "java-types.csv", class_rows)
    write_csv(out_dir / "java-methods.csv", method_rows)
    write_csv(
        out_dir / "java-packages.csv",
        [{"package": name, "files": sum(1 for row in file_rows if row["package"] == name)} for name in packages],
    )
    write_csv(out_dir / "resources.csv", res_rows)

    named_methods = [row for row in method_rows if row["kind"] == "method" and row["anonymous"] == "no"]
    anon_methods = [row for row in method_rows if row["anonymous"] == "yes"]
    constructors = [row for row in method_rows if row["kind"] == "constructor"]
    text_res = [row for row in res_rows if row["logical_lines"] != ""]
    summary = {
        "java_files": len(file_rows),
        "packages": len(packages),
        "types_named_including_inner": len(class_rows),
        "types_top_level": sum(1 for row in class_rows if row["top_level"] == "yes"),
        "classes": sum(1 for row in class_rows if row["kind"] == "class"),
        "interfaces": sum(1 for row in class_rows if row["kind"] == "interface"),
        "enums": sum(1 for row in class_rows if row["kind"] == "enum"),
        "methods_in_named_types": len(named_methods),
        "methods_in_anonymous_classes": len(anon_methods),
        "constructors": len(constructors),
        "java_wc_newlines": sum(row["wc_newlines"] for row in file_rows),
        "java_logical_lines": sum(row["logical_lines"] for row in file_rows),
        "java_blank_lines": sum(row["blank_lines"] for row in file_rows),
        "java_comment_lines": sum(row["comment_lines"] for row in file_rows),
        "java_code_lines": sum(row["code_lines"] for row in file_rows),
        "resource_files": len(res_rows),
        "resource_text_files": len(text_res),
        "resource_binary_files": len(res_rows) - len(text_res),
        "resource_wc_newlines_text_only": sum(int(row["wc_newlines"]) for row in text_res),
        "resource_logical_lines_text": sum(int(row["logical_lines"]) for row in text_res),
        "parser": "javalang 0.13.0",
    }
    write_csv(out_dir / "summary.csv", [summary])
    for key, value in summary.items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
