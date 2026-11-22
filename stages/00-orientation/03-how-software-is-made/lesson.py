"""Lesson 0.3: 软件是怎么做出来的，规范从哪来 (plan section 4, task T2).

A concept lesson that still has the learner do things: the ``start`` scenario
builds two small specimens of an exchange-rate dashboard in the playground,

- ``fx-dashboard``: kept in an engineering-grade way (README, data kept apart
  from code, a CHANGELOG, a backup of the data, a test file);
- ``fx-hobby``: the same idea "as it ran on someone's machine" (copies named
  app-final2.py, a hard-coded absolute path to another person's Desktop).

Every station ends in an auto-graded quiz.  Station a also reads one line the
learner adds to ``learner/profile.md`` (the product the course keeps
extending) and records it as the decision ``course_product``.  Ask items use
numbers that only the specimen yields (seeded per scenario): station a the
fifth currency's rate from the backend, station b a rate from the data backup.

Standard library only, Python 3.9 syntax, no side effects at import time.
Reference: docs/authoring/tool-api.md.
"""

import re

# ---------------------------------------------------------------------------
# META and TERMS
# ---------------------------------------------------------------------------
META = {
    "id": "0.3",
    "slug": "03-how-software-is-made",
    "title": "软件是怎么做出来的，规范从哪来",
    "stage": 0,
    "prerequisites": ["0.2"],
    "stations": [
        {
            "id": "0.3a",
            "title": "拆开一个真实的软件",
            "minutes": 35,
            "new_concept": "一个网页产品由前端、后端、数据、运行环境四块组成",
            "new_commands": [],
        },
        {
            "id": "0.3b",
            "title": "从想法到上线，工程级差在哪",
            "minutes": 30,
            "new_concept": "工程级 = 在我电脑上能跑，再加上可重复、可追溯、可协作、可验证、可恢复",
            "new_commands": ["python3 --version"],
        },
        {
            "id": "0.3c",
            "title": "规范的四种来源和约束力",
            "minutes": 30,
            "new_concept": "规则类型（谁定的）和约束力（有多强制）是两件事",
            "new_commands": [],
        },
    ],
    "rules": ["META-02"],
    "verified": {
        "date": "2026-11-20",
        "tools": {"python3": "3.14.9", "macos": "27.2.1", "zsh": "5.9"},
    },
    "unverified_steps": [
        "0.3a：用 code learner/profile.md 在 VS Code 里打开学习档案，在「## 想做的作品」下面加一行「课程产品：……」并按 ⌘S 保存"
        "（对照 VS Code 命令行文档，界面可能不同）",
        "0.3a：在 fx-dashboard 里用 code CHANGELOG.md 在 VS Code 里打开样品的更新记录，找出第五种货币（对照 VS Code 命令行文档，界面可能不同）",
        "0.3a 想多了解：对导师说“干活：带我看看我的看板由哪几块组成，只看不改”，导师只读学习者自己的项目、不改文件（建课时无法验证）",
        "0.3b：用 code 打开 data/backup 里的备份文件，读 EUR 那一行（对照 VS Code 命令行文档，界面可能不同）",
        "0.3c：用 code STANDARDS.md 在 VS Code 里打开规范地图，看开头五句和第 3 节的 META-02 那一行（对照 VS Code 命令行文档，界面可能不同）",
    ],
}

TERMS = [
    {"term": "前端", "en": "front end",
     "plain": "用户直接看到、直接操作的那一块，比如浏览器里的网页", "first": "0.3a"},
    {"term": "后端", "en": "back end",
     "plain": "在别处等着回答前端提问的程序", "first": "0.3a"},
    {"term": "服务器", "en": "server",
     "plain": "一台一直开着、专门回答别人请求的电脑", "first": "0.3a"},
    {"term": "数据", "en": "data",
     "plain": "软件要记住的内容，比如每天的汇率，和程序分开存放", "first": "0.3a"},
    {"term": "运行环境", "en": "runtime environment",
     "plain": "程序运行时离不开的那些机器、系统和软件", "first": "0.3a"},
    {"term": "状态码", "en": "status code",
     "plain": "后端回答里表示结果的三位数编号，比如 404 表示没找到", "first": "0.3a"},
    {"term": "软件生命周期", "en": "software development life cycle",
     "plain": "一个软件从想法到上线、再到长期维护要走的几步", "first": "0.3b"},
    {"term": "需求", "en": "requirements",
     "plain": "写清楚要做什么、给谁用、做到什么程度算好", "first": "0.3b"},
    {"term": "测试", "en": "testing",
     "plain": "用事先写好的检查证明程序做得对", "first": "0.3b"},
    {"term": "运维", "en": "operations",
     "plain": "软件上线以后让它一直好好运行：盯着、修、备份", "first": "0.3b"},
    {"term": "岗位期望", "en": "job expectation",
     "plain": "雇主对从业者的普遍期望，不是法律义务", "first": "0.3b"},
    {"term": "规则类型", "en": "rule type",
     "plain": "一条规矩是谁定的，课程分七种", "first": "0.3c"},
    {"term": "约束力", "en": "obligation level",
     "plain": "一条规矩在你的处境里有多强制：必须、推荐、参考", "first": "0.3c"},
    {"term": "标准", "en": "standard",
     "plain": "标准组织正式发布、带编号的文件", "first": "0.3c"},
    {"term": "行业要求", "en": "compliance requirement",
     "plain": "法律、合同、审计或平台强制政策，别人能拿它追究你", "first": "0.3c"},
    {"term": "惯例", "en": "convention",
     "plain": "没人能罚你，但工具和同行都默认你这么做", "first": "0.3c"},
    {"term": "个人偏好", "en": "personal preference",
     "plain": "可以自己决定的事，不是规则", "first": "0.3c"},
]


