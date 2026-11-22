"""Fixes after the two reviews of 2026-11-20 (writer ``tools-fix``).

One test class per finding: the behaviour on correct input, the awkward
inputs the finding names, and at least one assertion that fails on the code
before the fix.  The finding ids are those of the fixer's report (B = the
behaviour review, L = the learner-path review).
"""

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import envstubs
import helpers
from test_integration import Case

from courselib import progress, validate
from courselib import status as next_steps
from courselib.commands import doctor
from courselib.commands import review as review_command
from courselib.normalize import matches, parse_int

sys.path.insert(0, str(helpers.REPO / "tools" / "dev"))
import build_starter_manifest as manifest_tool
import make_sim_home

sys.path.remove(str(helpers.REPO / "tools" / "dev"))


# ---------------------------------------------------------------------------
# B1 parse_int: a negation counts only next to the number
# ---------------------------------------------------------------------------
class ParseIntNegationTest(unittest.TestCase):
    def test_lesson_1_1_wording_as_the_answer(self):
        # lesson 1.1 asks 「隐藏文件也算，. 和 .. 不算。」; repeating it is not a negation
        for answer in ("5 个，不算 . 和 ..", "5 个，没算 . 和 ..", "5（隐藏的也算了）", "一共 5 个"):
            self.assertEqual(parse_int(answer), 5, answer)
            self.assertTrue(matches(answer, [5, 6]), answer)

    def test_remarks_and_hedges_keep_the_number(self):
        cases = {"3 个，不算隐藏文件": 3, "应该是 3 个吧，不太确定": 3, "3（不确定）": 3,
                 "3 行，不包括空行": 3, "差不多 3 个": 3, "4 行（第一行是标题）": 4,
                 "（3 个）": 3}
        for text, value in cases.items():
            self.assertEqual(parse_int(text), value, text)

    def test_a_negation_of_the_number_itself_is_still_none(self):
        for text in ("不是3", "没有 3 个", "不是三个", "不到 3 个", "一个也没有", "3 个都不是",
                     "负一", "没有"):
            self.assertIsNone(parse_int(text), text)

    def test_ranges_and_halves_are_not_one_number(self):
        for text in ("三到四个", "大约 3 到 4 个", "3 至 4 个", "三四个", "三个半", "3 个半", "3-4"):
            self.assertIsNone(parse_int(text), text)

    def test_the_documented_cases_hold(self):
        for text, value in {"第二条": 2, "一共三个": 3, "共 12 行": 12, "大概五个": 5,
                            "十分钟": 10, "3 个，就是三个": 3, "-2": -2}.items():
            self.assertEqual(parse_int(text), value, text)
        for text in ("第二条，共 3 行", "3 或 4", "3.5", "1.6a", "一共", "统一"):
            self.assertIsNone(parse_int(text), text)


