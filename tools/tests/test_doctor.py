"""The ``doctor`` command, in a simulation home with fake programs on PATH.

Nothing here reads the real home, the real Git configuration or the network:
HOME is the sandbox's home (with the .gitconfig of plan G8 written by
tools/dev/make_sim_home.py), PATH holds only stub programs, the attribute
reader /usr/bin/xattr is replaced by a stub, and --net uses a fake opener.
"""

import json
import os
import shutil
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

import envstubs
import helpers

from courselib.commands import doctor

SIM = envstubs.make_sim_home


@unittest.skipUnless(envstubs.REAL_GIT, "git is not installed")
class DoctorTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.bin = envstubs.FakeBin(self.box.base / "bin").learner_machine()
        self.xattr = envstubs.xattr_stub(self.box.base / "xattr-bin")
        patcher = mock.patch.object(doctor, "XATTR", str(self.xattr))
        patcher.start()
        self.addCleanup(patcher.stop)

    # -- running ------------------------------------------------------------
    def home(self, identity=True, signing=True, extra=""):
        SIM.write_home(self.box.home, identity=identity, signing=signing)
        if extra:
            with open(str(self.box.home / ".gitconfig"), "a", encoding="utf-8") as handle:
                handle.write(extra)

    def doctor(self, *argv, **env):
        values = {"PATH": str(self.bin), "SHELL": str(self.bin.path / "zsh"),
                  "TERM": "xterm-256color"}
        values.update(env)
        result = self.box.run("doctor", *argv, **values)
        self.assertNotIn("Traceback", result.text)
        return result

    def groups(self, result):
        """{"ok": [...], "todo": [...], "info": [...]} from the printed report."""
        found = {"ok": [], "todo": [], "info": []}
        current = None
        heads = {"没问题": "ok", "需要处理": "todo", "仅提示": "info"}
        for line in result.out.splitlines():
            for word, key in heads.items():
                if line.lstrip("✅⚠️ ").startswith(word + "（"):
                    current = key
            if current and line.startswith("  - "):
                found[current].append(line[4:])
        return found

    def line(self, result, group, start):
        lines = [text for text in self.groups(result)[group] if text.startswith(start)]
        self.assertEqual(len(lines), 1, (
            f"no single {group} line starting {start!r} in\n{result.out}"))
        return lines[0]

    def assert_no_secrets(self, result):
        stored = (self.box.root / "learner" / "last-result.json").read_text(encoding="utf-8")
        for secret in envstubs.SECRETS:
            self.assertNotIn(secret, result.text)
            self.assertNotIn(secret, stored)

    # -- regressions (tester novice-abuse) ------------------------------------
    def test_a_broken_gitconfig_is_named_not_blamed_on_missing_tools(self):
        self.home(extra="[core\n bad = \n")
        result = self.doctor()
        line = self.line(result, "todo", "Git：")
        self.assertIn("设置文件有一行写坏了", line)
        self.assertNotIn("Command Line Tools", line)
        self.assertNotIn(str(self.box.home), result.text)

    def test_an_editor_that_edits_nothing_is_flagged(self):
        self.home()
        result = self.doctor(GIT_EDITOR="true")
        self.assertIn("不是一个真正的编辑器", self.line(result, "info", "Git 的编辑器"))

    # -- the common bad case of plan G7 (the reference Mac) -------------------
    def test_learner_machine_signing_on_without_gpg(self):
        self.home()
        before = (self.box.home / ".gitconfig").read_bytes()
        result = self.doctor()
        self.assertEqual(result.code, 0, result)
        self.assertTrue(result.out.startswith("环境检查 · 2026-11-19\n"))
        signing = self.line(result, "todo", "提交签名：")
        self.assertIn("找不到签名程序 gpg", signing)
        self.assertIn("→ 第 1.6 课会带你处理", signing)
        self.assertIn("user.name 已设置，user.email 已设置",
                      self.line(result, "ok", "Git 身份："))
        self.line(result, "ok", "macOS 版本：27.2.1")
        self.line(result, "ok", "登录用的 shell：zsh 5.9")
        self.line(result, "ok", "python3：3.14.9")
        self.line(result, "ok", "Git：")
        self.line(result, "ok", "全局忽略文件：有（~/.gitignore_global）")
        self.line(result, "ok", "code 命令：有")
        self.line(result, "ok", "~/Developer 文件夹：有")
        self.line(result, "ok", "学习工作区的位置：")
        self.assertIn("第 1.11 课", self.line(result, "info", "GitHub CLI（gh）：还没安装"))
        self.line(result, "info", "能不能连上 github.com：这次没有检查")
        self.assert_no_secrets(result)
        # read-only: the configuration is untouched, no state file appeared
        self.assertEqual((self.box.home / ".gitconfig").read_bytes(), before)
        self.assertFalse((self.box.root / "learner" / "state.json").exists())
        self.assertEqual(sorted(p.name for p in (self.box.root / "learner").iterdir()),
                         ["last-result.json"])

    def test_last_result_for_the_tutor(self):
        self.home()
        self.doctor()
        record = self.box.last_result()
        self.assertEqual(record["kind"], "doctor")
        self.assertEqual(record["ts"], "2026-11-19T10:00:00")
        self.assertFalse(record["net"])
        by_key = {item["key"]: item for item in record["findings"]}
        self.assertEqual(by_key["git.signing"]["group"], "todo")
        self.assertEqual(by_key["git.signing"]["lesson"], "1.6")
        self.assertEqual(by_key["git.identity"]["group"], "ok")
        self.assertEqual(record["counts"]["todo"],
                         len([i for i in record["findings"] if i["group"] == "todo"]))
        text = json.dumps(record, ensure_ascii=False)
        self.assertNotIn(str(self.box.home), text)

    def test_signing_on_with_a_gpg_program(self):
        self.home()
        self.bin.prints("gpg", "gpg (GnuPG) 2.4.9")
        result = self.doctor()
        self.assertIn("签名程序 gpg 找到了", self.line(result, "ok", "提交签名："))
        self.assertEqual(self.groups(result)["todo"], [])
        self.assertIn("小结：没有需要处理的事。", result.out)
        self.assert_no_secrets(result)

    def test_signing_program_named_by_path(self):
        self.home(extra="[gpg]\n\tprogram = /nowhere/bin/gpg2\n")
        self.bin.prints("gpg", "gpg (GnuPG) 2.4.9")
        result = self.doctor()
        self.assertIn("找不到签名程序 /nowhere/bin/gpg2", self.line(result, "todo", "提交签名："))

    def test_signing_off(self):
        self.home(signing=False)
        result = self.doctor()
        self.line(result, "ok", "提交签名：没有打开")

    def test_ssh_signing(self):
        self.home(extra="[gpg]\n\tformat = ssh\n[user]\n\tsigningkey = ~/.ssh/id_ed25519.pub\n")
        # the common bad case of plan G7: gpg.ssh.program present with an empty value
        empty = self.doctor()
        text = self.line(empty, "todo", "提交签名：")
        self.assertIn("设置 gpg.ssh.program 是空的", text)
        self.assertIn("→ 第 1.11 课会带你处理", text)
        with open(str(self.box.home / ".gitconfig"), "a", encoding="utf-8") as handle:
            handle.write('[gpg "ssh"]\n\tprogram = ssh-keygen\n')
        no_keygen = self.doctor()
        text = self.line(no_keygen, "todo", "提交签名：")
        self.assertIn("找不到签名程序 ssh-keygen", text)
        self.assertIn("→ 第 1.11 课会带你处理", text)
        self.bin.prints("ssh-keygen", "usage: ssh-keygen ...", code=1)
        missing = self.doctor()
        text = self.line(missing, "todo", "提交签名：")
        self.assertIn("~/.ssh/id_ed25519.pub 不存在", text)
        # E7: choosing and setting up SSH signing is lesson 1.11, not 1.6
        self.assertIn("→ 第 1.11 课会带你处理", text)
        (self.box.home / ".ssh").mkdir()
        (self.box.home / ".ssh" / "id_ed25519.pub").write_text("ssh-ed25519 AAAA test\n",
                                                               encoding="utf-8")
        present = self.doctor()
        self.line(present, "ok", "提交签名：已经打开（格式 ssh），签名程序和钥匙都找到了")

    def test_an_empty_gpg_program_is_named(self):
        self.home(extra="[gpg]\n\tprogram = \n")
        self.bin.prints("gpg", "gpg (GnuPG) 2.4.9")
        text = self.line(self.doctor(), "todo", "提交签名：")
        self.assertIn("已经打开（commit.gpgsign=true，格式 openpgp），但设置 gpg.program 是空的", text)
        self.assertIn("现在每次 git commit 都会失败", text)
        # handling the failing gpg setup is lesson 1.6
        self.assertIn("→ 第 1.6 课会带你处理", text)

    def test_ssh_signing_without_a_key(self):
        SIM.write_home(self.box.home, signing=False)
        with open(str(self.box.home / ".gitconfig"), "a", encoding="utf-8") as handle:
            handle.write("[commit]\n\tgpgsign = true\n[gpg]\n\tformat = ssh\n")
        self.bin.prints("ssh-keygen", "usage", code=1)
        result = self.doctor()
        text = self.line(result, "todo", "提交签名：")
        self.assertIn("已经打开（commit.gpgsign=true，格式 ssh），但没有设置用哪把钥匙", text)
        self.assertIn("→ 第 1.11 课会带你处理", text)
        record = {i["key"]: i for i in self.box.last_result()["findings"]}
        self.assertEqual(record["git.signing"]["lesson"], "1.11")

    # -- identity -----------------------------------------------------------
    def test_identity_absent(self):
        self.home(identity=False)
        result = self.doctor()
        self.assertEqual(result.code, 0)
        text = self.line(result, "todo", "Git 身份：")
        self.assertIn("user.name 未设置，user.email 未设置", text)
        # what Git 2.54 really does without an identity (verified in a simulation
        # home): it composes one from the account and computer name and commits
        self.assertNotIn("没有身份就不能提交", text)
        self.assertIn("Git 会拿这台 Mac 的账户名和电脑名自己拼一个", text)
        self.assertIn("提交照样能成功", text)
        self.assertIn("→ 第 1.6 课会带你正式设好", text)
        record = {i["key"]: i for i in self.box.last_result()["findings"]}
        self.assertEqual(record["git.identity"]["lesson"], "1.6")
        self.assert_no_secrets(result)

    def test_identity_half_set_never_prints_the_value(self):
        self.box.write_gitconfig("[user]\n\temail = only-me@example.invalid\n")
        result = self.doctor()
        self.assertIn("user.name 未设置，user.email 已设置",
                      self.line(result, "todo", "Git 身份："))
        stored = (self.box.root / "learner" / "last-result.json").read_text(encoding="utf-8")
        self.assertNotIn("only-me", result.text + stored)

    # -- editor and default branch -------------------------------------------
    def test_vi_is_the_editor_when_nothing_is_set(self):
        self.home()
        result = self.doctor()
        text = self.line(result, "info", "Git 的编辑器：vi")
        self.assertIn("第 1.6 课会把它换掉", text)
        # Without a real terminal Git will not name vi by itself; the doctor asks again.
        dumb = self.doctor(TERM="dumb")
        self.line(dumb, "info", "Git 的编辑器：vi")

    def test_other_editors(self):
        self.home(extra='[core]\n\teditor = code --wait\n')
        self.line(self.doctor(), "ok", "Git 的编辑器：code --wait")
        self.home()
        self.line(self.doctor(EDITOR="vim"), "info", "Git 的编辑器：vim")

    def test_default_branch(self):
        self.home()
        # GIT_CONFIG_NOSYSTEM=1 hides Xcode's system file, so Git's own default shows.
        master = self.doctor()
        self.assertIn("课程的例子里写的是 main", self.line(master, "info", "新仓库的第一个分支名：master"))
        self.home(extra="[init]\n\tdefaultBranch = main\n")
        self.line(self.doctor(), "ok", "新仓库的第一个分支名：main")

    def test_global_excludes_file(self):
        self.home()
        (self.box.home / ".gitignore_global").unlink()
        self.assertIn("不存在", self.line(self.doctor(), "info", "全局忽略文件："))
        SIM.write_home(self.box.home, identity=True, signing=True)
        text = (self.box.home / ".gitconfig").read_text(encoding="utf-8")
        self.box.write_gitconfig(text.replace("[core]\n\texcludesfile = ~/.gitignore_global\n", ""))
        self.assertIn("第 1.9 课", self.line(self.doctor(), "info", "全局忽略文件：没有"))
        (self.box.home / ".config" / "git").mkdir(parents=True)
        (self.box.home / ".config" / "git" / "ignore").write_text("*.tmp\n", encoding="utf-8")
        self.assertIn("Git 默认的位置", self.line(self.doctor(), "ok", "全局忽略文件：有"))

    # -- where the workspace lives ------------------------------------------
    def test_workspace_under_an_icloud_folder(self):
        self.home()
        self.xattr = envstubs.xattr_stub(self.box.base / "xattr-bin", flagged=[self.box.base])
        result = self.doctor()
        text = self.line(result, "todo", "学习工作区的位置：")
        self.assertIn(f"在 iCloud 同步的文件夹里（{self.box.base}）", text)
        self.assertIn("→ 第 0.2 课会带你处理", text)
        record = {i["key"]: i for i in self.box.last_result()["findings"]}
        self.assertEqual((record["workspace"]["group"], record["workspace"]["lesson"]),
                         ("todo", "0.2"))

    def state(self, data):
        folder = self.box.root / "learner"
        folder.mkdir(exist_ok=True)
        path = folder / "state.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_a_decision_to_stay_in_the_synced_folder_is_named_with_lesson_1_12(self):
        self.home()
        envstubs.xattr_stub(self.box.base / "xattr-bin", flagged=[self.box.base])
        path = self.state({"schema": 1, "decisions": {"workspace_location": "stay-in-sync"}})
        before = path.read_bytes()
        (self.box.home / "Developer" / "fullstack-from-zero").symlink_to(self.box.root)
        result = self.doctor()
        text = self.line(result, "todo", "学习工作区的位置：")
        # The real place, never the entrance (E1b).
        self.assertTrue(text.startswith(f"学习工作区的位置：{self.box.root}，"), text)
        self.assertIn("~/Developer/fullstack-from-zero 是通往它的入口，课文里的 cd ~/Developer/fullstack-from-zero "
                      "照样能用；学习工作区本身还在同步盘里。这是你在第 0.2 课做的决定：先留在原处。", text)
        self.assertIn("→ 第 1.12 课把课程变成仓库之前，会再问你一次", text)
        self.assertNotIn("第 0.2 课会带你处理", text)
        record = {i["key"]: i for i in self.box.last_result()["findings"]}
        self.assertEqual((record["workspace"]["group"], record["workspace"]["lesson"]),
                         ("todo", "1.12"))
        self.assertEqual(path.read_bytes(), before)            # read only

    def stay_in_sync(self):
        self.home()
        envstubs.xattr_stub(self.box.base / "xattr-bin", flagged=[self.box.base])
        self.state({"schema": 1, "decisions": {"workspace_location": "stay-in-sync"}})
        return self.box.home / "Developer" / "fullstack-from-zero"

    def test_staying_without_the_entrance_names_the_sentence_for_the_tutor(self):
        self.stay_in_sync()
        result = self.doctor()
        text = self.line(result, "todo", "学习工作区的位置：")
        self.assertIn("这是你在第 0.2 课做的决定：先留在原处。~/Developer/fullstack-from-zero 这个入口还没有建，"
                      "课文里的 cd ~/Developer/fullstack-from-zero 现在走不通。", text)
        self.assertIn("第 1.12 课把课程变成仓库之前，会再问你一次要不要搬。", text)
        self.assertTrue(text.endswith("→ 对导师说“我先不搬，帮我在 ~/Developer 建一个入口”"), text)
        record = {i["key"]: i for i in self.box.last_result()["findings"]}
        self.assertEqual(record["workspace"]["lesson"], "0.2")

    def test_staying_with_a_broken_or_wrong_entrance(self):
        entrance = self.stay_in_sync()
        entrance.symlink_to(self.box.base / "nowhere")            # a broken link
        text = self.line(self.doctor(), "todo", "学习工作区的位置：")
        self.assertIn("~/Developer/fullstack-from-zero 有一个入口，但它没有通到这个学习工作区", text)
        self.assertIn("→ 对导师说“我先不搬，帮我在 ~/Developer 建一个入口”", text)
        entrance.unlink()
        other = self.box.base / "other"
        other.mkdir()
        entrance.symlink_to(other)                                # a link elsewhere
        self.assertIn("没有通到这个学习工作区", self.line(self.doctor(), "todo", "学习工作区的位置："))

    def test_staying_with_a_half_finished_move_keeps_todays_line(self):
        entrance = self.stay_in_sync()
        (entrance / "stages").mkdir(parents=True)                 # a real, different folder
        text = self.line(self.doctor(), "todo", "学习工作区的位置：")
        self.assertNotIn("入口", text)
        self.assertTrue(text.endswith("这是你在第 0.2 课做的决定：先留在原处。"
                                      " → 第 1.12 课把课程变成仓库之前，会再问你一次"), text)

    def test_an_entrance_to_a_workspace_that_is_not_synced(self):
        self.home()
        (self.box.home / "Developer" / "fullstack-from-zero").symlink_to(self.box.root)
        text = self.line(self.doctor(), "ok", "学习工作区的位置：")
        self.assertEqual(text, f"学习工作区的位置：{self.box.root}，不在同步到云端的文件夹里。"
                               "~/Developer/fullstack-from-zero 是通往它的入口，课文里的 cd ~/Developer/fullstack-from-zero 照样能用。")

    def test_the_label_is_learning_workspace_everywhere(self):
        # E1b: from lesson 1.6 on a bare 工作区 is Git's working tree.
        for key, text in doctor.TEXT.items():
            plain = text.replace("学习工作区", "")
            with self.subTest(key=key):
                self.assertNotIn("工作区", plain)
                self.assertNotIn("课程文件夹", text)

    def test_other_or_unreadable_decisions_keep_the_lesson_0_2_line(self):
        self.home()
        envstubs.xattr_stub(self.box.base / "xattr-bin", flagged=[self.box.base])
        self.state({"decisions": {"workspace_location": "not-synced"}})
        self.assertIn("→ 第 0.2 课会带你处理", self.line(self.doctor(), "todo", "学习工作区的位置："))
        (self.box.root / "learner" / "state.json").write_text("{ damaged", encoding="utf-8")
        result = self.doctor()
        self.assertIn("→ 第 0.2 课会带你处理", self.line(result, "todo", "学习工作区的位置："))
        self.assertEqual((self.box.root / "learner" / "state.json").read_text(encoding="utf-8"),
                         "{ damaged")

    def test_a_git_folder_in_the_workspace_before_lesson_1_12(self):
        self.home()
        self.assertEqual([t for t in self.groups(self.doctor())["todo"]
                          if t.startswith("学习工作区：")], [])
        (self.box.root / ".git").mkdir()
        result = self.doctor()
        text = self.line(result, "todo", "学习工作区：")
        self.assertIn("把学习工作区变成仓库是第 1.12 课的事", text)
        self.assertIn("多半是在错的文件夹里运行了 git init", text)
        self.assertIn("先什么都不要删", text)
        self.assertIn("→ 对导师说“急救：学习工作区里多了 .git”", text)
        self.assertNotIn("课程文件夹", text)
        self.assertTrue((self.box.root / ".git").is_dir())
        # after 1.12a the repository is the lesson's work: nothing to say
        self.state({"stations": {"1.12a": {"first_pass": "2026-11-19T10:00:00",
                                           "status": "passed"}}})
        self.assertEqual([t for t in self.groups(self.doctor())["todo"]
                          if t.startswith("学习工作区：")], [])

    def test_a_git_file_counts_too_and_an_open_station_does_not_hide_it(self):
        self.home()
        (self.box.root / ".git").write_text("gitdir: /somewhere/else\n", encoding="utf-8")
        self.state({"stations": {"1.12a": {"attempts": 2, "status": "open"}}})
        self.line(self.doctor(), "todo", "学习工作区：")

    def test_starter_files_that_differ_are_named_once(self):
        self.home()
        shutil.copytree(str(helpers.REPO / "starter"), str(self.box.root / "starter"))
        self.assertEqual([t for t in self.groups(self.doctor())["info"]
                          if t.startswith("练习用的起始文件")], [])
        # lesson 0.1c tells the learner to edit convert.py: never reported
        convert = self.box.root / "starter" / "hello-fx" / "convert.py"
        convert.write_text(convert.read_text(encoding="utf-8").replace("100", "250"),
                           encoding="utf-8")
        self.assertEqual([t for t in self.groups(self.doctor())["info"]
                          if t.startswith("练习用的起始文件")], [])
        (self.box.root / "starter" / "my-site" / "index.html").write_text("改过\n")
        (self.box.root / "starter" / "hello-fx" / "rates.txt").unlink()
        result = self.doctor()
        text = self.line(result, "info", "练习用的起始文件（starter/）：")
        self.assertIn("starter/hello-fx/rates.txt 不见了", text)
        self.assertIn("starter/my-site/index.html 改过", text)
        self.assertIn("练习不受影响：练习场景和考试用的都是工具里存的原样", text)
        self.assertIn("对导师说“急救：starter 被改动了”", text)
        self.assertNotIn("convert.py", text)
        self.assertEqual(self.groups(result)["info"].count(text), 1)

    def test_workspace_itself_flagged(self):
        self.home()
        envstubs.xattr_stub(self.box.base / "xattr-bin", flagged=[self.box.root])
        self.line(self.doctor(), "todo", "学习工作区的位置：")

    def test_workspace_in_icloud_drive(self):
        self.home()
        inside = (self.box.home / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
                  / "fullstack-from-zero")
        (inside / "stages").mkdir(parents=True)
        self.box.root = inside
        text = self.line(self.doctor(), "todo", "学习工作区的位置：")
        self.assertIn("~/Library/Mobile Documents/com~apple~CloudDocs/fullstack-from-zero", text)
        self.assertIn("iCloud 云盘", text)

    def test_workspace_not_synced(self):
        self.home()
        self.assertIn("不在同步到云端的文件夹里", self.line(self.doctor(), "ok", "学习工作区的位置："))

    def test_attribute_reader_failing_means_cannot_tell(self):
        self.home()
        envstubs.xattr_stub(self.box.base / "xattr-bin", fail=True)
        result = self.doctor()
        self.assertEqual(result.code, 0)
        self.assertIn("无法判断", self.line(result, "info", "学习工作区的位置："))
        with mock.patch.object(doctor, "XATTR", str(self.box.base / "no-such-xattr")):
            missing = self.doctor()
        self.assertIn("无法判断", self.line(missing, "info", "学习工作区的位置："))

    def test_attribute_reader_timeout(self):
        self.home()
        envstubs.FakeBin(self.box.base / "xattr-bin").script("xattr", "/bin/sleep 10")
        with mock.patch.object(doctor, "XATTR_TIMEOUT", 1):
            result = self.doctor()
        text = self.line(result, "info", "学习工作区的位置：")
        self.assertIn("无法判断", text)
        self.assertIn("超过 1 秒没有结束", text)

    def test_no_developer_folder(self):
        self.home()
        (self.box.home / "Developer").rmdir()
        self.assertIn("第 0.2 课", self.line(self.doctor(), "info", "~/Developer 文件夹：还没有"))

    # -- missing or unusual programs ------------------------------------------
    def test_missing_tools(self):
        self.home()
        for name in ("code", "python3", "sw_vers"):
            self.bin.remove(name)
        result = self.doctor()
        self.assertEqual(result.code, 0, result)
        code = self.line(result, "todo", "code 命令：在 PATH 里找不到")
        self.assertIn("第 0.1 课", code)
        # the fixed first-aid sentence of lesson 0.1 (COMMON section 2)
        self.assertIn("→ 对导师说“急救：code 命令找不到”", code)
        self.line(result, "todo", "python3：在 PATH 里找不到")
        self.line(result, "info", "macOS 版本：找不到 sw_vers")

    def test_no_git_at_all(self):
        self.home()
        self.bin.remove("git")
        result = self.doctor()
        self.assertEqual(result.code, 0, result)
        self.assertIn("第 1.6 课之前要弄好", self.line(result, "todo", "Git：在 PATH 里找不到"))
        self.line(result, "info", "Git 的设置：因为 git 用不了")
        self.assertNotIn("提交签名", result.out)

    def test_git_that_cannot_run(self):
        self.home()
        self.bin.prints("git", "xcrun: error: invalid active developer path", code=1, stderr=True)
        result = self.doctor()
        text = self.line(result, "todo", "Git：git 命令在，但运行失败")
        self.assertIn("xcrun: error", text)

    def test_python_versions(self):
        self.home()
        self.bin.prints("python3", "Python 3.8.10")
        self.assertIn("太旧了", self.line(self.doctor(), "todo", "python3："))
        self.bin.prints("python3", "Python 3.9.6")
        self.line(self.doctor(), "ok", "python3：3.9.6")
        self.bin.prints("python3", "something else")
        self.assertIn("看不懂", self.line(self.doctor(), "info", "python3："))

    def test_other_shells_and_systems(self):
        self.home()
        self.bin.prints("bash", "GNU bash, version 3.2.57(1)-release")
        self.assertIn("课程是按 zsh 写的",
                      self.line(self.doctor(SHELL=str(self.bin.path / "bash")), "info", "登录用的 shell：bash"))
        self.line(self.doctor(SHELL=""), "info", "登录用的 shell：环境变量 SHELL 没有设置")
        self.bin.prints("sw_vers", "26.7.3")
        self.assertIn("比课程核对时用的 27.2.1 旧", self.line(self.doctor(), "info", "macOS 版本："))
        self.bin.prints("sw_vers", "not a version")
        self.line(self.doctor(), "info", "macOS 版本：sw_vers 的输出看不懂")

    def test_gh_installed(self):
        self.home()
        self.bin.prints("gh", "gh version 2.105.0 (2026-11-18)\nhttps://github.com/cli/cli/releases")
        text = self.line(self.doctor(), "info", "GitHub CLI（gh）：已经装了")
        self.assertIn("（2.105.0）。第 1.11 课才用到。", text)
        # after lesson 1.11 (which installs it) gh is simply there
        self.state({"stations": {s: {"first_pass": "2026-11-25T10:00:00", "status": "passed"}
                                 for s in ("1.11a", "1.11b", "1.11c")}})
        self.line(self.doctor(), "ok", "GitHub CLI（gh）：2.105.0")

    def test_gh_missing_before_and_after_lesson_1_11(self):
        # E6: doctor and fresh name the same lesson (baseline.json installed_in).
        self.home()
        before = self.line(self.doctor(), "info", "GitHub CLI（gh）：")
        self.assertEqual(before, "GitHub CLI（gh）：还没安装。第 1.11 课会带你装，在那之前用不到。")
        self.state({"stations": {s: {"first_pass": "2026-11-25T10:00:00", "status": "passed"}
                                 for s in ("1.11a", "1.11b", "1.11c")}})
        after = self.line(self.doctor(), "todo", "GitHub CLI（gh）：")
        self.assertEqual(after, "GitHub CLI（gh）：在 PATH 里找不到。第 1.11 课装过它，后面的课还要用。"
                                " → 把这一行发给导师")

    # -- the network, only with --net -----------------------------------------
    def test_net_is_never_used_without_the_flag(self):
        self.home()

        def forbidden(request, timeout):
            raise AssertionError("network used without --net")

        with mock.patch.object(doctor, "open_url", forbidden):
            result = self.doctor()
        self.assertEqual(result.code, 0)

    def test_net_reachable_and_not(self):
        self.home()
        seen = []

        class Answer:
            def close(self):
                pass

        def fine(request, timeout):
            seen.append((request.get_method(), request.full_url, timeout, request.data))
            return Answer()

        with mock.patch.object(doctor, "open_url", fine):
            ok = self.doctor("--net")
        self.assertEqual(seen, [("HEAD", "https://github.com", 8, None)])
        self.line(ok, "ok", "能不能连上 github.com：8 秒内连上了")
        self.assertTrue(self.box.last_result()["net"])

        def refused(request, timeout):
            raise urllib.error.URLError(ConnectionRefusedError(61, "Connection refused"))

        with mock.patch.object(doctor, "open_url", refused):
            bad = self.doctor("--net")
        self.assertEqual(bad.code, 0)
        self.assertIn("第 1.11 课", self.line(bad, "info", "能不能连上 github.com：8 秒内没连上"))

        def slow(request, timeout):
            raise OSError("timed out")

        with mock.patch.object(doctor, "open_url", slow):
            late = self.doctor("--net")
        self.assertIn("等太久", self.line(late, "info", "能不能连上 github.com"))

        def status(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", {}, None)

        with mock.patch.object(doctor, "open_url", status):
            answered = self.doctor("--net")
        self.line(answered, "ok", "能不能连上 github.com")

    # -- robustness -----------------------------------------------------------
    def test_one_broken_check_does_not_stop_the_others(self):
        self.home()

        def broken(self):
            raise RuntimeError("boom")

        with mock.patch.object(doctor.Doctor, "check_macos", broken):
            result = self.doctor()
        self.assertEqual(result.code, 0)
        self.assertIn("这一项没查成（工具内部出错）", self.line(result, "info", "macOS 版本："))
        self.line(result, "todo", "提交签名：")

    def test_works_with_a_damaged_state_file(self):
        self.home()
        (self.box.root / "learner").mkdir()
        (self.box.root / "learner" / "state.json").write_text("{not json", encoding="utf-8")
        result = self.doctor()
        self.assertEqual(result.code, 0, result)
        self.assertEqual((self.box.root / "learner" / "state.json").read_text(encoding="utf-8"),
                         "{not json")

    def test_cannot_store_the_result(self):
        self.home()
        (self.box.root / "learner").write_text("a file where the folder should be", encoding="utf-8")
        result = self.doctor()
        self.assertEqual(result.code, 2, result)
        self.assertIn("需要处理", result.out)          # the report was printed first
        self.assertIn("检查器出问题", result.text)

    def test_help_is_chinese(self):
        result = self.box.run("doctor", "-h")
        self.assertEqual(result.code, 0)
        self.assertIn("--net", result.out)
        self.assertIn("只看不改", result.out)

    def test_python_39_process(self):
        python = helpers.find_python39()
        if python is None:
            self.skipTest("no Python 3.9 on this machine")
        self.home()
        result = self.box.run_process("doctor", python=python, PATH=str(self.bin),
                                      SHELL=str(self.bin.path / "zsh"), TERM="xterm-256color")
        self.assertEqual(result.code, 0, result)
        self.assertNotIn("Traceback", result.text)
        self.assertIn("找不到签名程序 gpg", result.out)
        for secret in envstubs.SECRETS:
            self.assertNotIn(secret, result.text)


class SimHomeTest(unittest.TestCase):
    """tools/dev/make_sim_home.py itself."""

    def setUp(self):
        self.box = helpers.Sandbox(self)

    def test_builds_the_learner_settings(self):
        target = self.box.base / "sim"
        info = SIM.make_sim_home(target, workspace=self.box.root)
        home = target / "home"
        self.assertEqual(info["home"], str(home))
        self.assertTrue((home / "Developer" / "fullstack-from-zero" / "stages").is_dir())
        ignore = (home / ".gitignore_global").read_text(encoding="utf-8").split("\n")
        self.assertEqual(ignore[:8], [".DS_Store", "._*", ".Spotlight-V100", ".Trashes",
                                      ".idea/", "*.swp", "*.swo", "*.log"])
        if not envstubs.REAL_GIT:
            return
        env = {"HOME": str(home), "PATH": os.environ.get("PATH", ""), "GIT_CONFIG_NOSYSTEM": "1"}

        def get(key):
            import subprocess
            done = subprocess.run([envstubs.REAL_GIT, "config", "--global", "--get", key],
                                  env=env, capture_output=True, check=False, timeout=30)
            return done.stdout.decode("utf-8").strip()

        self.assertEqual(get("commit.gpgsign"), "true")
        self.assertEqual(get("gpg.format"), "openpgp")
        self.assertEqual(get("gpg.program"), "gpg")
        self.assertEqual(get("user.signingkey"), "FAKEKEY0000")
        self.assertEqual(get("user.name"), "Learner")
        self.assertEqual(get("core.excludesfile"), "~/.gitignore_global")
        self.assertEqual(get("tag.forceSignAnnotated"), "false")
        # present with EMPTY values, as in the common bad case of plan G7
        import subprocess
        listed = subprocess.run([envstubs.REAL_GIT, "config", "--global", "--get-regexp", r"^gpg\.ssh\."],
                                env=env, capture_output=True, check=False, timeout=30)
        self.assertEqual(listed.stdout.decode("utf-8"),
                         "gpg.ssh.program \ngpg.ssh.allowedsignersfile \n")
        self.assertIn('[gpg "ssh"]\n\tprogram = \n\tallowedSignersFile = \n',
                      (home / ".gitconfig").read_text(encoding="utf-8"))
        lines = SIM.export_lines(info)
        self.assertIn("export HOME=" + str(home), lines)

    def test_the_exact_gitconfig_text(self):
        self.assertEqual(SIM.gitconfig_text(), (
            "[user]\n\tname = Learner\n\temail = learner@example.com\n\tsigningkey = FAKEKEY0000\n"
            "[commit]\n\tgpgsign = true\n[gpg]\n\tformat = openpgp\n\tprogram = gpg\n"
            '[gpg "ssh"]\n\tprogram = \n\tallowedSignersFile = \n'
            "[tag]\n\tforceSignAnnotated = false\n[core]\n\texcludesfile = ~/.gitignore_global\n"))
        self.assertNotIn("gpg", SIM.gitconfig_text(signing=False))
        self.assertNotIn("forceSignAnnotated", SIM.gitconfig_text(signing=False))

    @unittest.skipUnless(envstubs.REAL_GIT, "git is not installed")
    def test_a_signed_commit_fails_as_on_the_learner_machine(self):
        import subprocess
        target = self.box.base / "sim"
        info = SIM.make_sim_home(target, copy=False)
        repo = target / "repo"
        repo.mkdir()
        empty_bin = self.box.base / "nobin"
        empty_bin.mkdir()
        git_dir = os.path.dirname(envstubs.REAL_GIT)
        env = {"HOME": info["home"], "PATH": git_dir + os.pathsep + str(empty_bin),
               "GIT_CONFIG_NOSYSTEM": "1", "LC_ALL": "C", "TMPDIR": tempfile.gettempdir()}

        def git(*args):
            return subprocess.run([envstubs.REAL_GIT] + list(args), cwd=str(repo), env=env,
                                  capture_output=True, check=False, timeout=30)

        git("init", "-q")
        (repo / "a.txt").write_text("a\n", encoding="utf-8")
        git("add", "a.txt")
        done = git("commit", "-m", "x")
        self.assertNotEqual(done.returncode, 0)
        err = done.stderr.decode("utf-8")
        if shutil.which("gpg", path=env["PATH"]) is None:
            self.assertIn("error: cannot run gpg: No such file or directory", err)
        self.assertIn("fatal: failed to write commit object", err)
        # the empty gpg.ssh.program: SSH signing fails too, with an empty program name
        key = Path(info["home"]) / ".ssh" / "id_ed25519.pub"
        key.parent.mkdir()
        key.write_text("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI0000 sim\n", encoding="utf-8")
        ssh = git("-c", "gpg.format=ssh", "-c", "user.signingkey=" + str(key), "commit", "-m", "y")
        self.assertNotEqual(ssh.returncode, 0)
        self.assertIn("error: cannot run : No such file or directory", ssh.stderr.decode("utf-8"))

    def test_no_copy(self):
        info = SIM.make_sim_home(self.box.base / "sim", copy=False)
        self.assertIsNone(info["workspace"])
        self.assertEqual(sorted(p.name for p in (self.box.base / "sim" / "home").iterdir()),
                         [".gitconfig", ".gitignore_global", "Developer"])

    def test_refuses_outside_the_temporary_folder(self):
        # A path that is outside every temporary folder wherever the suite
        # runs from (the workspace itself may lie under $TMPDIR in a G8
        # simulation).  The refusal comes before any folder is created.
        outside = Path("/course-sim-should-not-exist")
        with self.assertRaises(SIM.Refusal):
            SIM.make_sim_home(outside, copy=False)
        self.assertFalse(outside.exists())
        # A folder in the home folder is refused, unless HOME itself lies in
        # a temporary folder (a G8 simulation): there it is a legal target,
        # so that one case cannot be tested and is left out.
        home = Path(os.path.realpath(os.path.expanduser("~")))
        in_temp = any(home == root or root in home.parents for root in SIM.temp_roots())
        if not in_temp:
            in_home = Path(os.path.expanduser("~/sim-should-not-exist"))
            with self.assertRaises(SIM.Refusal):
                SIM.make_sim_home(in_home, copy=False)
            self.assertFalse(in_home.exists())
        with self.assertRaises(SIM.Refusal):
            SIM.make_sim_home(SIM.temp_roots()[0], copy=False)

    def test_refuses_a_non_empty_folder_and_a_copy_into_itself(self):
        (self.box.base / "busy").mkdir()
        (self.box.base / "busy" / "x.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(SIM.Refusal):
            SIM.make_sim_home(self.box.base / "busy", copy=False)
        with self.assertRaises(SIM.Refusal):
            SIM.make_sim_home(self.box.root / "sim", workspace=self.box.root)

    def test_command_line(self):
        import subprocess
        import sys
        script = str(helpers.TOOLS / "dev" / "make_sim_home.py")
        target = self.box.base / "cli-sim"
        done = subprocess.run([sys.executable, script, str(target), "--workspace",
                               str(self.box.root)], capture_output=True, check=False, timeout=60)
        out = done.stdout.decode("utf-8")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("export HOME=" + str(target / "home"), out)
        self.assertIn("cd " + str(target / "home" / "Developer" / "fullstack-from-zero"), out)
        again = subprocess.run([sys.executable, script, str(target)], capture_output=True,
                               check=False, timeout=60)
        self.assertEqual(again.returncode, 2)
        self.assertIn("拒绝", again.stderr.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
