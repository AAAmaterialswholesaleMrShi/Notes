import net.micode.notes.tool.NoteTextMetrics;
import net.micode.notes.tool.TrashPolicy;

/**
 * 不依赖 Android SDK 的断言程序。失败时进程退出码为 1。
 */
public class RunToolTests {
    private static int failed;

    public static void main(String[] args) {
        testEmpty();
        testCodePoints();
        testLines();
        testChecklist();
        testTrashDecide();
        testRestoreParent();
        if (failed == 0) {
            System.out.println("ALL PASSED");
        } else {
            System.out.println("FAILED " + failed);
            System.exit(1);
        }
    }

    private static void testEmpty() {
        NoteTextMetrics.Summary empty = NoteTextMetrics.analyze(null);
        check(empty.codePoints == 0 && empty.lines == 0 && empty.checklistItems == 0, "null text");
        NoteTextMetrics.Summary blank = NoteTextMetrics.analyze("");
        check(blank.codePoints == 0 && blank.utf16Units == 0 && blank.lines == 0, "empty text");
    }

    private static void testCodePoints() {
        NoteTextMetrics.Summary han = NoteTextMetrics.analyze("你好");
        check(han.codePoints == 2 && han.utf16Units == 2 && han.lines == 1, "two han characters");
        String emoji = "\uD83D\uDE00";
        NoteTextMetrics.Summary face = NoteTextMetrics.analyze(emoji);
        check(face.codePoints == 1 && face.utf16Units == 2, "emoji is one code point");
        NoteTextMetrics.Summary spaced = NoteTextMetrics.analyze("a b\n");
        check(spaced.codePoints == 4 && spaced.nonWhitespaceCodePoints == 2 && spaced.lines == 1,
                "whitespace and trailing newline");
    }

    private static void testLines() {
        check(NoteTextMetrics.analyze("a\nb").lines == 2, "two lines");
        check(NoteTextMetrics.analyze("a\n\nb").lines == 3, "blank line kept");
        check(NoteTextMetrics.analyze("a\n").lines == 1, "trailing newline dropped");
        check(NoteTextMetrics.analyze("\n").lines == 1, "single newline is one empty line");
    }

    private static void testChecklist() {
        String text = "\u221A 买菜\n\u25A1 写作业\n普通正文\n";
        NoteTextMetrics.Summary summary = NoteTextMetrics.analyze(text);
        check(summary.checklistItems == 2 && summary.checklistDone == 1, "checklist marks");
        check(summary.lines == 3, "checklist line count");
        check(NoteTextMetrics.analyze("  \u25A1 缩进").checklistItems == 1, "trimmed mark");
    }

    private static void testTrashDecide() {
        check(TrashPolicy.decide(8L, 0L) == TrashPolicy.DeleteAction.MOVE_TO_TRASH, "normal delete");
        check(TrashPolicy.decide(8L, TrashPolicy.TRASH_FOLDER_ID) == TrashPolicy.DeleteAction.PURGE,
                "purge in trash");
        check(TrashPolicy.decide(TrashPolicy.ROOT_FOLDER_ID, 0L) == TrashPolicy.DeleteAction.REJECT,
                "reject root");
        check(TrashPolicy.decide(TrashPolicy.TRASH_FOLDER_ID, 0L) == TrashPolicy.DeleteAction.REJECT,
                "reject trash folder");
        check(TrashPolicy.decide(TrashPolicy.CALL_RECORD_FOLDER_ID, 0L)
                == TrashPolicy.DeleteAction.REJECT, "reject call folder");
        check(TrashPolicy.TRASH_FOLDER_ID == -3L && TrashPolicy.ROOT_FOLDER_ID == 0L
                && TrashPolicy.TEMPORARY_FOLDER_ID == -1L
                && TrashPolicy.CALL_RECORD_FOLDER_ID == -2L, "ids match Notes.java");
    }

    private static void testRestoreParent() {
        check(TrashPolicy.restoreParent(0L, true) == 0L, "root origin");
        check(TrashPolicy.restoreParent(-2L, true) == -2L, "call folder origin");
        check(TrashPolicy.restoreParent(12L, true) == 12L, "user folder still exists");
        check(TrashPolicy.restoreParent(12L, false) == 0L, "missing folder falls back to root");
        check(TrashPolicy.restoreParent(-3L, true) == 0L, "do not restore into trash");
        check(TrashPolicy.restoreParent(-1L, true) == 0L, "do not restore into temporary");
    }

    private static void check(boolean condition, String name) {
        if (condition) {
            System.out.println("PASS " + name);
        } else {
            failed++;
            System.out.println("FAIL " + name);
        }
    }
}