# ---------------------------------------------------------------------------
# B2 validate: no false alarms on legitimate lesson text
# ---------------------------------------------------------------------------
class ValidateFalseAlarmTest(unittest.TestCase):
    def tutor(self, line):
        return list(validate._tutor_matches(line))

    def test_the_tutors_own_words_are_not_a_sentence_to_the_tutor(self):
        self.assertEqual(self.tutor("导师会对你说“好，我们继续往下讲”。"), [])
        self.assertEqual(self.tutor("如果导师说“先别急着继续”，就停下。"), [])

    def test_the_learner_speaking_is_still_checked(self):
        self.assertTrue(self.tutor("下次可以对导师说“从 1.6a 继续吧”。"))
        self.assertTrue(self.tutor("跟导师说“从收尾继续”。"))
        # the real hit of lesson 1.15 (line 249) stays
        self.assertTrue(self.tutor("2. 导师说改完以后，对它说“回到上课，我来验收 1.15a”。"))
        self.assertEqual(self.tutor("下次可以对导师说“从 1.6b 继续”。"), [])

    def test_working_tree_in_gits_sense_from_lesson_1_12(self):
        line = "运行 git status：~/Developer/fullstack-from-zero 的工作区是干净的，没有要提交的改动。"
        self.assertEqual(validate._folder_name_problems(line, "1.12"), [])
        self.assertEqual(validate._folder_name_problems(line, "1.14"), [])
        # still flagged: the course-folder sense, and 回到工作区 at any time
        self.assertTrue(validate._folder_name_problems("~/Developer/fullstack-from-zero 的工作区", "1.12"))
        self.assertTrue(validate._folder_name_problems("回到工作区：git 也在这里", "1.12"))
        self.assertTrue(validate._folder_name_problems(line, "1.8"))

    def test_optional_words_in_headings_only_as_a_label(self):
        doc = validate.Doc("# 课\n\n### 自己做（可选的两种做法都行）\n\n### 选做：再练一次\n\n"
                           "### 再练一次（可选）\n")
        found = [title for _i, _level, title in doc.headings
                 if validate._OPTIONAL_IN_HEADING.search(title)]
        self.assertEqual(found, ["选做：再练一次", "再练一次（可选）"])

    def test_a_named_release_says_since_when(self):
        self.assertTrue(validate._since_when("旧教程会写 bash；从 macOS Catalina 起默认是 zsh。"))
        self.assertTrue(validate._since_when("Python 3 以后 print 要加括号。"))
        self.assertFalse(validate._since_when("旧教程会写 bash；现在默认是 zsh。"))

    def test_the_guest_account_is_not_a_user_name(self):
        self.assertEqual(validate._path_problems("`/Users/Guest` 是访客账户。", "0.2"), [])
        self.assertEqual(validate._path_problems("`/Users/Shared` 是共享文件夹。", "0.2"), [])
        self.assertTrue(validate._path_problems("/Users/laowang/Desktop", "0.3"))


# ---------------------------------------------------------------------------
# B3 a state written before lesson_checks existed
# ---------------------------------------------------------------------------
class OldStateLessonCheckTest(Case):
    def setUp(self):
        super().setUp()
        self.lesson("1.6")
        self.lesson("1.7")
        self.pass_lesson("1.6")

    def forget_lesson_checks(self):
        path = self.box.root / "learner" / "state.json"
        state = json.loads(path.read_text(encoding="utf-8"))
        state.pop(next_steps.LESSON_CHECKS, None)
        path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

    def test_the_log_counts_when_the_state_has_no_lesson_checks(self):
        self.forget_lesson_checks()
        self.assertEqual(self.journal_default(), "从 1.7 开始")
        out = self.box.run("status").out
        self.assertNotIn("收尾先做全课检查", out)

    def test_without_a_logged_check_the_closing_steps_come_first(self):
        self.forget_lesson_checks()
        log = self.box.root / "learner" / "log.jsonl"
        lines = [line for line in log.read_text(encoding="utf-8").splitlines()
                 if '"lesson-check"' not in line]
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.assertEqual(self.journal_default(), "从 1.6 的收尾继续")

    def test_logged_lesson_checks_reads_only_passed_checks(self):
        app = self.box.app()
        self.assertIn("1.6", next_steps.logged_lesson_checks(app))
        self.assertEqual(next_steps.logged_lesson_checks(object()), {})


