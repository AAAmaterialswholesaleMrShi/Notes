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

import android.app.PendingIntent;
import android.os.Build;

/**
 * 类：给 targetSdk 31 及以上补 PendingIntent 的不可变标志。
 * 原代码把 flags 写成 0 或只写 FLAG_UPDATE_CURRENT。目标版本不低于 31 时，
 * Android 12 及以上会因为缺少 FLAG_IMMUTABLE 或 FLAG_MUTABLE 而抛出 IllegalArgumentException。
 * 这些 PendingIntent 创建后不再被改写，使用不可变标志。
 */
public final class PendingIntentCompat {
    private PendingIntentCompat() {
    }

    /**
     * 方法：返回可以与其他 flag 按位或在一起的不可变标志。
     * FLAG_IMMUTABLE 从 API 23 才有常量；更低版本返回 0，由系统忽略未知需求。
     */
    public static int immutable() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            return PendingIntent.FLAG_IMMUTABLE;
        }
        return 0;
    }
}
