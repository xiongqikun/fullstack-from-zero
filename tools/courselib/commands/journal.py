"""``journal``: append an entry to ``journal/YYYY-MM-DD.md`` (plan I4).

Three one-line fields (做了什么 / 卡在哪 / 下次从哪开始) and two optional ones
(哪里看不懂 / 哪里太慢).  Without ``--done`` the fields are asked for one by
one; with ``--done`` nothing is asked and a missing ``--stuck`` or ``--next``
stays empty.  In non-interactive mode ``--done`` is required.
"""

from .. import cmdkit, journal, progress
from .. import status as next_steps
from ..errors import EXIT_NOT_YET, EXIT_OK, UsageProblem
from ..ui import one_line

SUMMARY = "写一条学习日志（收工前用）"
DESCRIPTION = """往今天的日志文件 journal/年-月-日.md 里加一条记录。日志是你自己的：
工具只会在文件末尾追加，不会改动已经写下的内容。

直接运行会一项一项问你；也可以把内容写在命令里：
  python3 tools/course.py journal --done '做完了 1.6b' --stuck '引号打成了全角' --next '从 1.6c 继续'

不写"下次从哪开始"时，直接回车就用工具算出的那一句（和 check、status 说的一样）。
"""

# ---------------------------------------------------------------------------
# Every user-visible string of this module.
# ---------------------------------------------------------------------------
TEXT = {
    "done_help": "做了什么（一句话）",
    "stuck_help": "卡在哪（没有可以不写）",
    "next_help": "下次从哪开始",
    "unclear_help": "哪里看不懂（可选）",
    "slow_help": "哪里太慢（可选）",
    "text": "<一句话>",
    "ask_done": "做了什么（一句话）：",
    "ask_done_again": "这一项不能空着。今天做了什么（哪怕只是读了一段课文）：",
    "ask_stuck": "卡在哪（没有就直接回车）：",
    "ask_next": "下次从哪开始（直接回车 = {default}）：",
    "ask_next_plain": "下次从哪开始（没想好就直接回车）：",
    "ask_unclear": "哪里看不懂（可选，直接回车跳过）：",
    "ask_slow": "哪里太慢（可选，直接回车跳过）：",
    "need_done": "不提问模式下要用 --done 写明做了什么，例如：--done \"做完了 1.6b\"",
    "empty": "没有写内容，日志没有改动。",
    "written": "已记到 {path}。",
    "bye": "下次打开终端，运行 python3 tools/course.py 就能看到从哪继续。",
}


def register(subparsers):
    parser = cmdkit.add_command(subparsers, "journal", SUMMARY, description=DESCRIPTION)
    parser.add_argument("--done", metavar=TEXT["text"], help=TEXT["done_help"])
    parser.add_argument("--stuck", metavar=TEXT["text"], help=TEXT["stuck_help"])
    parser.add_argument("--next", dest="next_step", metavar=TEXT["text"], help=TEXT["next_help"])
    parser.add_argument("--unclear", metavar=TEXT["text"], help=TEXT["unclear_help"])
    parser.add_argument("--slow", metavar=TEXT["text"], help=TEXT["slow_help"])


def _next_default(app, state):
    """A suggestion for 下次从哪开始: the sentence for the tutor of ``status.next_step``.

    The same answer as ``check`` and ``status`` give, reviews left out:
    「从 1.6b 继续」, 「从 0.1 的收尾继续」, 「从 1.7 开始」, 「做小关卡 gate-a」,
    「请问我 gate-a 的讲解题」 or 「准备阶段 2」; "" when there are no lessons.
    """
    return next_steps.next_step(app, state, reviews=False).say


def run(args):
    app = args.app
    console = app.console
    state = app.store.load()
    values = {"done": args.done, "stuck": args.stuck, "next": args.next_step,
              "unclear": args.unclear, "slow": args.slow}
    nothing_given = all(value is None for value in values.values())
    if (values["done"] or "").strip():
        # --done given: what the flags say is the entry.  Nothing is asked
        # (a missing --stuck or --next stays empty), so an end-of-file at a
        # follow-up prompt can never throw the given text away.
        pass
    elif console.can_prompt:
        if not (values["done"] or "").strip():
            values["done"] = console.read(TEXT["ask_done"])
            if not values["done"].strip():
                values["done"] = console.read(TEXT["ask_done_again"])
            if not values["done"].strip():
                # Asked twice and still nothing: stop here instead of asking more.
                console.out(TEXT["empty"])
                return EXIT_NOT_YET
        if values["stuck"] is None:
            values["stuck"] = console.read(TEXT["ask_stuck"])
        if values["next"] is None:
            default = _next_default(app, state)
            prompt = TEXT["ask_next"].format(default=default) if default else TEXT["ask_next_plain"]
            values["next"] = console.read(prompt).strip() or default
        if nothing_given:
            values["unclear"] = console.read(TEXT["ask_unclear"])
            values["slow"] = console.read(TEXT["ask_slow"])
    elif not (values["done"] or "").strip():
        raise UsageProblem(TEXT["need_done"])
    values = {key: one_line(value or "") for key, value in values.items()}
    if not values["done"]:  # pragma: no cover - guarded above; kept as a safety net
        console.out(TEXT["empty"])
        return EXIT_NOT_YET
    path = journal.append_entry(app, values)
    progress.touch_session(state, app.now)
    app.store.save(state, events=[{
        "type": "journal", "file": app.rel(path),
        "fields": [key for key, _ in journal.FIELDS if values.get(key)]}])
    console.out(TEXT["written"].format(path=app.rel(path)))
    console.out(TEXT["bye"])
    return EXIT_OK
