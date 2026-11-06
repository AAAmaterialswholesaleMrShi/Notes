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
 * 类：统计便签正文的字数、行数和清单完成度。
 * 不依赖 Android，编辑界面只负责把当前文本传进来。
 * 字数按 Unicode 码点计，一个 emoji 算 1 个字，不用 String.length() 的 UTF-16 单元数。
 * 清单标记与 NoteEditActivity 保存格式相同：完成是 √（U+221A），未完成是 □（U+25A1）。
 */
public final class NoteTextMetrics {
    /** 关键常量：完成项前缀，必须与 NoteEditActivity.TAG_CHECKED 相同。 */
    public static final String CHECKED_MARK = "\u221A";

    /** 关键常量：未完成项前缀，必须与 NoteEditActivity.TAG_UNCHECKED 相同。 */
    public static final String UNCHECKED_MARK = "\u25A1";

    private NoteTextMetrics() {
    }

    /**
     * 一次统计的结果。字段在构造后不再改变。
     */
    public static final class Summary {
        /** Unicode 码点数，含空白和换行。 */
        public final int codePoints;
        /** Java char 个数，即 UTF-16 代码单元，仅供和码点口径对照。 */
        public final int utf16Units;
        /** 去掉空白（含换行）后的码点数。 */
        public final int nonWhitespaceCodePoints;
        /** 行数。空文本为 0；末尾单独的换行不额外增加一行。 */
        public final int lines;
        /** 以清单标记开头的行数。 */
        public final int checklistItems;
        /** 以完成标记开头的行数。 */
        public final int checklistDone;

        Summary(int codePoints, int utf16Units, int nonWhitespaceCodePoints, int lines,
                int checklistItems, int checklistDone) {
            this.codePoints = codePoints;
            this.utf16Units = utf16Units;
            this.nonWhitespaceCodePoints = nonWhitespaceCodePoints;
            this.lines = lines;
            this.checklistItems = checklistItems;
            this.checklistDone = checklistDone;
        }
    }

    /**
     * 方法：统计一段便签文本。
     * text 为 null 时按空文本处理，避免编辑框尚未创建时崩溃。
     */
    public static Summary analyze(String text) {
        /* 语句块：空文本直接返回全 0，后面的分行逻辑不再运行。 */
        if (text == null || text.length() == 0) {
            return new Summary(0, 0, 0, 0, 0, 0);
        }

        int codePoints = 0;
        int nonWhitespace = 0;
        /* 语句块：按码点遍历，不能用 charAt 逐个 char，否则增补平面字符会被拆成两个字。 */
        int offset = 0;
        while (offset < text.length()) {
            int codePoint = text.codePointAt(offset);
            codePoints++;
            if (!Character.isWhitespace(codePoint)) {
                nonWhitespace++;
            }
            offset += Character.charCount(codePoint);
        }

        String[] rawLines = splitLines(text);
        int checklistItems = 0;
        int checklistDone = 0;
        /* 语句块：只把去掉首尾空白后以清单标记开头的行算进清单。普通正文不计入。 */
        for (int i = 0; i < rawLines.length; i++) {
            String line = rawLines[i].trim();
            if (line.startsWith(CHECKED_MARK)) {
                checklistItems++;
                checklistDone++;
            } else if (line.startsWith(UNCHECKED_MARK)) {
                checklistItems++;
            }
        }
        return new Summary(codePoints, text.length(), nonWhitespace, rawLines.length,
                checklistItems, checklistDone);
    }

    /**
     * 方法：按换行拆成行。
     * 关键语句：字符串以换行结尾时丢掉最后一段空串，因此 "a\n" 仍是 1 行。
     * 文本中间的空行保留，"a\n\nb" 是 3 行。
     */
    static String[] splitLines(String text) {
        String[] parts = text.split("\n", -1);
        if (text.endsWith("\n") && parts.length > 0) {
            String[] kept = new String[parts.length - 1];
            System.arraycopy(parts, 0, kept, 0, kept.length);
            return kept;
        }
        return parts;
    }
}