# ---------------------------------------------------------------------------
# L2, B5, B6, B7/L5, L12, L15 a gate seen through an open sitting and the explain-back
# ---------------------------------------------------------------------------
class GateSittingTest(Case):
    gate = "gate-b"

    def setUp(self):
        super().setUp()
        self.lesson("1.9", tasks=1)
        self.lesson("1.10", tasks=1)
        self.lesson("1.11")
        self.pass_lesson("1.9")
        self.pass_lesson("1.10")

    def test_an_open_sitting_is_named_with_grade(self):
        self.box.run("exam", "gate-b", "--seed", "3")
        again = self.box.run("check", "1.10", "--again").out
        self.assertIn("小关卡 gate-b「本地 Git 关卡」第 1 场考试还没批改完（2 题）：做完以后批改："
                      "python3 tools/course.py exam gate-b --grade", again)
        self.assertIn("下次可以对导师说“做小关卡 gate-b”。", again)
        self.assertNotIn("2 道实操题，预计", again)
        # the learner goes on to 1.11: the note line says the same
        self.box.flag("1.11a")
        self.box.run("check", "1.11a")
        notes = self.status_next()
        self.assertIn("小关卡 gate-b「本地 Git 关卡」第 1 场考试还没批改完（2 题），它不挡下一课。"
                      "做完以后批改：python3 tools/course.py exam gate-b --grade", notes)

    def test_where_the_learner_is_matches_the_next_step(self):
        out = self.box.run("status").out
        self.assertIn("你在：小关卡 gate-b「本地 Git 关卡」（学完 1.10 课以后）", out)
        self.assertNotIn("你在：1.11", out)

    def practical_passed(self):
        self.box.run("exam", "gate-b", "--seed", "3")
        self.solve("1.9-x1", "1.10-x1")
        self.assertEqual(self.box.run("exam", "gate-b", "--grade").code, 0)

    def test_a_practice_sitting_does_not_hide_where_the_gate_stands(self):
        self.practical_passed()
        start = self.box.run("exam", "gate-b", "--all", "--seed", "5").out
        self.assertIn("第 2 场 · 加练", start)
        self.assertIn("讲解题还差一次，约 10 分钟：对导师说“请问我 gate-b 的讲解题”。", start)
        self.assertNotIn("实操题都通过以后还有讲解题", start)
        listing = self.box.run("exam").out
        self.assertIn("实操题都通过了，还差讲解题；第 2 场加练还没批改完（2 题）", listing)
        self.box.run("status", "--write")
        text = (self.box.root / "PROGRESS.md").read_text(encoding="utf-8")
        self.assertIn("（1.9 到 1.10 课）：实操题都通过了，还差讲解题；第 2 场加练还没批改完（2 题）", text)
        summary = progress.gate_status(self.box.app().catalog(), self.box.state(), "gate-b")
        self.assertEqual((summary.sitting_kind, summary.next_count), ("practice", 2))
        graded = self.box.run("exam", "gate-b", "--grade").out
        self.assertIn("这是加练：通过的课不会退回去。", graded)

    def test_after_the_explain_back_a_practice_head_has_no_explain_line(self):
        self.practical_passed()
        self.box.run("exam", "gate-b", "--explain", "pass")
        start = self.box.run("exam", "gate-b", "--all", "--seed", "5").out
        self.assertNotIn("讲解题", start)
        self.assertIn("通过了（讲解题 2026-11-19）；第 2 场加练还没批改完（2 题）",
                      self.box.run("exam").out)

    def test_practice_only_is_said_only_in_a_practice_sitting(self):
        # first sitting: 1.9 passed, 1.10 not
        self.box.run("exam", "gate-b", "--seed", "3")
        self.solve("1.9-x1")
        self.box.run("exam", "gate-b", "--grade")
        # a full sitting (kind "again") where 1.10 passes and 1.9 does not
        self.box.run("exam", "gate-b", "--all", "--seed", "6")
        for task in self.box.state()["exam_attempts"]["gate-b"]["tasks"]:
            folder = self.box.playground / "exam-gate-b" / task["id"]
            (folder / "done.ok").unlink() if (folder / "done.ok").exists() else None
        self.solve("1.10-x1")
        graded = self.box.run("exam", "gate-b", "--grade").out
        self.assertIn("实操题都通过了", graded)
        self.assertNotIn("这是加练", graded)

    def test_again_after_pass_says_the_pass_was_taken_back(self):
        self.practical_passed()
        self.box.run("exam", "gate-b", "--explain", "pass")
        again = self.box.run("exam", "gate-b", "--explain", "again").out
        self.assertIn("之前记的是“通过”（2026-11-19），现在改成了“再来一次”：小关卡 gate-b 现在还没通过。",
                      again)
        self.assertIn("讲解题记为“再来一次”", again)
        plain = self.box.run("exam", "gate-b", "--explain", "again").out
        self.assertNotIn("之前记的是", plain)

    def test_pass_before_the_practical_part_says_it_is_kept(self):
        self.box.run("exam", "gate-b", "--seed", "3")
        self.solve("1.9-x1")
        self.box.run("exam", "gate-b", "--grade")
        early = self.box.run("exam", "gate-b", "--explain", "pass").out
        self.assertIn("讲解题的“通过”先记着：等实操题每课都有一题通过，小关卡 gate-b 就通过了。", early)

    def test_explain_values_are_folded_like_gate_ids(self):
        self.practical_passed()
        for value in ("PASS", "ｐａｓｓ", "pass　", " Pass "):
            result = self.box.run("exam", "gate-b", "--explain", value)
            self.assertEqual(result.code, 0, (value, result))
        bad = self.box.run("exam", "gate-b", "--explain", "fail")
        self.assertEqual(bad.code, 64)
        self.assertIn("用法不对：选项 --explain 不能是 fail（可以用的值：pass、again）", bad.err)


