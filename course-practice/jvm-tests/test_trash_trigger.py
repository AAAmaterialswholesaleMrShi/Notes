#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Python 自带 sqlite3 核对版本 5 触发器的行为。

SQL 按 NotesDatabaseHelper 里 folder_move_notes_on_trash 的语义手写了一份最小表。
脚本另外读取 Java 源码，确认触发器字符串里写了 origin_parent_id=old._id。
这不是在 Android 设备上打开 note.db，不能代替真机升级测试。
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

JAVA = Path("/workspace/src/net/micode/notes/data/NotesDatabaseHelper.java")


def main() -> int:
    text = JAVA.read_text(encoding="utf-8")
    start = text.find("FOLDER_MOVE_NOTES_ON_TRASH_TRIGGER")
    end = text.find("public NotesDatabaseHelper", start)
    trigger = text[start:end]
    if "ORIGIN_PARENT_ID + \"=old.\"" not in trigger and 'ORIGIN_PARENT_ID + "=old."' not in trigger:
        print("FAIL java trigger does not assign origin_parent_id from old._id")
        print(trigger)
        return 1
    if "DB_VERSION = 5" not in text:
        print("FAIL DB_VERSION is not 5")
        return 1
    print("PASS java trigger text contains origin_parent_id assignment and DB_VERSION 5")

    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE note (
            _id INTEGER PRIMARY KEY,
            parent_id INTEGER NOT NULL DEFAULT 0,
            origin_parent_id INTEGER NOT NULL DEFAULT 0,
            type INTEGER NOT NULL DEFAULT 0,
            snippet TEXT NOT NULL DEFAULT ''
        )
        """
    )
    connection.execute(
        """
        CREATE TRIGGER folder_move_notes_on_trash
        AFTER UPDATE ON note
        WHEN new.parent_id = -3
        BEGIN
            UPDATE note
               SET parent_id = -3,
                   origin_parent_id = old._id
             WHERE parent_id = old._id;
        END
        """
    )
    connection.execute("INSERT INTO note (_id, parent_id, type, snippet) VALUES (7, 0, 1, '工作')")
    connection.execute(
        "INSERT INTO note (_id, parent_id, type, snippet) VALUES (8, 7, 0, '子便签')"
    )
    connection.execute("UPDATE note SET parent_id = -3, origin_parent_id = 0 WHERE _id = 7")
    folder = connection.execute(
        "SELECT parent_id, origin_parent_id FROM note WHERE _id = 7"
    ).fetchone()
    child = connection.execute(
        "SELECT parent_id, origin_parent_id FROM note WHERE _id = 8"
    ).fetchone()
    if folder != (-3, 0):
        print("FAIL folder row", folder)
        return 1
    if child != (-3, 7):
        print("FAIL child row", child)
        return 1
    print("PASS sqlite trigger moves child to trash and records origin folder id 7")
    return 0


if __name__ == "__main__":
    sys.exit(main())