# ---------------------------------------------------------------------------
# SCENARIOS
# ---------------------------------------------------------------------------
EXTRA_CURRENCIES = [("AUD", "澳元", 450, 490), ("SGD", "新加坡元", 530, 560), ("CAD", "加元", 500, 530)]

ANSWER_PY = '''
    """汇率看板的后端（练习用的样品）。

    真正的后端是一台服务器上一直开着、等网页来提问的程序。
    这里为了不联网，用一条命令模拟网页问它一次：
        python3 {back}/answer.py EUR
    """
    import csv
    import json
    import sys
    import unicodedata
    from pathlib import Path

    DATA = Path(__file__).resolve().parent.parent / "{data}" / "rates.csv"


    def main():
        if len(sys.argv) != 2:
            print("用法：python3 {back}/answer.py 货币代码，比如 python3 {back}/answer.py EUR")
            return 2
        # 全角字母（中文输入法打出来的 ＥＵＲ）先换成半角
        code = unicodedata.normalize("NFKC", sys.argv[1]).strip().upper()
        if not (code.isascii() and code.isalpha()):
            print("货币代码要用三个半角英文字母，比如 EUR。你输入的是：" + sys.argv[1])
            return 2
        print("请求：查 " + code + " 的汇率")
        with DATA.open(encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                if row["code"] == code:
                    print("回答：200 OK")
                    print(json.dumps(row, ensure_ascii=False))
                    return 0
        print("回答：404 Not Found")
        print("数据里没有 " + code + " 这种货币。")
        return 1


    if __name__ == "__main__":
        sys.exit(main())
'''

INDEX_HTML = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="utf-8">
      <title>汇率看板</title>
    </head>
    <body>
      <h1>汇率看板</h1>
      <p>选一种货币，看 1 个单位换多少人民币。</p>
      <select id="code"><option>USD</option><option>EUR</option><option>GBP</option></select>
      <button id="ask">查询</button>
      <table id="result"></table>
      <script>
        // 前端不自己存汇率：它向后端提问，再把回答画成表格。
        document.getElementById("ask").onclick = async () => {
          const code = document.getElementById("code").value;
          const answer = await fetch("/api/rate?code=" + code);
          document.getElementById("result").textContent = await answer.text();
        };
      </script>
    </body>
    </html>