# ---------------------------------------------------------------------------
# B9 stray spaces and Chinese punctuation on the command line
# ---------------------------------------------------------------------------
class CommandLineTest(Case):
    def setUp(self):
        super().setUp()
        self.lesson("1.6")
        self.box.flag("1.6a")

    def test_trailing_punctuation_after_an_id(self):
        for typed in ("1.6a，", "1.6a。", "1.6a、", "1.6a."):
            result = self.box.run("check", typed)
            self.assertEqual(result.code, 0, (typed, result))

    def test_a_stray_space_around_an_option(self):
        self.assertEqual(self.box.run("check", "1.6a", "--again ").code, 0)

    def test_an_unknown_word_shows_its_stray_space(self):
        result = self.box.run("check", "1.6a", "x ")
        self.assertEqual(result.code, 64)
        self.assertIn("不认识的参数：x·", result.err)
        self.assertIn("不认识的选项：--wirte", self.box.run("check", "1.6a", "--wirte").err)


# ---------------------------------------------------------------------------
# B11 a gate with more lessons than one sitting holds
# ---------------------------------------------------------------------------
class FullPlanCapTest(unittest.TestCase):
    def test_open_lessons_come_first(self):
        pool = [(f"1.{i}", f"1.{i}-x1") for i in range(1, 9)]
        results = {f"1.{i}-x1": {"result": "pass", "date": "2026-11-19", "attempt": 1}
                   for i in range(1, 7)}
        lessons = [lesson for lesson, _ids in progress.gate_full_plan(pool, results)]
        self.assertIn("1.7", lessons)
        self.assertIn("1.8", lessons)
        self.assertEqual(len(lessons), progress.GATE_MAX_TASKS)
        self.assertEqual(lessons, sorted(lessons, key=lambda x: int(x.split(".")[1])))
        # up to six lessons nothing changes
        small = pool[:5]
        self.assertEqual([lesson for lesson, _ in progress.gate_full_plan(small, results)],
                         ["1.1", "1.2", "1.3", "1.4", "1.5"])


# ---------------------------------------------------------------------------
# B12 the scenario refusal names the id the learner typed
# ---------------------------------------------------------------------------
class ScenarioRefusalIdTest(unittest.TestCase):
    def test_the_refusal_uses_the_typed_id(self):
        box = helpers.Sandbox(self, example=True)
        first = box.run("scenario", "99.1")
        self.assertEqual(first.code, 0, first)
        folder = next(p for p in box.playground.iterdir() if p.name.startswith("99.1"))
        marker = folder / ".playground"
        data = json.loads(marker.read_text(encoding="utf-8"))
        data["scenario"] = "99.1-other"   # the folder holds another build of the tool
        marker.write_text(json.dumps(data), encoding="utf-8")
        result = box.run("scenario", "99.1")
        self.assertIn("工具不会覆盖它", result.text)
        self.assertIn("python3 tools/course.py scenario 99.1 --reset", result.text)
        self.assertNotIn("scenario 99.1-start --reset", result.text)


