#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给还没有紧邻类注释的顶层类型补上一句中文类注释。已有 JavaDoc 的文件跳过。"""

from pathlib import Path

COMMENTS = {
    "src/net/micode/notes/data/Contact.java": "按电话号码查询联系人显示名，并在进程内缓存，供通话便签列表使用。",
    "src/net/micode/notes/data/Notes.java": "便签的权威常量：ContentProvider 的 authority、系统文件夹 id、note/data 列名，以及文本便签和通话便签的 MIME。",
    "src/net/micode/notes/data/NotesDatabaseHelper.java": "创建并升级 note.db。现有用户表只有 note 和 data；版本 5 只重建触发器，不新增表。",
    "src/net/micode/notes/data/NotesProvider.java": "把 note 与 data 两张表暴露成 content://micode_notes，并提供按 snippet 搜索的查询。",
    "src/net/micode/notes/gtask/data/MetaData.java": "同步用的元数据任务，继承 Task，用来在 Google Tasks 侧保存本地同步状态。",
    "src/net/micode/notes/gtask/data/Node.java": "Google Tasks 同步树的抽象节点，持有名称、子节点和 JSON 序列化入口。",
    "src/net/micode/notes/gtask/data/SqlData.java": "本地 data 表中的一行与同步 JSON 之间的读写。",
    "src/net/micode/notes/gtask/data/SqlNote.java": "本地 note 表中的一条便签或文件夹与 GTask 任务之间的映射。",
    "src/net/micode/notes/gtask/data/Task.java": "一条 Google Tasks 任务，对应便签正文或清单项。",
    "src/net/micode/notes/gtask/data/TaskList.java": "一个 Google Tasks 列表，对应本地文件夹。",
    "src/net/micode/notes/gtask/exception/ActionFailureException.java": "同步动作被服务端拒绝或本地数据不完整时抛出的运行时异常。",
    "src/net/micode/notes/gtask/exception/NetworkFailureException.java": "同步过程中网络或登录失败时抛出的受检异常。",
    "src/net/micode/notes/gtask/remote/GTaskASyncTask.java": "在后台执行同步，并用通知栏报告进度。通知已改为 Notification.Builder。",
    "src/net/micode/notes/gtask/remote/GTaskClient.java": "用 Apache HttpClient 访问已经停用的 Google Tasks 私有接口。不同步时不会执行。",
    "src/net/micode/notes/gtask/remote/GTaskManager.java": "编排一次完整同步：登录、拉取远端列表、合并本地 note/data。",
    "src/net/micode/notes/gtask/remote/GTaskSyncService.java": "供界面启动或取消同步的 Service，本身不包含合并算法。",
    "src/net/micode/notes/model/Note.java": "已经落库的便签差异模型，把 note 与 data 的改动打成 ContentProvider 批量操作。",
    "src/net/micode/notes/model/WorkingNote.java": "编辑中的便签。空内容不会插入数据库；提醒、背景、清单模式都先记在这里。",
    "src/net/micode/notes/tool/BackupUtils.java": "把未在回收站中的便签导出成 SD 卡上的文本文件。",
    "src/net/micode/notes/tool/DataUtils.java": "通过 ContentResolver 批量删除、移动、查询便签。移入回收站和恢复是这次新增的方法。",
    "src/net/micode/notes/tool/GTaskStringUtils.java": "Google Tasks JSON 字段名常量，没有业务逻辑。",
    "src/net/micode/notes/tool/ResourceParser.java": "把背景色序号、字号序号映射到 drawable 和文字样式资源。",
    "src/net/micode/notes/ui/AlarmAlertActivity.java": "提醒时刻到达后弹出的界面，可以选择查看便签或关闭。",
    "src/net/micode/notes/ui/AlarmInitReceiver.java": "开机后为尚未过期的提醒重新注册 AlarmManager。",
    "src/net/micode/notes/ui/AlarmReceiver.java": "到点广播的接收者，拉起 AlarmAlertActivity。",
    "src/net/micode/notes/ui/DateTimePicker.java": "年、月、日、时、分的选择控件，供提醒对话框使用。",
    "src/net/micode/notes/ui/DateTimePickerDialog.java": "包裹 DateTimePicker 的对话框，确认后把毫秒时间回传给编辑界面。",
    "src/net/micode/notes/ui/DropdownMenu.java": "多选动作条上的下拉菜单，用来全选或取消全选。",
    "src/net/micode/notes/ui/FoldersListAdapter.java": "“移动到文件夹”对话框里的文件夹游标适配器。",
    "src/net/micode/notes/ui/NoteEditActivity.java": "便签编辑页：正文、清单、提醒、分享、背景和字号。这次在标题下增加字数与清单进度。",
    "src/net/micode/notes/ui/NoteEditText.java": "编辑框。清单模式下处理回车拆行、退格合并，并识别电话、邮箱和网址。",
    "src/net/micode/notes/ui/NoteItemData.java": "列表中一行的数据对象，从查询游标读取 id、摘要、颜色、父文件夹和小部件信息。",
    "src/net/micode/notes/ui/NotesListActivity.java": "便签主列表。管理文件夹、多选、搜索和导出。这次增加回收站入口，删除改为先移入回收站。",
    "src/net/micode/notes/ui/NotesListAdapter.java": "主列表的 CursorAdapter，并记录多选时勾中的行。",
    "src/net/micode/notes/ui/NotesListItem.java": "列表单行视图，按便签或文件夹、背景色和提醒状态选择背景。",
    "src/net/micode/notes/ui/NotesPreferenceActivity.java": "设置页。保存同步账号、上次同步时间和新建便签是否随机背景。",
    "src/net/micode/notes/widget/NoteWidgetProvider.java": "桌面小部件基类。按 widget id 读出便签摘要；便签在回收站时按原查询条件不会显示正文。",
    "src/net/micode/notes/widget/NoteWidgetProvider_2x.java": "2×2 桌面小部件，只提供布局和背景资源。",
    "src/net/micode/notes/widget/NoteWidgetProvider_4x.java": "4×4 桌面小部件，只提供布局和背景资源。",
}


def main() -> None:
    root = Path("/workspace")
    for rel, sentence in COMMENTS.items():
        path = root / rel
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        index = None
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.startswith("public class ") or stripped.startswith("public abstract class ") \
                    or stripped.startswith("public interface ") or stripped.startswith("public enum ") \
                    or stripped.startswith("public final class "):
                index = i
                break
        if index is None:
            raise SystemExit(f"no type in {rel}")
        previous = index - 1
        while previous >= 0 and lines[previous].strip() == "":
            previous -= 1
        if previous >= 0 and lines[previous].strip().endswith("*/"):
            print("skip", rel)
            continue
        block = (
            "/**\n"
            f" * 类：{sentence}\n"
            " */\n"
        )
        lines.insert(index, block)
        path.write_text("".join(lines), encoding="utf-8")
        print("added", rel)


if __name__ == "__main__":
    main()
