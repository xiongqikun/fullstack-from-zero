"""The ``journal`` command: appends to the learner's own file, never rewrites it."""

import unittest

import helpers


class JournalTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.box.add_syllabus_lesson("1.6")
        self.file = self.box.root / "journal" / "2026-11-19.md"

    def text(self):
        return self.file.read_text(encoding="utf-8")

    def test_entry_from_flags(self):
        result = self.box.run("journal", "--done", "做完了 1.6a", "--stuck", "引号打成了全角",
                              "--next", "从 1.6b 继续", noninteractive=True,
                              now="2026-11-19T21:05:00")
        self.assertEqual(result.code, 0)
        self.assertIn("已记到 journal/2026-11-19.md。", result.out)
        self.assertEqual(self.text(), (
            "# 学习日志 2026-11-19\n"
            "\n"
            "## 21:05\n"
            "\n"
            "- 做了什么：做完了 1.6a\n"
            "- 卡在哪：引号打成了全角\n"
            "- 下次从哪开始：从 1.6b 继续\n"))
        event = self.box.events("journal")[0]
        self.assertEqual(event["file"], "journal/2026-11-19.md")
        self.assertEqual(event["fields"], ["done", "stuck", "next"])

    def test_optional_fourth_and_fifth_fields(self):
        self.box.run("journal", "--done", "读了课文", "--unclear", "暂存区是什么",
                     "--slow", "打字", noninteractive=True)
        text = self.text()
        self.assertIn("- 卡在哪：（无）\n", text)
        self.assertIn("- 下次从哪开始：（无）\n", text)
        self.assertIn("- 哪里看不懂：暂存区是什么\n", text)
        self.assertIn("- 哪里太慢：打字\n", text)

    def pass_station(self, station):
        self.box.flag(station)
        self.assertEqual(self.box.run("check", station).code, 0)

    def default_next(self):
        result = self.box.run("journal", inputs=["读了课文", "", "", "", ""])
        self.assertEqual(result.code, 0, result)
        prompt = next(line for line in result.out.splitlines() if line.startswith("下次从哪开始"))
        return prompt[prompt.index("（") + 1:prompt.index("）")]

    def test_prompts_when_flags_are_absent(self):
        self.pass_station("1.6a")
        result = self.box.run("journal", inputs=["做完了第一站", "", "", "看不懂 HEAD", ""],
                              now="2026-11-19T21:30:00")
        self.assertEqual(result.code, 0)
        for prompt in ("做了什么（一句话）：", "卡在哪（没有就直接回车）：",
                       "下次从哪开始（直接回车 = 从 1.6b 继续）：",
                       "哪里看不懂（可选，直接回车跳过）：", "哪里太慢（可选，直接回车跳过）："):
            self.assertIn(prompt, result.out)
        text = self.text()
        self.assertIn("- 做了什么：做完了第一站\n", text)
        self.assertIn("- 卡在哪：（无）\n", text)
        self.assertIn("- 下次从哪开始：从 1.6b 继续\n", text)
        self.assertIn("- 哪里看不懂：看不懂 HEAD\n", text)
        self.assertNotIn("哪里太慢", text)

    def test_the_default_is_the_canonical_sentence_of_the_next_step(self):
        # E2: the same answer as check and status.  Before: 「从 1.7a 继续」
        # right after the last station, which skipped the closing steps.
        self.box.add_syllabus_lesson("1.7")
        self.assertEqual(self.default_next(), "直接回车 = 开始上课")
        for station in ("1.6a", "1.6b", "1.6c"):
            self.pass_station(station)
        self.assertEqual(self.default_next(), "直接回车 = 从 1.6 的收尾继续")
        self.assertEqual(self.box.run("check", "1.6").code, 0)
        self.assertEqual(self.default_next(), "直接回车 = 从 1.7 开始")
        self.pass_station("1.7b")
        self.assertEqual(self.default_next(), "直接回车 = 从 1.7a 继续")
        self.pass_station("1.7a")
        self.box.run("check", "1.7")
        self.assertEqual(self.default_next(), "直接回车 = 准备阶段 2")

    def test_with_done_given_nothing_is_asked(self):
        # Regression (tester novice-abuse): with --done given, an end-of-file
        # at a follow-up prompt used to discard the text given in the flags.
        result = self.box.run("journal", "--done", "做完了", "--next", "|表格|", inputs=[])
        self.assertEqual(result.code, 0, result)
        self.assertNotIn("卡在哪（", result.out)
        self.assertNotIn("哪里看不懂", result.out)
        self.assertIn("- 做了什么：做完了\n- 卡在哪：（无）\n- 下次从哪开始：|表格|\n",
                      self.text())

    def test_entries_are_appended_and_learner_text_is_kept(self):
        self.box.run("journal", "--done", "上午学了一站", noninteractive=True,
                     now="2026-11-19T09:00:00")
        with open(str(self.file), "a", encoding="utf-8") as handle:
            handle.write("\n我自己加的一段话，没有换行结尾")
        before = self.text()
        self.box.run("journal", "--done", "晚上又学了一站", noninteractive=True,
                     now="2026-11-19T21:00:00")
        after = self.text()
        self.assertTrue(after.startswith(before))
        self.assertEqual(after.count("# 学习日志 2026-11-19"), 1)
        self.assertIn("没有换行结尾\n\n## 21:00\n\n- 做了什么：晚上又学了一站\n", after)

    def test_one_file_per_day(self):
        self.box.run("journal", "--done", "第一天", noninteractive=True, now="2026-11-19T21:00:00")
        self.box.run("journal", "--done", "第二天", noninteractive=True, now="2026-11-20T21:00:00")
        names = sorted(path.name for path in (self.box.root / "journal").iterdir())
        self.assertEqual(names, ["2026-11-19.md", "2026-11-20.md"])

    def test_values_become_one_line(self):
        self.box.run("journal", "--done", "第一行\n第二行\t\t尾巴  ", noninteractive=True)
        self.assertIn("- 做了什么：第一行 第二行 尾巴\n", self.text())

    def test_no_prompt_mode_needs_done(self):
        result = self.box.run("journal", "--stuck", "x", noninteractive=True)
        self.assertEqual(result.code, 64)
        self.assertIn("--done", result.err)
        self.assertFalse(self.file.exists())

    def test_empty_done_writes_nothing(self):
        result = self.box.run("journal", inputs=["", "  ", "", ""])
        self.assertEqual(result.code, 1)
        self.assertIn("没有写内容", result.out)
        self.assertFalse(self.file.exists())

    def test_leaving_a_prompt_is_polite_and_writes_nothing(self):
        for inputs in ([], ["做了点事"], [KeyboardInterrupt]):
            result = self.box.run("journal", inputs=inputs)
            self.assertEqual(result.code, 1, inputs)
            self.assertIn("已取消", result.out)
            self.assertNotIn("Traceback", result.text)
        self.assertFalse(self.file.exists())

    def test_journal_counts_as_study_time(self):
        self.box.run("check", "1.6a", now="2026-11-19T20:00:00")
        self.box.run("journal", "--done", "收工", noninteractive=True, now="2026-11-19T20:30:00")
        self.assertEqual(self.box.state()["sessions"][-1]["minutes"], 30)

    def test_a_file_where_the_folder_should_be_is_a_tool_problem(self):
        (self.box.root / "journal").write_text("oops")
        result = self.box.run("journal", "--done", "x", noninteractive=True)
        self.assertEqual(result.code, 2)
        self.assertIn("检查器出问题", result.out)
        self.assertNotIn("Traceback", result.text)


if __name__ == "__main__":
    unittest.main()