# ---------------------------------------------------------------------------
# L3 the starter manifest and the file a lesson tells the learner to edit
# ---------------------------------------------------------------------------
class StarterLearnerEditTest(unittest.TestCase):
    def setUp(self):
        self.ws = Path(tempfile.mkdtemp(prefix="starter-fix-"))
        self.addCleanup(__import__("shutil").rmtree, str(self.ws), True)
        for rel, text in (("starter/hello-fx/convert.py", "print(1)\n"),
                          ("starter/my-site/index.html", "<p>hi</p>\n")):
            (self.ws / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.ws / rel).write_text(text, encoding="utf-8")
        self.manifest = self.ws / "manifest.json"
        self.lines = []
        self.assertEqual(self.run_tool("--write"), 0)

    def run_tool(self, *argv):
        return manifest_tool.main(list(argv), workspace=self.ws, manifest=self.manifest,
                                  out=self.lines.append)

    def test_an_edited_convert_py_is_named_apart_and_does_not_count(self):
        (self.ws / "starter/hello-fx/convert.py").write_text("print(2)\n", encoding="utf-8")
        self.lines.clear()
        self.assertEqual(self.run_tool("--check"), 0)
        text = "\n".join(self.lines)
        self.assertIn("课文让学习者自己改的文件，改过不算问题：starter/hello-fx/convert.py", text)
        self.assertNotIn("改动过：starter/hello-fx/convert.py", text)
        # together with a real difference: exit 1, convert.py still apart
        (self.ws / "starter/my-site/index.html").write_text("x\n", encoding="utf-8")
        self.lines.clear()
        self.assertEqual(self.run_tool("--check"), 1)
        text = "\n".join(self.lines)
        self.assertIn("改动过：starter/my-site/index.html", text)
        self.assertIn("--write 只给建课的人用", text)

    def test_restore_refuses_the_learners_exercise_without_force(self):
        path = self.ws / "starter/hello-fx/convert.py"
        path.write_text("print(2)\n", encoding="utf-8")
        with mock.patch.object(sys, "stderr", new=__import__("io").StringIO()) as err:
            self.assertEqual(self.run_tool("--restore", "starter/hello-fx/convert.py"), 2)
        self.assertIn("课文让学习者自己改的文件", err.getvalue())
        self.assertEqual(path.read_text(encoding="utf-8"), "print(2)\n")
        self.assertEqual(self.run_tool("--restore", "starter/hello-fx/convert.py", "--force"), 0)
        self.assertEqual(path.read_text(encoding="utf-8"), "print(1)\n")
        self.assertTrue((self.ws / "starter/hello-fx/convert.py.changed").is_file())


# ---------------------------------------------------------------------------
# L8 the return sentence in the fixed quotation marks
# ---------------------------------------------------------------------------
class ReturnSentenceTest(unittest.TestCase):
    def test_full_width_double_quotes(self):
        for text in (next_steps.TEXT["away_long"], review_command.TEXT["return_tutor"]):
            self.assertIn("对导师说“我回来了，带我走回归流程”。", text)
            self.assertNotIn("「我回来了", text)


