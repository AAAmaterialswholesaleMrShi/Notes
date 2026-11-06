#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成课程图的 SVG 源文件，并用 cairosvg 导出 PNG。这些是示意图，不是模拟器截图。"""

from pathlib import Path

import cairosvg

OUT = Path("/workspace/course-practice/diagrams")


def svg_page(width, height, body, title):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#f7f4ee"/>
  <text x="32" y="36" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="20" fill="#1d2a24">{title}</text>
  {body}
</svg>
'''


def ellipse(x, y, w, h, text, fill="#fffdf8"):
    lines = text.split("\n")
    tspans = []
    start = y - (len(lines) - 1) * 9
    for i, line in enumerate(lines):
        tspans.append(
            f'<tspan x="{x}" y="{start + i * 18}">{line}</tspan>'
        )
    return (
        f'<ellipse cx="{x}" cy="{y}" rx="{w}" ry="{h}" fill="{fill}" stroke="#1f4d3a" stroke-width="1.6"/>'
        f'<text text-anchor="middle" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="14" fill="#1d2a24">{"".join(tspans)}</text>'
    )


def actor(x, y, name):
    return f'''
    <circle cx="{x}" cy="{y}" r="16" fill="none" stroke="#1d2a24" stroke-width="1.8"/>
    <line x1="{x}" y1="{y+16}" x2="{x}" y2="{y+52}" stroke="#1d2a24" stroke-width="1.8"/>
    <line x1="{x-18}" y1="{y+32}" x2="{x+18}" y2="{y+32}" stroke="#1d2a24" stroke-width="1.8"/>
    <line x1="{x}" y1="{y+52}" x2="{x-16}" y2="{y+78}" stroke="#1d2a24" stroke-width="1.8"/>
    <line x1="{x}" y1="{y+52}" x2="{x+16}" y2="{y+78}" stroke="#1d2a24" stroke-width="1.8"/>
    <text x="{x}" y="{y+100}" text-anchor="middle" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="15" fill="#1d2a24">{name}</text>
    '''


def box(x, y, w, h, title, lines, fill="#fffdf8", stroke="#1f4d3a"):
    body = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>']
    body.append(f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="6" fill="#1f4d3a"/>')
    body.append(f'<rect x="{x}" y="{y+16}" width="{w}" height="12" fill="#1f4d3a"/>')
    body.append(
        f'<text x="{x+12}" y="{y+19}" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="14" fill="#f7f4ee">{title}</text>'
    )
    yy = y + 50
    for line in lines:
        body.append(
            f'<text x="{x+12}" y="{yy}" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="13" fill="#1d2a24">{line}</text>'
        )
        yy += 18
    return "\n".join(body)


def arrow(x1, y1, x2, y2, label=""):
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2 - 6
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#8a5a2a" stroke-width="1.4" marker-end="url(#arrow)"/>'
        + (f'<text x="{mid_x}" y="{mid_y}" text-anchor="middle" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="12" fill="#8a5a2a">{label}</text>' if label else "")
    )


DEFS = '''
<defs>
  <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
    <path d="M0,0 L8,3 L0,6 Z" fill="#8a5a2a"/>
  </marker>
