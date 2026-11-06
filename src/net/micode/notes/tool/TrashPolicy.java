/*
 * Copyright (c) 2010-2011, The MiCode Open Source Community (www.micode.net)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package net.micode.notes.tool;

/**
 * 类：决定删除时是移入回收站、永久删除，还是拒绝操作系统文件夹，以及恢复时应该回到哪个父文件夹。
 * 不访问数据库。调用方负责传入当前父 id、原来的父 id，以及原文件夹是否还在。
 * 下面四个 id 必须与 Notes.java 里的系统文件夹常量保持一致。这里不引用 Notes，
 * 是为了让该类可以在没有 Android SDK 的情况下用 javac 做单元测试。
 */
public final class TrashPolicy {
    /** 根文件夹。Notes.ID_ROOT_FOLDER。 */
    public static final long ROOT_FOLDER_ID = 0L;
    /** 临时文件夹。Notes.ID_TEMPARAY_FOLDER，源码里的拼写就是 TEMPARAY。 */
    public static final long TEMPORARY_FOLDER_ID = -1L;
    /** 通话便签文件夹。Notes.ID_CALL_RECORD_FOLDER。 */
    public static final long CALL_RECORD_FOLDER_ID = -2L;
    /** 回收站。Notes.ID_TRASH_FOLER，源码里的拼写就是 FOLER。 */
    public static final long TRASH_FOLDER_ID = -3L;

    /**
     * 删除动作。
     * MOVE_TO_TRASH：还在普通位置，删除改为移入回收站。
     * PURGE：已经在回收站，再次删除才真正从库里去掉。
     * REJECT：四个系统文件夹本身不能删除。
     */
    public enum DeleteAction {
        MOVE_TO_TRASH,
        PURGE,
        REJECT
    }

    private TrashPolicy() {
    }

    /**
     * 方法：根据便签 id 和它现在的父文件夹决定删除动作。
     * noteId 是 note 表的 _id，parentId 是当前 parent_id。
     */
    public static DeleteAction decide(long noteId, long parentId) {
        /* 语句块：系统文件夹是数据库初始化时插入的固定行，删掉会导致列表和同步失去根。 */
        if (isSystemFolder(noteId)) {
            return DeleteAction.REJECT;
        }
        /* 关键语句：只有父 id 已经是回收站时才允许物理删除。 */
        if (parentId == TRASH_FOLDER_ID) {
            return DeleteAction.PURGE;
        }
        return DeleteAction.MOVE_TO_TRASH;
    }

    /**
     * 方法：计算恢复后的 parent_id。
     * originParentId 来自 note.origin_parent_id。该列默认值是 0，和根文件夹 id 相同，
     * 所以 0 一律恢复到根目录，无法区分“原来就在根目录”和“移入回收站时没有记下原位置”。
     * originFolderStillExists 为 false 时，用户文件夹已经不在了，改回到根目录，避免便签挂到不存在的父 id 上。
     * 通话文件夹和根文件夹视为始终存在，调用方也应这样传入。
     */
    public static long restoreParent(long originParentId, boolean originFolderStillExists) {
        /* 语句块：回收站和临时文件夹不能作为恢复目标。 */
        if (originParentId == TRASH_FOLDER_ID || originParentId == TEMPORARY_FOLDER_ID) {
            return ROOT_FOLDER_ID;
        }
        if (originParentId == ROOT_FOLDER_ID || originParentId == CALL_RECORD_FOLDER_ID) {
            return originParentId;
        }
        /* 关键语句：原用户文件夹已被删掉或本身也在回收站时，退回根目录。 */
        if (!originFolderStillExists) {
            return ROOT_FOLDER_ID;
        }
        return originParentId;
    }

    /** 方法：四个固定 id 都是系统文件夹。 */
    public static boolean isSystemFolder(long noteId) {
        return noteId == ROOT_FOLDER_ID
                || noteId == TEMPORARY_FOLDER_ID
                || noteId == CALL_RECORD_FOLDER_ID
                || noteId == TRASH_FOLDER_ID;
    }
}