# ---------------------------------------------------------------------------
# B10/L11, L10 doctor: the entrance outside the synced case; no future tense
# ---------------------------------------------------------------------------
@unittest.skipUnless(envstubs.REAL_GIT, "git is not installed")
class DoctorFixTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.bin = envstubs.FakeBin(self.box.base / "bin").learner_machine()
        self.xattr = envstubs.xattr_stub(self.box.base / "xattr-bin")
        patcher = mock.patch.object(doctor, "XATTR", str(self.xattr))
        patcher.start()
        self.addCleanup(patcher.stop)
        envstubs.make_sim_home.write_home(self.box.home, identity=True, signing=True)

    def state(self, data):
        folder = self.box.root / "learner"
        folder.mkdir(exist_ok=True)
        (folder / "state.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def lines(self):
        result = self.box.run("doctor", PATH=str(self.bin), SHELL=str(self.bin.path / "zsh"),
                              TERM="xterm-256color")
        self.assertNotIn("Traceback", result.text)
        return [line[4:] for line in result.out.splitlines() if line.startswith("  - ")]

    def line(self, start):
        found = [line for line in self.lines() if line.startswith(start)]
        self.assertEqual(len(found), 1, found)
        return found[0]

    def passed(self, *lessons):
        from courselib import syllabus
        stations = {station: {"status": "passed", "first_pass": "2026-11-19T10:00:00"}
                    for lesson in lessons for station in syllabus.lesson_entry(lesson)["stations"]}
        return stations

    def test_a_broken_entrance_of_a_folder_that_is_not_synced(self):
        self.state({"schema": 1, "decisions": {"workspace_location": "stay-in-sync"}})
        entrance = self.box.home / "Developer" / "fullstack-from-zero"
        entrance.symlink_to(self.box.base / "nowhere")
        text = self.line("学习工作区的位置：")
        self.assertIn("不在同步到云端的文件夹里。这是你在第 0.2 课做的决定：先留在原处。"
                      "~/Developer/fullstack-from-zero 有一个入口，但它没有通到这个学习工作区", text)
        self.assertTrue(text.endswith("→ 对导师说“我先不搬，帮我在 ~/Developer 建一个入口”"), text)
        self.assertNotIn("第 1.12 课", text)
        entrance.unlink()
        text = self.line("学习工作区的位置：")
        self.assertIn("~/Developer/fullstack-from-zero 这个入口还没有建", text)

    def test_before_lesson_0_2_a_missing_entrance_is_not_named(self):
        text = self.line("学习工作区的位置：")
        self.assertNotIn("入口", text)
        self.assertTrue(text.endswith("不在同步到云端的文件夹里。"), text)

    def test_pointers_after_the_lesson_is_done(self):
        # the sim gitconfig: commit.gpgsign=true, gpg.format=openpgp, no gpg
        before = self.line("提交签名：")
        self.assertIn("→ 第 1.6 课会带你处理", before)
        self.state({"schema": 1, "stations": self.passed("1.6")})
        after = self.line("提交签名：")
        self.assertIn("→ 第 1.6 课已经学过了，把这一行发给导师", after)
        self.assertNotIn("会带你处理", after)

    def test_the_stayed_learner_after_lesson_1_12(self):
        envstubs.xattr_stub(self.box.base / "xattr-bin", flagged=[self.box.base])
        (self.box.home / "Developer" / "fullstack-from-zero").symlink_to(self.box.root)
        self.state({"schema": 1, "decisions": {"workspace_location": "stay-in-sync"},
                    "stations": self.passed("1.12")})
        text = self.line("学习工作区的位置：")
        self.assertIn("→ 第 1.12 课已经问过你了；想搬的时候对导师说“帮我把课程安置到 ~/Developer”", text)


# ---------------------------------------------------------------------------
# L13 the simulation home carries the course's own skeletons
# ---------------------------------------------------------------------------
class SimHomeSkeletonTest(unittest.TestCase):
    def test_skeletons_without_the_learners_lines(self):
        base = Path(tempfile.mkdtemp(prefix="skeleton-"))
        self.addCleanup(__import__("shutil").rmtree, str(base), True)
        source, target = base / "src", base / "dst"
        (source / "notes").mkdir(parents=True)
        (source / "journal").mkdir()
        (source / "journal" / "README.md").write_text("日志说明\n", encoding="utf-8")
        (source / "journal" / "2026-11-19.md").write_text("我的日志\n", encoding="utf-8")
        (source / "notes" / "my-rules.md").write_text(
            "# 我的行规笔记\n\n说明\n\n## 0.1 第一次动手\n\n### META-01 遇到报错先问三件事\n"
            "我自己写的一句话\n", encoding="utf-8")
        target.mkdir()
        make_sim_home.copy_skeletons(source, target)
        self.assertEqual((target / "journal" / "README.md").read_text(encoding="utf-8"), "日志说明\n")
        self.assertFalse((target / "journal" / "2026-11-19.md").exists())
        notes = (target / "notes" / "my-rules.md").read_text(encoding="utf-8")
        self.assertIn("### META-01 遇到报错先问三件事", notes)
        self.assertIn("说明", notes)
        self.assertNotIn("我自己写的一句话", notes)


# ---------------------------------------------------------------------------
# B8/L7 one gate naming in the landing line too
# ---------------------------------------------------------------------------
class LandingNameTest(Case):
    def test_landing_line_uses_the_gate_label(self):
        self.lesson("1.4")
        self.lesson("1.5", tasks=1)
        out = self.box.run("status").out
        self.assertIn("下一个落脚点是小关卡 gate-a「终端与文档关卡」（学完 1.5），还有", out)
        self.assertNotIn("终端与文档关卡 gate-a", out)
        self.assertFalse(re.search(r"「[^」]*「", out.split("下一个落脚点")[1].splitlines()[0][:3]))


class WrapupHereTest(Case):
    def test_the_here_line_names_the_closing_steps(self):
        self.lesson("1.6")
        self.lesson("1.7")
        for station in ("1.6a", "1.6b", "1.6c"):
            self.box.flag(station)
            self.box.run("check", station)
        out = self.box.run("status").out
        self.assertIn("你在：1.6 ", out)
        self.assertIn(" · 收尾", out)
        self.assertNotIn("你在：1.7", out)


if __name__ == "__main__":
    unittest.main()