"""

TEST_PY = '''
    """检查后端回答得对不对。在 fx-dashboard 文件夹里运行：python3 tests/test_answer.py"""
    import subprocess
    import sys
    import unittest
    from pathlib import Path

    ANSWER = Path(__file__).resolve().parent.parent / "backend" / "answer.py"


    def ask(code):
        return subprocess.run([sys.executable, str(ANSWER), code],
                              capture_output=True, text=True, encoding="utf-8")


    class AnswerTest(unittest.TestCase):
        def test_known_currency(self):
            result = ask("EUR")
            self.assertEqual(result.returncode, 0)
            self.assertIn("200 OK", result.stdout)

        def test_lower_case_code(self):
            self.assertEqual(ask("eur").returncode, 0)

        def test_unknown_currency(self):
            result = ask("JPY")
            self.assertEqual(result.returncode, 1)
            self.assertIn("404", result.stdout)
{extra}

    if __name__ == "__main__":
        unittest.main()
'''

TEST_EXTRA = '''
        def test_{lower}(self):
            self.assertIn("200 OK", ask("{code}").stdout)
'''


def _rates(sc):
    """Seeded rates: {code: (name, '7.12')} plus the extra currency."""
    extra = sc.pick(EXTRA_CURRENCIES)
    rates = [
        ("USD", "美元", "%.2f" % (sc.randint(700, 725) / 100)),
        ("EUR", "欧元", "%.2f" % (sc.randint(760, 840) / 100)),
        ("GBP", "英镑", "%.2f" % (sc.randint(880, 960) / 100)),
        ("HKD", "港币", "%.2f" % (sc.randint(89, 93) / 100)),
        (extra[0], extra[1], "%.2f" % (sc.randint(extra[2], extra[3]) / 100)),
    ]
    return rates, extra


def _csv(rates, day):
    lines = ["code,name,cny,date"]
    lines += ["%s,%s,%s,%s" % (code, name, cny, day) for code, name, cny in rates]
    return "\n".join(lines) + "\n"


def build_start(sc):
    """State before 0.3: S0 (no my-site), plus two specimens of the dashboard."""
    today = sc.now.date()
    day = (sc.ago(days=1)).date().isoformat()
    rates, extra = _rates(sc)
    tests = sc.randint(3, 4)

    d = "fx-dashboard"
    sc.write(d + "/README.md", """
        # 汇率看板（练习用的样品）

        一个显示人民币汇率的网页。这是课程做的样品，用来拆开看一个软件由哪几块组成。

        ## 怎么运行

        需要 Python 3（2026-11-20 用 Python 3.14.9 测过）。在这个文件夹里运行：

            python3 backend/answer.py EUR

        它模拟网页问后端一次“EUR 现在换多少人民币”，并打印后端的回答。

        ## 怎么检查它没坏

            python3 tests/test_answer.py

        ## 改了什么

        见 CHANGELOG.md。
    """)
    sc.write(d + "/CHANGELOG.md", """
        # 更新记录

        ## 1.1.0 - %s

        ### 新增

        - 可以查%s（%s）和港币（HKD）。

        ## 1.0.0 - %s

        ### 新增

        - 第一版：可以查美元、欧元、英镑。
    """ % (day, extra[1], extra[0], (sc.ago(days=12)).date().isoformat()))
    sc.write(d + "/frontend/index.html", INDEX_HTML)
    sc.write(d + "/backend/answer.py", ANSWER_PY.replace("{data}", "data").replace("{back}", "backend"))
    sc.write(d + "/data/rates.csv", _csv(rates, day))
    old = [(code, name, "%.2f" % (float(cny) + 0.01)) for code, name, cny in rates[:3]]
    sc.write(d + "/data/backup/rates-%s.csv" % (sc.ago(days=2)).date().isoformat(),
             _csv(old, (sc.ago(days=2)).date().isoformat()))
    extra_test = ""
    if tests == 4:
        extra_test = TEST_EXTRA.replace("{lower}", extra[0].lower()).replace("{code}", extra[0])
    sc.write(d + "/tests/test_answer.py", TEST_PY.replace("{extra}", extra_test.rstrip("\n")))

    h = "fx-hobby"
    sc.write(h + "/app.py", """
        # 汇率看板 第一版
        print("1 美元 = 7.1 人民币")
    """)
    sc.write(h + "/app-old.py", """
        # 汇率看板 旧的（别删，万一要用）
        print("1 美元 = 7.1 人民币")
        print("1 欧元 = 7.7 人民币")
    """)
    sc.write(h + "/app-final.py", """
        # 汇率看板 最终版
        rates = {"美元": 7.1, "欧元": 7.7}
        for name in rates:
            print("1 " + name + " = " + str(rates[name]) + " 人民币")
    """)
    sc.write(h + "/app-final2.py", """
        # 汇率看板 第二版（最终版）
        # 照着一篇 2020 年的教程写的：教程说要装 Python 3.8。
        print("汇率看板 第二版（教程说：需要 Python 3.8）")
        rates = open("/Users/老王/Desktop/汇率.csv", encoding="utf-8").read()
        print(rates)
    """)

    sc.fact("extra_code", extra[0])
    sc.fact("extra_name", extra[1])
    sc.fact("extra_cny", dict((c, v) for c, _n, v in rates)[extra[0]])
    sc.fact("eur_cny", rates[1][2])
    sc.fact("backup_eur", old[1][2])
    sc.fact("date", day)
    sc.fact("tests", tests)
    sc.fact("built_on", today.isoformat())
    sc.todo("看板样品（工程级的那份）：" + sc.show(d))
    sc.todo("同一个想法的“只在我电脑上能跑”版：" + sc.show(h))


SCENARIOS = {"start": build_start}


# ---------------------------------------------------------------------------
# helpers shared by checks, review items and exam graders
# ---------------------------------------------------------------------------
_NUMBER = re.compile(r"\d+(?:\.\d+)?")
_DECIMAL_COMMA = re.compile(r"(\d)[,，](\d)")
_ISO_DATE = re.compile(r"\d{4}-\d{1,2}-\d{1,2}")


def _number_is(value):
    """Expected-answer function: the answer names ``value`` (a str like '4.72').

    Accepted shapes: ``5.08``, ``5.08元``, ``1 加元 = 5.08 人民币``, ``５．０８``,
    ``5,08`` and the pasted JSON line of the backend.  A leading count ``1``
    (one unit of the currency) and dates are ignored.  More than one other
    number (a guess such as ``5.07 5.08``) is not accepted.
    """
    target = float(value)

    def match(typed):
        text = _ISO_DATE.sub(" ", _DECIMAL_COMMA.sub(r"\1.\2", typed))
        found = [float(n) for n in _NUMBER.findall(text)]
        others = [n for n in found if n != 1.0]
        candidates = sorted(set(others)) if others else found
        return len(candidates) == 1 and abs(candidates[0] - target) < 0.0051

    return match


_ANY_DATE = re.compile(r"(\d{4})\s*[-/.年]\s*(\d{1,2})\s*[-/.月]\s*(\d{1,2})")


def _date_is(value):
    """Expected-answer function: the answer names the ISO date ``value``.

    Accepted: ``2026-11-15``, ``2026/11/15``, ``2026.11.15``, ``2026年11月15日``,
    ``2026-11-5`` style without leading zeros, and the pasted JSON line.  Exactly
    one date may be named.
    """
    year, month, day = (int(part) for part in value.split("-"))

    def match(typed):
        found = set((int(y), int(m), int(d)) for y, m, d in _ANY_DATE.findall(typed))
        return found == {(year, month, day)}

    return match


PROFILE_LINE = re.compile(r"^\s*(?:#{1,6}\s*)?(?:[-*+]\s*|\d+\s*[.、)．]\s*)?(?:\*\*)?课程产品(?:\*\*)?\s*([：:])?\s*(.*?)\s*$")
PLACEHOLDERS = ("……", "...", "？", "?", "汇率看板或你的题材")


def _product(ctx):
    """Find the line 课程产品：…… in learner/profile.md; record it as a decision."""
    target = "learner/profile.md"
    if not ctx.is_file(target):
        ctx.fail("还没有学习档案。对导师说“我们来做入学问卷”，建好以后再加课程产品那一行",
                 where="learner/profile.md", saw="这个文件还不存在（它本该在第 0.1 课建好）")
        return
    value, problem, typed = None, "missing", ""
    for line in ctx.lines(target):
        found = PROFILE_LINE.match(line)
        if not found:
            continue
        text = found.group(2).strip().strip("*").strip()
        if not found.group(1):
            problem = "colon" if text else "empty"
            continue
        if not text:
            problem = "empty"
        elif "__" in text or text in PLACEHOLDERS:
            problem, typed = "placeholder", text
        else:
            value = text
            break
    if value is None:
        if problem == "colon":
            ctx.fail("「课程产品」后面漏了冒号，写成 课程产品：汇率看板 这样",
                     where="learner/profile.md 的「课程产品」那一行", saw="课程产品和题材之间没有冒号")
        elif problem == "empty":
            ctx.fail("「课程产品：」后面还没写内容", where="learner/profile.md 的「课程产品」那一行",
                     saw="冒号后面是空的")
        elif problem == "placeholder":
            ctx.fail("「课程产品：」后面还是占位的符号，换成你选的题材",
                     where="learner/profile.md 的「课程产品」那一行",
                     saw="冒号后面是「" + ctx.visible(typed)[:20] + "」，还是占位的符号")
        else:
            ctx.fail("学习档案里还没有「课程产品：……」这一行；写好了的话，确认按了 ⌘S 保存",
                     where="learner/profile.md", saw="文件里找不到以「课程产品」开头的一行")
    else:
        ctx.ok("学习档案里写下了课程产品：" + value[:20])
        ctx.decide("course_product", value[:60])
        if "汇率" not in value:
            ctx.note("你选了别的题材。课文里的例子还是汇率看板，导师会帮你对应到你的题材上。")


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
PARTS = ["前端", "后端", "数据", "运行环境"]


def check_a(ctx):
    """Station a: the product line in the profile, one ask from the specimen, three quiz items."""
    info = ctx.scenario("start")
    _product(ctx)
    if ctx.failed:
        ctx.stop()
    ctx.ask("在看板样品里用后端查一次 %s。后端回答：1 %s换多少人民币？（照屏幕上 cny 后面的数填）"
            % (info.facts["extra_code"], info.facts["extra_name"]),
            expected=_number_is(info.facts["extra_cny"]))
    ctx.quiz("网页问「EUR 现在换多少人民币」，是哪一块去查数字、再把答案送回来？", PARTS, "B",
             explain="前端只负责问和显示，查找和回答是后端的事。",
             feedback={"A": "前端只是把问题发出去、把回答显示出来，它自己不存汇率。",
                       "C": "数据只是存着，自己不会回答问题，要有程序去查它。",
                       "D": "运行环境是让程序能跑的条件，本身不回答问题。"})
    ctx.quiz("你刚才在终端里运行 answer.py。这一次，它的运行环境是什么？",
             ["样品里的 backend 文件夹", "你的 Mac，加上上面装的 python3",
              "data 文件夹里的 rates.csv", "浏览器"], "B",
             explain="运行环境不在项目文件夹里：它是程序跑在上面的那台机器和那些软件。",
             feedback={"A": "backend 文件夹里是后端的程序本身，不是让它跑起来的条件。",
                       "C": "rates.csv 是数据，程序跑起来以后才去读它。",
                       "D": "这一次没有用到浏览器：你是在终端里直接运行后端的。"})
    ctx.quiz("只把 data/rates.csv 里 EUR 的数字改掉，前端和后端的代码一行不动，再查 EUR 会怎样？",
             ["回答跟着变成新的数字", "还是旧的数字，要改代码才会变", "直接报错"], "A",
             explain="数据和程序分开放，换数据不用改程序。",
             feedback={"B": "后端每次都去 rates.csv 里现查，数字没有写死在程序里。",
                       "C": "只是换了一个数字，文件的格式没有变，后端照样读得懂。"})


def check_b(ctx):
    """Station b: one ask from the data backup, four quiz items on the engineering words."""
    info = ctx.scenario("start")
    ctx.ask("打开 fx-dashboard 的数据备份（data/backup 里的那个文件）。备份里 EUR 那一行，"
            "1 欧元换多少人民币？（照文件里的数填）",
            expected=_number_is(info.facts.get("backup_eur")
                                or "%.2f" % (float(info.facts["eur_cny"]) + 0.01)))   # scenarios built before 2026-11-20
    ctx.quiz("app-final2.py 在老王的电脑上能跑，在你这里报 FileNotFoundError。它最缺哪一个？",
             ["可重复", "可追溯", "可恢复", "可协作"], "A",
             explain="它写死了老王桌面上的文件，换一台电脑就跑不起来。",
             feedback={"B": "可追溯说的是查得到谁、什么时候、为什么改，这里的问题是换了电脑就跑不起来。",
                       "C": "可恢复说的是改坏了能回去，这里还没改坏任何东西。",
                       "D": "可协作也受影响，但最直接的毛病是同样的步骤换个地方结果就不同。"})
    ctx.quiz("fx-hobby 靠 app-old、app-final、app-final2 这样改名来留版本。它最缺哪一个？",
             ["可验证", "可追溯", "可重复"], "B",
             explain="改名留版本，看不出每一版改了什么，也留不下“谁、什么时候、为什么”。阶段 1 用 Git 的提交记录解决。",
             feedback={"A": "可验证说的是有检查证明它做得对，这里问的是改动的来龙去脉。",
                       "C": "可重复说的是换个地方照做结果一样，这里问的是改动的来龙去脉。"})
    ctx.quiz("fx-dashboard 里的 tests 文件夹，主要让它做到哪一个？",
             ["可验证", "可恢复", "可协作"], "A",
             explain="测试是写下来的检查，谁运行都能证明后端回答得对。",
             feedback={"B": "测试不保存旧版本，改坏了它只会告诉你坏了，不会帮你回去。",
                       "C": "测试对协作有帮助，但它最直接的作用是证明程序做得对。"})
    ctx.quiz("fx-dashboard 的 data/backup 里存着前几天的数据。它对应哪一个？",
             ["可追溯", "可验证", "可恢复"], "C",
             explain="数据改坏了，可以从备份拿回来。阶段 1 还会学 Git 的撤销和云端备份。",
             feedback={"A": "备份能让你回去，但不记录是谁、为什么改的。",
                       "B": "备份不检查程序对不对，它只是留着一份旧的。"})


LABELS = ["标准", "行业要求", "惯例·事实标准", "惯例·平台与工具", "规范·组织", "规范·团队约定", "个人偏好"]


def _label_options(answer, drop):
    """Six of the seven labels (quiz takes at most six): drop one that is not the answer."""
    options = [label for label in LABELS if label != drop or label == answer]
    if len(options) > 6:
        options = [label for label in options if label != "规范·组织" or label == answer][:6]
    return options


def _classify(ctx, statement, answer, drop, explain, feedback):
    options = _label_options(answer, drop)
    letter = "ABCDEF"[options.index(answer)]
    letters = dict((label, "ABCDEF"[i]) for i, label in enumerate(options))
    fb = dict((letters[label], text) for label, text in feedback.items() if label in letters)
    return ctx.quiz("这句话的规则类型是哪一种？\n  「" + statement + "」", options, letter,
                    explain=explain, feedback=fb)


def check_c(ctx):
    """Station c: six statements to classify (plan row 0.3c), one question on the two axes."""
    _classify(ctx, "HTTP 状态码 404 的意思是「没找到」（RFC 9110）。", "标准", "规范·团队约定",
              "它出自 IETF 发布的 RFC 9110，有发布机构，有编号。",
              {"惯例·平台与工具": "所有浏览器和服务器都照同一份文件来，问问这份文件是谁发的、有没有编号。",
               "惯例·事实标准": "第 3 步之前还有两步，先回头问第 1、2 步。",
               "行业要求": "没人会因为你用错状态码罚你，第 1 步不是。",
               "规范·组织": "RFC 不是一家公司写给自己工程师的指南。回头看第 2 步：发布它的 IETF 在不在那份名单里？",
               "个人偏好": "404 是什么意思不由你自己决定，所有浏览器和服务器都照同一份带编号的文件来。"})
    _classify(ctx, "你给一家银行做系统，合同写明：上线前必须通过银行的安全审计。", "行业要求", "个人偏好",
              "客户能凭合同追究你，第 1 步就是「是」。",
              {"规范·组织": "这不是银行写给自己工程师的做法指南。从第 1 步问起：这一条能不能被拿来追究你？",
               "标准": "合同条款不是标准组织发布的带编号文件。",
               "规范·团队约定": "这不是你们自己商量定的，是客户写进合同的。",
               "惯例·事实标准": "这不是很多项目照着做的公开规范，而是写进了合同。从第 1 步问起：这一条能不能被拿来追究你？",
               "惯例·平台与工具": "这不是某个工具本身的工作方式。从第 1 步问起：这一条能不能被拿来追究你？"})
    _classify(ctx, "版本号写成「主版本.次版本.修订号」，比如 2.1.0（语义化版本 2.0.0）。",
              "惯例·事实标准", "行业要求",
              "公开、有版本号、很多工具都照着做，但发布它的不是标准组织。",
              {"标准": "它有版本号，但发布它的不在第 2 步那份标准组织名单里，第 2 步不是。",
               "惯例·平台与工具": "它不是某一个工具自己的做法，很多互不相干的项目都照着做。",
               "个人偏好": "它是公开写成文字、很多项目照着做的规范，不是谁的口味。",
               "规范·组织": "它不是哪一家组织写给自己人的指南，很多互不相干的项目都照着做。回头看第 3 步。",
               "规范·团队约定": "它不是你们团队自己商量的，是公开发布、有版本号的规范。回头看第 3 步。"})
    _classify(ctx, "GitHub 会读仓库最外层文件夹里的 LICENSE 文件（写明别人能不能用你代码的文件），认出是哪种许可证，显示在仓库页面上。",
              "惯例·平台与工具", "个人偏好",
              "这只是 GitHub 这个平台本身的工作方式。",
              {"行业要求": "GitHub 不会因为你没放 LICENSE 罚你或锁你的账号，它只是不显示。",
               "惯例·事实标准": "这是一个平台自己的做法，不是很多项目共用的一份有版本号的规范。",
               "规范·组织": "这不是一份写给工程师的做法指南，而是平台本身怎么工作。",
               "标准": "GitHub 不在第 2 步那份标准组织名单里，这句话也没有标准编号。",
               "规范·团队约定": "这不是你们团队商量定的。回头看第 4 步：它是不是某一个平台本身的工作方式？"})
    _classify(ctx, "Google 的代码评审指南（评审：同事检查你的改动、提出意见）说："
                   "收到评审请求，最晚一个工作日内要回复。", "规范·组织", "行业要求",
              "一家组织以自己的名义写给自己工程师的做法指南，外人自愿采用。",
              {"标准": "Google 不在第 2 步那份标准组织名单里，这份指南也没有标准编号。",
               "惯例·事实标准": "这份指南没有版本号，又是一家公司以自己的名义写的，第 3 步不是，接着往下问。",
               "规范·团队约定": "它不是你们团队自己商量的，是另一家组织写的。",
               "惯例·平台与工具": "它不是哪个工具或平台本身的工作方式，第 4 步不是，接着往下问。",
               "个人偏好": "它是一家组织写成文字、要求自己工程师照做的规矩，不是谁的口味。"})
    _classify(ctx, "我的编辑器用深色主题，看着舒服。", "个人偏好", "惯例·事实标准",
              "只关你自己，不能拿来要求别人。",
              {"规范·团队约定": "没有人和你商量过，也没人要求别人照做。",
               "惯例·平台与工具": "编辑器默认是什么不重要，这里是你自己选的口味。",
               "规范·组织": "没有哪家组织规定你用什么颜色。",
               "标准": "没有哪个标准组织管你的编辑器配色，第 2 步不是。",
               "行业要求": "没有人会因为你用深色主题罚你、追究你，第 1 步不是。"})
    ctx.quiz("PEP 8（Python 的第 8 号改进提案，讲代码怎么写）本身是推荐。你加入的团队设了自动检查，"
             "不符合 PEP 8 的代码放不进项目。对这个团队，它变成了什么？",
             ["规则类型变成规范·团队约定，约束力不变", "规则类型还是标准，约束力变成必须（适用范围：所在团队）",
              "规则类型和约束力都没变"], "B",
             explain="谁定的没变，变的是在这个团队里有多强制。",
             feedback={"A": "PEP 8 还是 Python 官方那份带编号的文件，团队只是规定要照它做。",
                       "C": "放不进项目就是被拦下了，这已经不只是推荐。"})


checks = {"0.3a": check_a, "0.3b": check_b, "0.3c": check_c}


# ---------------------------------------------------------------------------
# HINTS
# ---------------------------------------------------------------------------
HINTS = {
    "0.3a": [
        "检查一共看三样：学习档案里那一行、你在样品里亲手查到的一个数、几道关于四块的选择题。"
        "检查结果里“还缺什么”说的是哪一样？",
        "学习档案是学习工作区里的 learner/profile.md，要有一行以「课程产品：」开头（放在「想做的作品」那一节下面），"
        "改完按 ⌘S 保存。"
        "数字要在样品文件夹 fx-dashboard 里运行后端才看得到，题目里写了要查哪种货币，它的代码在 CHANGELOG.md 里。"
        "选择题对照课文第 1 站“概念”里那张图。",
        "相似的例子：查 EUR 时，回答的第二行是 200 OK，第三行大括号里 cny 后面的数，就是 1 欧元换多少人民币。"
        "选择题想一想手机上的天气 App：你看到的页面、替你查天气的程序、记着历年气温的地方、让这一切跑起来的手机和服务器。",
        "答案：在 learner/profile.md 的「## 想做的作品」下面加一行「课程产品：汇率看板」（或你选的题材），按 ⌘S 保存。"
        "进入 ~/Developer/playground/0.3-start/fx-dashboard，运行 python3 backend/answer.py 加上题目里的货币代码，"
        "把 cny 后面的数填上。选择题依次是 B 后端、B 你的 Mac 加 python3、A 跟着变。"
        "补全的答案：后端是 backend/answer.py，数据是 data/rates.csv，运行环境是你的 Mac 加上 python3。"
        "解释：看得见的是前端，回答问题的是后端，存着的数字是数据，让它们跑起来的机器和软件是运行环境。",
    ],
    "0.3b": [
        "检查先问你一个只有打开备份文件才知道的数，再问几道题：几个词各靠什么做到。",
        "备份在 fx-dashboard 的 data/backup 文件夹里。先进入 fx-dashboard，用 ls 看备份文件叫什么，再用 code 打开它。"
        "五个词对照课文第 2 站的那张表。",
        "相似的例子：一份菜谱写着“放盐少许”，换个人做咸淡就不一样，缺的是可重复；"
        "菜谱改了好几版却没写为什么改，缺的是可追溯。"
        "打开文件的例子：第 1 站你用 code CHANGELOG.md 打开过样品的更新记录，打开备份是同一个做法。",
        "答案：在 ~/Developer/playground/0.3-start/fx-dashboard 里运行 ls data/backup，"
        "再运行 code data/backup/ 加上列出的文件名（输到 data/backup/r 按 Tab 能补全），"
        "填 EUR 那一行逗号隔开的第三项。选择题依次是 A 可重复、B 可追溯、A 可验证、C 可恢复。"
        "补全的答案：可追溯靠 CHANGELOG.md，fx-hobby 只靠改文件名；可协作靠 README.md；"
        "可验证靠 tests 文件夹里的测试，fx-hobby 没有任何测试；可恢复靠 data/backup 里的备份，fx-hobby 没有备份。"
        "解释：工程级是在“能跑”之外，让别人、别的机器、以后的你都能放心接手。",
    ],
    "0.3c": [
        "每一句话先问来源，按七步判断法从第 1 步问起，遇到第一个“是”就停。最后一题问的是两个问题要分开。",
        "七步判断法在课文第 3 站，也在 STANDARDS.md 第 2 节“七步判断法”。"
        "注意第 1 步问的是谁能罚你、追究你；第 2 步问的是发布它的是不是名单里的标准组织；"
        "第 4 步问的是它是不是某一个工具或平台本身的工作方式或期待。",
        "相似的例子：「提交说明以 feat: 或 fix: 开头」是惯例·事实标准；"
        "「ls 默认不列出名字以 . 开头的文件」（ls 的说明书里写着）是惯例·平台与工具；"
        "「收集用户的个人信息，一般要先告诉对方、取得同意」（《个人信息保护法》）是行业要求。",
        "答案：404 是标准；银行合同是行业要求；语义化版本是惯例·事实标准；GitHub 读 LICENSE 是惯例·平台与工具；"
        "Google 的评审指南是规范·组织；深色主题是个人偏好。"
        "PEP 8 那题选 B：类型还是标准，在这个团队里约束力变成必须（适用范围：所在团队）。"
        "补全的答案：README 在第 4 步停，惯例·平台与工具；PEP 8 每行 79 个字符在第 2 步停，标准；"
        "本课程规定写核对日期在第 6 步停，规范·团队约定（写成规范·本课程约定）。"
        "解释：每句都按七步从第 1 步问起，问的是这条规矩本身从哪来；有多强制，要看你今天在哪个项目、有没有人引用它。",
    ],
}


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------
REVIEW = [
    {"id": "0.3-parts", "type": "recall", "tier": "fluent", "station": "0.3a",
     "q": "一个网页产品可以拆成哪四块？每块用一句话说它做什么。",
     "a": "前端：用户看到、操作的网页。后端：在服务器上等着回答前端提问的程序。"
          "数据：存起来的内容，比如每天的汇率。运行环境：让这一切跑起来的机器和软件。"},
    {"id": "0.3-three-questions", "type": "recall", "tier": "fluent", "station": "0.3c", "rule": "META-02",
     "q": "有人告诉你一条“规矩”。照 META-02，你先问哪三件事？",
     "a": "谁说的（名称和网址）；多强制（约束力：必须、推荐还是参考，在什么范围）；哪年的版本（原文是哪一版，哪天核对的）。"},
    {"id": "0.3-two-axes", "type": "which", "tier": "fluent", "station": "0.3c",
     "q": "GB/T 开头的是推荐性国家标准。客户合同写明系统必须符合某一份 GB/T 标准。对这个项目，下面哪一句对？",
     "options": ["它的规则类型变成了行业要求", "它还是标准，只是约束力变成了必须", "它从此对所有项目都是必须"],
     "answer": "B",
     "explain": "谁定的没变；合同点了它的名，在这个项目里它就成了必须。别的项目没有这条合同，还是推荐。"},
    {"id": "0.3-classify", "type": "which", "tier": "lookup", "station": "0.3c",
     "q": "「PEP 8 建议每一级缩进用 4 个空格。」这句话的规则类型是哪一种？",
     "options": ["标准", "规范·组织", "惯例·事实标准", "个人偏好"], "answer": "A",
     "explain": "PEP 是 Python 官方的改进提案，带编号，属于标准。它本身是推荐，项目自己的风格指南优先。"},
    {"id": "0.3-grade-words", "type": "which", "tier": "lookup", "station": "0.3b",
     "q": "同事把你的项目复制到他的电脑上，照着 README 一步步做，得到和你一样的结果。这说明项目做到了哪一个？",
     "options": ["可重复", "可追溯", "可恢复"], "answer": "A",
     "explain": "可重复：换一台机器、换一个人，同样的步骤得到同样的结果。"},
    {"id": "0.3-life-cycle", "type": "recall", "tier": "aware", "station": "0.3b",
     "q": "软件生命周期的六步是什么？",
     "a": "需求、设计、开发、测试、发布、运维；运维里发现的新问题又回到需求。"},
]


# ---------------------------------------------------------------------------
# EXAM (gate-0)
# ---------------------------------------------------------------------------
FOLDER_POOLS = {
    "A": {"front": ["web", "site", "pages"], "back": ["server", "service", "responder"],
          "data": ["store", "records", "storage"]},
    "B": {"front": ["ui", "screens", "client"], "back": ["api", "worker", "handler"],
          "data": ["db", "history", "datastore"]},
}
EXAM_CODES = [("EUR", "欧元", 760, 840), ("GBP", "英镑", 880, 960), ("HKD", "港币", 89, 93)]


def build_x1(sc):
    """A dashboard whose four parts sit in folders with seeded, unexplained names."""
    pools = FOLDER_POOLS[sc.form]
    front, back, data = sc.pick(pools["front"]), sc.pick(pools["back"]), sc.pick(pools["data"])
    project = "board-" + sc.word()
    code, name, low, high = sc.pick(EXAM_CODES)
    cny = "%.2f" % (sc.randint(low, high) / 100)
    day = (sc.ago(days=sc.randint(1, 5))).date().isoformat()
    sc.write(project + "/" + front + "/index.html", INDEX_HTML)
    sc.write(project + "/" + back + "/answer.py", ANSWER_PY.replace("{data}", data).replace("{back}", back))
    rows = [("USD", "美元", "%.2f" % (sc.randint(700, 725) / 100)), (code, name, cny)]
    sc.write(project + "/" + data + "/rates.csv", _csv(rows, day))
    sc.write(project + "/docs/notes.md", """
        # 开发笔记

        这个文件夹只放给人看的说明，程序不会读它。
    """)
    sc.fact("project", project)
    sc.fact("back", back)
    sc.fact("data", data)
    sc.fact("code", code)
    sc.fact("name", name)
    sc.fact("cny", cny)
    sc.fact("date", day)


def grade_x1(ctx):
    # Both answers are typed, so the task is graded even when the learner renamed
    # or removed the task folder afterwards (that is the learner's doing, not a
    # fault of the checker).
    info = ctx.scenario()
    folders = lambda typed: typed.strip().strip("/").lower()   # noqa: E731
    if info.form == "A":
        ctx.ask("后端在哪个文件夹？（只写文件夹的名字）",
                expected=lambda typed: folders(typed) == info.facts["back"])
        ctx.ask("用后端查 %s，它回答 1 %s换多少人民币？（填 cny 后面的数）" % (info.facts["code"], info.facts["name"]),
                expected=_number_is(info.facts["cny"]))
    else:
        ctx.ask("数据放在哪个文件夹？（只写文件夹的名字）",
                expected=lambda typed: folders(typed) == info.facts["data"])
        ctx.ask("用后端查 %s，回答里的日期是哪一天？（照屏幕上的写）" % info.facts["code"],
                expected=_date_is(info.facts["date"]))


STATEMENTS = {
    "A": [
        ("PEP 8 规定：Python 代码每一级缩进用 4 个空格。", "标准"),
        ("你的 App 想上架应用商店，就必须遵守商店的审核规则，否则会被下架。", "行业要求"),
        ("我们学习小组约定：每个人每天结束前把当天的笔记交一次。", "规范·团队约定"),
        ("Google 的 Python 风格指南规定：每行最长 80 个字符。", "规范·组织"),
    ],
    "B": [
        ("约定式提交 1.0.0 规定：修复问题的提交以 fix: 开头。", "惯例·事实标准"),
        ("GitHub 会把仓库最外层文件夹里的 README 显示在仓库首页。", "惯例·平台与工具"),
        ("我喜欢把终端的字体调大一号。", "个人偏好"),
        ("日期写成 2026-11-19 这样「年-月-日」的格式（国际标准 ISO 8601）。", "标准"),
    ],
}


def build_x2(sc):
    """Two statements chosen by the seed; the folder only holds a note for the learner."""
    chosen = sc.sample(STATEMENTS[sc.form], 2)
    sc.write("README.md", """
        # 分类题

        题目里的两句话要你判断规则类型。这里不用做别的事，判断好以后，批改时回答。
    """)
    sc.fact("s1", chosen[0][0])
    sc.fact("t1", chosen[0][1])
    sc.fact("s2", chosen[1][0])
    sc.fact("t2", chosen[1][1])


def grade_x2(ctx):
    info = ctx.scenario()
    for n in ("1", "2"):
        answer = info.facts["t" + n]
        drop = "惯例·平台与工具" if answer != "惯例·平台与工具" else "规范·组织"
        options = _label_options(answer, drop)
        ctx.quiz("第 %s 句的规则类型是哪一种？\n  「%s」" % (n, info.facts["s" + n]),
                 options, "ABCDEF"[options.index(answer)])


EXAM = [
    {
        "id": "0.3-x1",
        "gate": "gate-0",
        "title": "拆开一个软件，认出它的几块",
        "minutes": 6,
        "build": build_x1,
        "task": {
            "A": "{dir}/{project} 是一个汇率看板，它的几块分在几个文件夹里，名字没有写明是哪一块。"
                 "找出哪个文件夹是后端，用它查一次 {code}，记下回答里的人民币数。批改时会问你这两样。",
            "B": "进入 {dir}/{project}：这个汇率看板的几块分在几个名字陌生的文件夹里。"
                 "找出数据放在哪个文件夹，再用后端查一次 {code}，记下回答里的日期。批改时会问你这两样。",
        },
        "grade": grade_x1,
    },
    {
        "id": "0.3-x2",
        "gate": "gate-0",
        "title": "给两句话分规则类型",
        "minutes": 4,
        "build": build_x2,
        "task": {
            "A": "判断这两句话各是哪一种规则类型：一「{s1}」；二「{s2}」。想好以后，批改时回答。",
            "B": "下面两句话，各属于哪一种规则类型（或个人偏好）？一「{s1}」；二「{s2}」。用七步判断法想好，批改时回答。",
        },
        "grade": grade_x2,
    },
]
