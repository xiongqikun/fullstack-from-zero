"""``validate``: for builders; checks lesson modules against the plan (I4).

Exit code 0 when no lesson has an error (warnings are allowed), 1 otherwise.
"""

import json
import os
from pathlib import Path

from .. import cmdkit, validate
from ..catalog import LESSON_ID, load_lesson
from ..errors import EXIT_NOT_YET, EXIT_OK, UsageProblem
from ..ui import BAD_MARK, OK_MARK

SUMMARY = "（建课用）检查课程模块合不合规"
DESCRIPTION = """给建课的人用：加载课程模块，逐项对照课程规范检查。

  每课要定义的名字和它们的形状（META、TERMS、checks、HINTS、REVIEW、SCENARIOS、EXAM）
  每课 2 到 3 站，每站 15 到 40 分钟（超过 30 分钟提醒）、一个新概念、最多五条新命令、
    一个检查、四级提示
  每课最多两张规则卡；每张卡十三个字段都要写全：约束力（带适用范围）、
    规则类型（七种之一）、谁说的、核对日期和复核周期、谁来管和不遵守的后果……
  大纲里规定的文件夹、站点编号、规则编号和关卡
  课文里反复出现的固定写法（只提醒，不算错误）：存档点、每站四部分和最后的提示、检查两行、
    收尾、“课文对不上”那一行、对导师说的话、引号、学习工作区的叫法、可跳过的材料、
    本课行规的表、旧教程提醒、git config 的写法、开头的用时

例子：
  python3 tools/course.py validate                检查 stages/ 下的全部课程
  python3 tools/course.py validate 1.6 1.7        只检查这两课
  python3 tools/course.py validate --build 1.6    另外把 1.6 的场景和考题试搭一遍
  python3 tools/course.py validate --complete     验收：大纲里的课一课都不能少"""

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "lessons_help": "只检查这些课：课程编号（如 1.6）或课程文件夹的路径；不写就检查全部",
    "complete_help": "验收模式：大纲里的每一课、每课的课文都必须在，每个关卡至少四道考题",
    "build_help": "把每个场景和每道考题在临时文件夹里试搭一遍（不动练习场）",
    "json_help": "用 JSON 输出结果（给脚本用）",
    "head": "课程自检 · {n} 课",
    "none": "没有找到任何课程模块（stages/*/*/lesson.py）。",
    "unknown": "没有找到 {what}：既不是已有的课程编号，也不是含有 lesson.py 的文件夹。",
    "lesson_line": "{mark} {id} {title}（{path}）",
    "error": "错误",
    "warning": "警告",
    "general": "跨课程的问题：",
    "total": "合计：{n} 课，{ok} 课通过，{bad} 课没通过；错误 {errors} 条，警告 {warnings} 条。",
}


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "validate", SUMMARY, description=DESCRIPTION)
    parser.add_argument("lessons", nargs="*", metavar="<课>", help=TEXT["lessons_help"])
    parser.add_argument("--complete", action="store_true", help=TEXT["complete_help"])
    parser.add_argument("--build", action="store_true", help=TEXT["build_help"])
    parser.add_argument("--json", action="store_true", help=TEXT["json_help"])


def _select(app, wanted):
    """The lessons named on the command line (all lessons when none is named)."""
    catalog = app.catalog()
    if not wanted:
        return list(catalog.all)
    chosen = []
    for text in wanted:
        target = cmdkit.clean_id(text)
        if LESSON_ID.match(target):
            found = [lesson for lesson in catalog.all if lesson.id == target]
            if not found:
                raise UsageProblem(TEXT["unknown"].format(what=text))
            chosen += [lesson for lesson in found if lesson not in chosen]
            continue
        path = Path(text)
        if not path.is_absolute():
            path = Path(os.getcwd()) / path
        if path.is_dir():
            path = path / "lesson.py"
        if not path.is_file():
            raise UsageProblem(TEXT["unknown"].format(what=text))
        known = [lesson for lesson in catalog.all
                 if os.path.realpath(str(lesson.path)) == os.path.realpath(str(path))]
        lesson = known[0] if known else load_lesson(path, app.root)
        if lesson not in chosen:
            chosen.append(lesson)
    return chosen


def run(args):
    app = args.app
    out = app.console.out
    lessons = _select(app, args.lessons)
    if not lessons and not args.complete:
        if args.json:
            out(json.dumps({"ok": False, "lessons": [], "general": [], "message": TEXT["none"]},
                           ensure_ascii=False))
        else:
            out(TEXT["none"])
        return EXIT_NOT_YET
    reports, general = validate.validate_all(app, lessons, complete=args.complete,
                                             build=args.build)
    errors = sum(len(report.errors) for report in reports)
    errors += sum(1 for finding in general if finding.level == validate.ERROR)
    warnings = sum(len(report.warnings) for report in reports)
    warnings += sum(1 for finding in general if finding.level == validate.WARNING)
    passed = sum(1 for report in reports if report.ok)

    if args.json:
        out(json.dumps({
            "ok": errors == 0,
            "counts": {"lessons": len(reports), "passed": passed,
                       "errors": errors, "warnings": warnings},
            "lessons": [{
                "id": report.lesson.id, "path": report.lesson.rel, "ok": report.ok,
                "errors": [{"code": f.code, "message": f.message} for f in report.errors],
                "warnings": [{"code": f.code, "message": f.message} for f in report.warnings],
            } for report in reports],
            "general": [{"level": f.level, "code": f.code, "message": f.message}
                        for f in general],
        }, ensure_ascii=False, indent=2))
        return EXIT_OK if errors == 0 else EXIT_NOT_YET

    out(TEXT["head"].format(n=len(reports)))
    out("")
    for report in reports:
        lesson = report.lesson
        out(TEXT["lesson_line"].format(mark=OK_MARK if report.ok else BAD_MARK,
                                       id=lesson.id or "?", title=lesson.title,
                                       path=lesson.rel))
        for finding in report.errors:
            out("     {} [{}] {}".format(TEXT["error"], finding.code, finding.message))
        for finding in report.warnings:
            out("     {} [{}] {}".format(TEXT["warning"], finding.code, finding.message))
    if general:
        out("")
        out(TEXT["general"])
        for finding in general:
            word = TEXT["error"] if finding.level == validate.ERROR else TEXT["warning"]
            out(f"     {word} [{finding.code}] {finding.message}")
    out("")
    out(TEXT["total"].format(n=len(reports), ok=passed, bad=len(reports) - passed,
                             errors=errors, warnings=warnings))
    return EXIT_OK if errors == 0 else EXIT_NOT_YET
