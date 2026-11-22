"""The worked example (docs/authoring/example-lesson) used end to end, as an author would."""

import unittest

import helpers
from courselib import runner, scenario


class ExampleLessonTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self, example=True)
        self.app = self.box.app()
        self.lesson = self.app.catalog().lesson("99.1")

    def test_it_loads_with_every_part_of_the_api(self):
        lesson = self.lesson
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson.station_ids, ["99.1a", "99.1b"])
        self.assertEqual(sorted(lesson.checks), ["99.1a", "99.1b"])
        self.assertTrue(all(len(lesson.hints[s]) == 4 for s in lesson.station_ids))
        self.assertEqual({item["type"] for item in lesson.review}, {"recall", "which", "do"})
        self.assertIn("start", lesson.scenarios)
        self.assertEqual(len(lesson.exam), 1)

    def test_quiz_station(self):
        right = self.box.run("check", "99.1a", "--answer", "B", "--answer", "ｂ", noninteractive=True)
        self.assertEqual(right.code, 0, right)
        self.assertIn("选对了", right.out)
        self.assertIn("提交只发生在你自己的电脑上", right.out)
        wrong = self.box.run("check", "99.1a", "--answer", "A", "--answer", "B",
                             noninteractive=True)
        self.assertEqual(wrong.code, 1, wrong)
        self.assertIn("提交不需要联网", wrong.out)
        self.assertNotIn("带说明的快照）", wrong.out.split("还差")[1])
        self.assertIn("这一站之前已经通过", wrong.out)
        self.assertEqual(self.box.state()["stations"]["99.1a"]["status"], "passed")

    def test_hands_on_station_with_an_ask_question(self):
        missing = self.box.run("check", "99.1b", "--answer", "3", noninteractive=True)
        self.assertEqual(missing.code, 1, missing)
        self.assertIn("python3 tools/course.py scenario 99.1-start", missing.out)

        info = self.box.build_scenario("99.1", seed=7)
        repo = info.path / info.facts["repo"]
        count = info.facts["commits"]
        self.assertTrue(2 <= count <= 4)
        self.assertIn("练习仓库在这里：~/Developer/playground/99.1-start/", "\n".join(info.todo))

        before = self.box.run("check", "99.1b", "--answer", str(count), noninteractive=True)
        self.assertEqual(before.code, 1, before)
        self.assertIn("这个文件要存在", before.out)
        self.assertIn("还没有新的提交", before.out)
        self.assertNotIn("问：", before.out, "the question waits until the work is there")

        (repo / "README.md").write_text("# 我的笔记\n", encoding="utf-8")
        self.box.git(repo, "add", "README.md")
        self.box.git(repo, "commit", "-q", "-m", "docs: 添加说明")
        wrong = self.box.run("check", "99.1b", "--answer", str(count + 1), noninteractive=True)
        self.assertEqual(wrong.code, 1, wrong)
        self.assertIn(f"你的回答是「{count + 1}」", wrong.out)
        self.assertNotIn("应该是", wrong.out)
        right = self.box.run("check", "99.1b", "--answer", f"{count} 个",
                             noninteractive=True)
        self.assertEqual(right.code, 0, right)
        self.assertIn("答对了", right.out)
        self.assertIn("数的时候别忘了", right.out)

    def test_four_hint_levels(self):
        for level in range(1, 5):
            result = self.box.run("hint", "99.1b", noninteractive=True)
            self.assertIn(f"提示 {level}/4", result.out)
        self.assertEqual(self.box.state()["stations"]["99.1b"]["status"], "assisted")

    def test_do_review_item_is_graded_on_its_own_copy(self):
        lesson = self.lesson
        item = next(item for item in lesson.review if item["type"] == "do")
        info = scenario.build(self.app, lesson.scenarios[item["scenario"]], "review/" + item["id"],
                              scenario_id=item["id"], key=item["scenario"], lesson_id=lesson.id,
                              seed=3, reset=True)
        first = runner.run_check(self.app, item["check"], lesson=lesson, scenario=info,
                                 state={})
        self.assertEqual(first.outcome, runner.NOT_YET, first.to_dict())
        repo = info.path / info.facts["repo"]
        (repo / "README.md").write_text("# 复习\n", encoding="utf-8")
        self.box.git(repo, "add", "-A")
        self.box.git(repo, "commit", "-q", "-m", "docs: 复习")
        second = runner.run_check(self.app, item["check"], lesson=lesson, scenario=info, state={})
        self.assertEqual(second.outcome, runner.PASSED, second.to_dict())
        self.assertFalse((self.box.playground / "99.1-start").exists(),
                         "the learner's own station folder is not used")

    def test_exam_task_in_both_forms(self):
        lesson = self.lesson
        task = lesson.exam[0]
        for form in ("A", "B"):
            with self.subTest(form=form):
                info = scenario.build(self.app, task["build"], "exam-example/" + form,
                                      scenario_id=task["id"], lesson_id=lesson.id, seed=11,
                                      form=form, reset=True)
                text = scenario.fill_text(self.app, task["task"][form], info)
                self.assertNotIn("{", text)
                self.assertIn("~/Developer/playground/exam-example/" + form, text)
                cold = runner.run_check(self.app, task["grade"], lesson=lesson, scenario=info)
                self.assertEqual(cold.outcome, runner.NOT_YET)
                repo = info.path / info.facts["repo"]
                if form == "A":
                    (repo / info.facts["file"]).write_text("一行字\n", encoding="utf-8")
                else:
                    page = (repo / "index.html").read_text(encoding="utf-8")
                    (repo / "index.html").write_text(page.replace("旧标题", info.facts["title"]),
                                                     encoding="utf-8")
                self.box.git(repo, "add", "-A")
                self.box.git(repo, "commit", "-q", "-m", "docs: 考试")
                done = runner.run_check(self.app, task["grade"], lesson=lesson, scenario=info)
                self.assertEqual(done.outcome, runner.PASSED, done.to_dict())

    def test_seed_changes_names_and_counts(self):
        seen = set()
        for seed in range(1, 12):
            info = scenario.build(self.app, self.lesson.scenarios["start"], f"seed-{seed}",
                                  seed=seed, log=False)
            seen.add((info.facts["repo"], info.facts["commits"]))
        self.assertGreater(len(seen), 3)


if __name__ == "__main__":
    unittest.main()