</defs>
'''


def phone(x, y, title, rows):
    parts = [
        f'<rect x="{x}" y="{y}" width="280" height="520" rx="28" fill="#1d2a24"/>',
        f'<rect x="{x+12}" y="{y+12}" width="256" height="496" rx="18" fill="#f3ecdf"/>',
        f'<text x="{x+140}" y="{y+48}" text-anchor="middle" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="16" fill="#1d2a24">{title}</text>',
    ]
    yy = y + 70
    for kind, text in rows:
        if kind == "bar":
            parts.append(f'<rect x="{x+28}" y="{yy}" width="224" height="28" rx="4" fill="#ead8b8"/>')
            parts.append(f'<text x="{x+40}" y="{yy+19}" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="13" fill="#1d2a24">{text}</text>')
            yy += 38
        elif kind == "note":
            parts.append(f'<rect x="{x+28}" y="{yy}" width="224" height="64" rx="6" fill="#fffdf8" stroke="#d7c7a4"/>')
            parts.append(f'<text x="{x+40}" y="{yy+28}" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="14" fill="#1d2a24">{text}</text>')
            yy += 74
        elif kind == "meta":
            parts.append(f'<text x="{x+28}" y="{yy}" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="13" fill="#6d5b3d">{text}</text>')
            yy += 24
        elif kind == "body":
            parts.append(f'<text x="{x+28}" y="{yy}" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="15" fill="#1d2a24">{text}</text>')
            yy += 26
        elif kind == "button":
            parts.append(f'<rect x="{x+28}" y="{y+450}" width="224" height="40" rx="20" fill="#1f4d3a"/>')
            parts.append(f'<text x="{x+140}" y="{y+475}" text-anchor="middle" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="14" fill="#f7f4ee">{text}</text>')
    parts.append(f'<text x="{x+140}" y="{y+548}" text-anchor="middle" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="12" fill="#6d5b3d">界面原型，不是模拟器截图</text>')
    return "\n".join(parts)


def write(name, content):
    path = OUT / name
    path.write_text(content, encoding="utf-8")
    png = path.with_suffix(".png")
    cairosvg.svg2png(url=str(path), write_to=str(png))
    print(png)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    usecase = DEFS + actor(90, 180, "用户") + actor(90, 430, "闹钟服务")
    items = [
        (280, 90, "浏览列表"),
        (470, 90, "新建/编辑"),
        (660, 90, "清单模式"),
        (850, 90, "文件夹"),
        (280, 190, "搜索"),
        (470, 190, "分享"),
        (660, 190, "导出文本"),
        (850, 190, "桌面小部件"),
        (280, 300, "设置提醒"),
        (470, 300, "到点提醒"),
        (660, 300, "同步账号"),
        (850, 300, "通话便签"),
        (360, 430, "查看字数\n和清单进度"),
        (560, 430, "移入回收站"),
        (760, 430, "恢复/清空"),
    ]
    for x, y, text in items:
        fill = "#e7f0ea" if y >= 400 else "#fffdf8"
        usecase += ellipse(x, y, 78, 36, text, fill)
    usecase += (
        '<text x="32" y="560" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="13" fill="#6d5b3d">'
        "浅色椭圆是从现有源码读出的原有能力。绿色椭圆是本次实现的两项改进。同步仍调用已停用的 Google Tasks 接口，图中保留是因为它的代码还在。"
        "</text>"
    )
    write("fig-01-usecase.svg", svg_page(980, 590, usecase, "图1  便签备忘用例图"))

    seq = DEFS
    headers = [(80, "用户"), (280, "NoteEditActivity"), (520, "NoteTextMetrics"), (760, "字数 TextView")]
    for x, name in headers:
        seq += f'<rect x="{x-70}" y="70" width="150" height="36" rx="6" fill="#1f4d3a"/>'
        seq += f'<text x="{x+5}" y="93" text-anchor="middle" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="13" fill="#f7f4ee">{name}</text>'
        seq += f'<line x1="{x+5}" y1="106" x2="{x+5}" y2="430" stroke="#1d2a24" stroke-dasharray="4 4"/>'
    seq += arrow(85, 150, 280, 150, "输入文字")
    seq += arrow(285, 200, 520, 200, "analyze(text)")
    seq += arrow(525, 250, 285, 250, "Summary")
    seq += arrow(285, 310, 760, 310, "setText 字数/行数或清单进度")
    seq += '<text x="32" y="480" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="13" fill="#6d5b3d">清单模式传给 analyze 的字符串带 √ / □ 前缀，和保存进 data.content 的格式相同。统计结果不写入数据库。</text>'
    write("fig-02-sequence-metrics.svg", svg_page(920, 520, seq, "图2  编辑页刷新字数的顺序图"))

    seq2 = DEFS
    headers = [(70, "用户"), (230, "列表界面"), (420, "TrashPolicy"), (620, "DataUtils"), (810, "note 表")]
    for x, name in headers:
        seq2 += f'<rect x="{x-60}" y="70" width="130" height="36" rx="6" fill="#1f4d3a"/>'
        seq2 += f'<text x="{x+5}" y="93" text-anchor="middle" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="13" fill="#f7f4ee">{name}</text>'
        seq2 += f'<line x1="{x+5}" y1="106" x2="{x+5}" y2="470" stroke="#1d2a24" stroke-dasharray="4 4"/>'
    seq2 += arrow(75, 150, 230, 150, "删除")
    seq2 += arrow(235, 200, 420, 200, "decide")
    seq2 += arrow(425, 250, 235, 250, "MOVE_TO_TRASH")
    seq2 += arrow(235, 310, 620, 310, "moveNotesToTrash")
    seq2 += arrow(625, 360, 810, 360, "parent_id=-3, origin_parent_id=当前父id")
    seq2 += arrow(75, 430, 230, 430, "在回收站选择恢复")
    seq2 += '<text x="32" y="530" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="13" fill="#6d5b3d">恢复时 DataUtils 再读 origin_parent_id，调用 restoreParent。原文件夹不存在则回到根目录 0。已经在回收站里的删除才是物理删除。</text>'
    write("fig-03-sequence-trash.svg", svg_page(960, 570, seq2, "图3  移入回收站并恢复的顺序图"))

    classes = (
        box(40, 80, 280, 150, "NoteTextMetrics  本次新增", ["+ analyze(String): Summary", "+ splitLines(String): String[]", "不保存数据"])
        + box(360, 80, 280, 170, "TrashPolicy  本次新增", ["+ decide(id, parent): DeleteAction", "+ restoreParent(origin, exists): long", "常量与 Notes 的系统文件夹 id 相同"])
        + box(680, 80, 250, 190, "DataUtils  原有类，新增方法", ["+ moveNotesToTrash(...)", "+ restoreNotesFromTrash(...)", "+ queryNoteIdsByParent(...)", "原有 batchDeleteNotes 仍负责物理删除"])
        + box(40, 320, 280, 150, "NoteEditActivity  原有界面", ["调用 NoteTextMetrics", "删除时调用 TrashPolicy", "字数只显示，不入库"])
        + box(360, 320, 280, 150, "NotesListActivity  原有界面", ["菜单进入回收站 id=-3", "普通删除改为移入回收站", "回收站内可恢复或清空"])
        + box(680, 320, 250, 170, "NotesDatabaseHelper", ["已有表 note、data", "版本 4 → 5", "只重建 folder_move_notes_on_trash", "不新增表或列"])
    )
    write("fig-04-class.svg", svg_page(980, 540, classes, "图4  本次改动涉及的类"))

    state = DEFS
    state += ellipse(180, 180, 90, 40, "在普通文件夹")
    state += ellipse(480, 180, 90, 40, "在回收站", "#e7f0ea")
    state += ellipse(780, 180, 90, 40, "记录已删除")
    state += arrow(270, 180, 390, 180, "删除")
    state += arrow(390, 220, 270, 220, "恢复")
    state += arrow(570, 180, 690, 180, "永久删除或清空")
    state += '<text x="32" y="320" font-family="WenQuanYi Micro Hei, Droid Sans Fallback, sans-serif" font-size="13" fill="#6d5b3d">状态由图中的 note.parent_id 表达：不是 -3 表示还在普通位置，等于 -3 表示在回收站。物理删除后行不再存在。没有新增状态表。</text>'
    write("fig-05-state-trash.svg", svg_page(960, 360, state, "图5  便签删除状态图"))

    activity = DEFS
    activity += box(80, 80, 220, 70, "开始", ["用户在列表或编辑页点删除"])
    activity += box(360, 80, 240, 90, "判断", ["TrashPolicy.decide", "父 id 是否已是 -3"])
    activity += box(680, 70, 240, 100, "移入回收站", ["写 parent_id = -3", "写 origin_parent_id"])
    activity += box(680, 230, 240, 100, "物理删除", ["batchDeleteNotes", "触发器删除 data 行"])
    activity += arrow(300, 115, 360, 115, "")
    activity += arrow(600, 100, 680, 110, "否")
    activity += arrow(600, 145, 680, 260, "是")
    write("fig-06-activity-trash.svg", svg_page(980, 380, activity, "图6  删除动作的活动图"))

    ui = phone(40, 40, "便签", [
        ("note", "欢迎使用 MiCode 便签"),
        ("note", "买菜：牛奶、面包"),
        ("note", "文件夹  课程"),
        ("button", "新建便签"),
    ])
    ui += phone(360, 40, "编辑", [
        ("meta", "2026-11-06  08:30"),
        ("meta", "12 字 · 2 行"),
        ("body", "买菜"),
        ("body", "牛奶、面包"),
    ])
    ui += phone(680, 40, "回收站", [
        ("bar", "回收站"),
        ("note", "已删除的便签"),
        ("button", "菜单：清空回收站"),
    ])
    write("fig-07-ui-prototype.svg", svg_page(1000, 640, ui, "图7  新增与原有界面原型"))

    data = (
        box(40, 80, 430, 250, "note  已有表，本次不新增列", [
            "_id  INTEGER  主键",
            "parent_id  INTEGER  父文件夹，回收站为 -3",
            "origin_parent_id  INTEGER  移入前的父 id",
            "snippet  TEXT  列表摘要",
            "type  INTEGER  0便签 1文件夹 2系统",
            "alert_date, bg_color_id, widget_id, ...",
            "created_date, modified_date, gtask_id, version",
            "版本 5 只改触发器，列与版本 4 相同",
        ])
        + box(500, 80, 430, 210, "data  已有表，本次未修改", [
            "_id  INTEGER  主键",
            "mime_type  TEXT  文本或通话",
            "note_id  INTEGER  属于哪条 note",
            "content  TEXT  正文",
            "data1…data5  清单模式 / 通话号码等",
            "created_date, modified_date",
        ])
        + box(40, 370, 430, 180, "note_label  拟新增，未建表", [
            "_id INTEGER 主键",
            "name TEXT  标签名，非空",
            "color INTEGER  颜色序号",
            "created_date INTEGER",
            "本次代码没有 CREATE 这张表",
        ], fill="#f6efe4", stroke="#8a5a2a")
        + box(500, 370, 430, 180, "note_label_map  拟新增，未建表", [
            "note_id INTEGER  参照 note._id",
            "label_id INTEGER  参照 note_label._id",
            "主键 (note_id, label_id)",
            "一条便签可有多个标签",
            "本次代码没有 CREATE 这张表",
        ], fill="#f6efe4", stroke="#8a5a2a")
    )
    write("fig-08-data.svg", svg_page(980, 590, data, "图8  已有表与拟新增表"))
    print("done")


if __name__ == "__main__":
    main()
