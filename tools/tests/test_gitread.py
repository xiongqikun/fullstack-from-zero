"""Read-only Git access: what the checks can see, and that looking changes nothing."""

import os
import stat
import unittest

import helpers
from courselib.errors import ToolTrouble
from courselib.gitread import GitReader, GitRepo, parse_status


def snapshot(folder):
    """Every file below ``folder`` with its size and modification time."""
    seen = {}
    for base, _dirs, files in os.walk(str(folder)):
        for name in files:
            path = os.path.join(base, name)
            info = os.stat(path)
            seen[os.path.relpath(path, str(folder))] = (info.st_size, info.st_mtime_ns)
    return seen


class GitReadTest(unittest.TestCase):
    def setUp(self):
        self.box = helpers.Sandbox(self)
        self.reader = GitReader(self.box.environment())
        self.work = self.box.base / "work"
        self.work.mkdir()

    def repo(self, path):
        return GitRepo(path, self.reader)

    def make_repo(self, name="proj", commits=0):
        path = self.work / name
        path.mkdir()
        self.box.git(path, "init", "-q", "-b", "main")
        for number in range(1, commits + 1):
            (path / f"file{number}.txt").write_text(f"内容 {number}\n", encoding="utf-8")
            self.box.git(path, "add", "-A")
            self.box.git(path, "commit", "-q", "-m", f"docs: 第 {number} 次提交")
        return path

    # -- what kind of folder --------------------------------------------------
    def test_missing_folder(self):
        repo = self.repo(self.work / "nope")
        self.assertFalse(repo.exists)
        self.assertFalse(repo.is_repo)
        self.assertFalse(repo.inside_repo)
        self.assertEqual(repo.commits(), [])
        self.assertEqual(repo.commit_count(), 0)
        self.assertTrue(repo.status().clean)
        self.assertEqual(repo.tracked(), [])
        self.assertEqual(repo.remotes(), {})
        self.assertIsNone(repo.branch)
        self.assertIsNone(repo.config("user.name"))

    def test_plain_folder_is_not_a_repository(self):
        plain = self.work / "plain"
        plain.mkdir()
        repo = self.repo(plain)
        self.assertTrue(repo.exists)
        self.assertFalse(repo.is_repo)
        self.assertFalse(repo.inside_repo)
        self.assertIsNone(repo.toplevel)

    def test_repository_before_the_first_commit(self):
        path = self.make_repo()
        (path / "new.txt").write_text("x\n")
        repo = self.repo(path)
        self.assertTrue(repo.is_repo)
        self.assertFalse(repo.is_bare)
        self.assertIsNone(repo.head)
        self.assertFalse(repo.has_commits)
        self.assertEqual(repo.branch, "main")
        self.assertEqual(repo.commit_count(), 0)
        self.assertEqual(repo.commits(), [])
        self.assertIsNone(repo.commit())
        self.assertEqual(repo.status().untracked, ["new.txt"])
        self.assertIsNone(repo.upstream())
        self.assertIsNone(repo.ahead_behind())

    def test_folder_inside_another_repository(self):
        path = self.make_repo(commits=1)
        inner = path / "sub"
        inner.mkdir()
        repo = self.repo(inner)
        self.assertFalse(repo.is_repo)
        self.assertTrue(repo.inside_repo)
        self.assertTrue(os.path.samefile(str(repo.toplevel), str(path)))
        self.assertEqual(repo.commits(), [])
        self.assertEqual(repo.tracked(), [])

    # -- history --------------------------------------------------------------
    def test_commits_newest_first_with_all_fields(self):
        path = self.make_repo(commits=2)
        (path / "file2.txt").write_text("改过\n", encoding="utf-8")
        self.box.git(path, "commit", "-q", "-am", "fix: 修正第二个文件\n\n这里是正文。\n第二行。")
        repo = self.repo(path)
        commits = repo.commits()
        self.assertEqual([c.subject for c in commits],
                         ["fix: 修正第二个文件", "docs: 第 2 次提交", "docs: 第 1 次提交"])
        newest = commits[0]
        self.assertEqual(newest.body, "这里是正文。\n第二行。")
        self.assertEqual(newest.message, "fix: 修正第二个文件\n\n这里是正文。\n第二行。")
        self.assertEqual((newest.author_name, newest.author_email),
                         ("Learner", "learner@example.com"))
        self.assertEqual(len(newest.hash), 40)
        self.assertTrue(newest.hash.startswith(newest.short))
        self.assertEqual(newest.parents, [commits[1].hash])
        self.assertEqual(commits[-1].parents, [])
        self.assertRegex(newest.date, r"^\d{4}-\d{2}-\d{2}T")
        self.assertEqual(repo.commit_count(), 3)
        self.assertEqual(repo.head, newest.hash)
        self.assertEqual(repo.commit("HEAD~1").subject, "docs: 第 2 次提交")
        self.assertEqual(len(repo.commits(limit=1)), 1)
        self.assertIsNone(repo.ref("no-such-branch"))

    def test_changed_files_and_file_contents_of_a_commit(self):
        path = self.make_repo(commits=2)
        (path / "file1.txt").write_text("新内容\n", encoding="utf-8")
        os.remove(str(path / "file2.txt"))
        (path / "中文 名字.txt").write_text("你好\n", encoding="utf-8")
        self.box.git(path, "add", "-A")
        self.box.git(path, "commit", "-q", "-m", "chore: 三种改动")
        repo = self.repo(path)
        self.assertEqual(sorted(repo.changed_files("HEAD")),
                         [("A", "中文 名字.txt"), ("D", "file2.txt"), ("M", "file1.txt")])
        self.assertEqual(repo.changed_files("HEAD~2"), [("A", "file1.txt")])
        self.assertEqual(repo.file_at("HEAD", "file1.txt"), "新内容\n")
        self.assertEqual(repo.file_at("HEAD~1", "file1.txt"), "内容 1\n")
        self.assertIsNone(repo.file_at("HEAD", "file2.txt"))
        self.assertEqual(repo.tracked(), ["file1.txt", "中文 名字.txt"])
        self.assertTrue(repo.is_tracked("中文 名字.txt"))

    # -- working tree and index -----------------------------------------------
    def test_status_tells_staged_unstaged_and_untracked_apart(self):
        path = self.make_repo(commits=3)
        (path / "file1.txt").write_text("staged change\n")
        self.box.git(path, "add", "file1.txt")
        (path / "file2.txt").write_text("unstaged change\n")
        (path / "notes").mkdir()
        (path / "notes" / "新的.txt").write_text("untracked\n", encoding="utf-8")
        self.box.git(path, "mv", "file3.txt", "renamed.txt")
        status = self.repo(path).status()
        self.assertFalse(status.clean)
        self.assertEqual(sorted(status.staged), ["file1.txt", "renamed.txt"])
        self.assertEqual(status.unstaged, ["file2.txt"])
        self.assertEqual(status.untracked, ["notes/新的.txt"])
        self.assertEqual(status.code("file1.txt"), "M ")
        self.assertEqual(status.code("file2.txt"), " M")
        self.assertEqual(status.code("nothing"), "")
        renamed = [entry for entry in status.entries if entry.path == "renamed.txt"][0]
        self.assertEqual((renamed.x, renamed.original), ("R", "file3.txt"))

    def test_clean_repository(self):
        repo = self.repo(self.make_repo(commits=1))
        self.assertTrue(repo.is_clean())
        self.assertEqual(repo.status().entries, [])

    def test_parse_status_ignores_garbage(self):
        self.assertEqual(parse_status(""), [])
        entries = parse_status("?? a b.txt\0 M x.txt\0R  new\0old\0xx\0")
        self.assertEqual([(e.code, e.path, e.original) for e in entries],
                         [("??", "a b.txt", None), (" M", "x.txt", None), ("R ", "new", "old")])

    def test_ignore_rules(self):
        path = self.make_repo(commits=1)
        (path / ".gitignore").write_text("*.secret\nbuild/\n")
        (path / "key.secret").write_text("x")
        (path / "build").mkdir()
        (path / "build" / "out.bin").write_text("x")
        (path / "plain.txt").write_text("x")
        repo = self.repo(path)
        self.assertTrue(repo.is_ignored("key.secret"))
        self.assertTrue(repo.is_ignored("build/out.bin"))
        self.assertFalse(repo.is_ignored("plain.txt"))
        self.assertIn("key.secret", repo.ignored())
        self.assertEqual(sorted(repo.status().untracked), [".gitignore", "plain.txt"])

    # -- configuration --------------------------------------------------------
    def test_configuration_scopes(self):
        self.box.write_gitconfig("[user]\n\tname = 全局名字\n[commit]\n\tgpgsign = true\n")
        path = self.make_repo(commits=1)
        self.box.git(path, "config", "user.email", "local@example.com")
        repo = self.repo(path)
        self.assertEqual(repo.config("user.name"), "全局名字")
        self.assertEqual(repo.config("user.email"), "local@example.com")
        self.assertIsNone(repo.config("user.email", scope="global"))
        self.assertIsNone(repo.config("user.name", scope="local"))
        self.assertIsNone(repo.config("no.such"))
        self.assertIs(repo.config_bool("commit.gpgsign"), True)
        self.assertIsNone(repo.config_bool("tag.gpgsign"))
        self.assertEqual(self.reader.global_config("user.name"), "全局名字")
        self.assertIsNone(self.reader.global_config("user.email"))
        self.assertIs(self.reader.global_bool("commit.gpgsign"), True)
        self.assertIsNone(self.reader.global_bool("tag.gpgsign"))

    def test_real_global_configuration_is_never_read(self):
        # the sandbox home has no .gitconfig: whatever the real home holds is invisible
        self.assertIsNone(self.reader.global_config("user.name"))
        self.assertIsNone(self.reader.global_config("user.email"))
        self.assertIsNone(self.reader.global_bool("commit.gpgsign"))

    # -- branches, tags, remotes ----------------------------------------------
    def test_branches_tags_and_a_local_remote(self):
        path = self.make_repo(commits=2)
        bare = self.work / "remote.git"
        self.box.git(self.work, "init", "-q", "--bare", "-b", "main", str(bare))
        self.box.git(path, "remote", "add", "origin", str(bare))
        repo = self.repo(path)
        self.assertEqual(repo.remotes(), {"origin": str(bare)})
        self.assertIsNone(repo.upstream())
        self.box.git(path, "push", "-q", "-u", "origin", "main")
        self.box.git(path, "branch", "draft")
        self.box.git(path, "tag", "v0.1.0")
        repo.refresh()
        self.assertEqual(repo.upstream(), "origin/main")
        self.assertEqual(repo.ahead_behind(), (0, 0))
        self.assertEqual(sorted(repo.branches()), ["draft", "main"])
        self.assertEqual(repo.tags(), ["v0.1.0"])
        self.assertEqual(repo.ref("origin/main"), repo.head)
        (path / "more.txt").write_text("x\n")
        self.box.git(path, "add", "-A")
        self.box.git(path, "commit", "-q", "-m", "feat: 多一个")
        self.assertEqual(self.repo(path).ahead_behind(), (1, 0))

        remote = self.repo(bare)
        self.assertTrue(remote.is_repo)
        self.assertTrue(remote.is_bare)
        self.assertEqual(remote.commit_count("main"), 2)
        self.assertEqual(remote.branches(), ["main"])
        self.assertTrue(remote.status().clean)

    # -- safety ---------------------------------------------------------------
    def test_looking_at_a_repository_changes_nothing_in_it(self):
        path = self.make_repo(commits=2)
        (path / "file1.txt").write_text("edit\n")
        (path / "untracked.txt").write_text("x\n")
        before = snapshot(path)
        repo = self.repo(path)
        repo.status()
        repo.commits()
        repo.tracked()
        repo.ignored()
        repo.is_ignored("untracked.txt")
        repo.changed_files()
        repo.file_at("HEAD", "file1.txt")
        repo.config("user.name")
        repo.branches()
        repo.remotes()
        repo.upstream()
        repo.query("diff", "--stat")
        self.assertEqual(snapshot(path), before)

    def test_query_accepts_only_read_only_commands(self):
        path = self.make_repo(commits=1)
        repo = self.repo(path)
        self.assertEqual(repo.query("rev-parse", "HEAD").out.strip(), repo.head)
        self.assertEqual(repo.query("log", "--format=%s").lines, ["docs: 第 1 次提交"])
        for forbidden in (("commit", "-m", "x"), ("reset", "--hard"), ("config", "a.b", "c"),
                          ("checkout", "."), ("diff", "--output=/tmp/x"), ()):
            with self.assertRaises(ToolTrouble, msg=forbidden):
                repo.query(*forbidden)
        self.assertEqual(repo.commit_count(), 1)

    def test_missing_git_is_a_tool_problem(self):
        empty = self.box.base / "empty-bin"
        empty.mkdir()
        reader = GitReader(self.box.environment(PATH=str(empty)))
        with self.assertRaises(ToolTrouble) as caught:
            GitRepo(self.make_repo(), reader).is_repo
        self.assertIn("git", caught.exception.summary)

    def test_a_hanging_git_is_a_tool_problem(self):
        fake_bin = self.box.base / "slow-bin"
        fake_bin.mkdir()
        script = fake_bin / "git"
        script.write_text("#!/bin/sh\nsleep 20\n")
        os.chmod(str(script), os.stat(str(script)).st_mode | stat.S_IXUSR)
        reader = GitReader(self.box.environment(PATH=str(fake_bin) + ":/usr/bin:/bin"), timeout=0.5)
        with self.assertRaises(ToolTrouble) as caught:
            GitRepo(self.make_repo(), reader).is_repo
        self.assertIn("没有结束", caught.exception.summary)

    def test_inherited_git_variables_cannot_redirect_the_reader(self):
        path = self.make_repo(commits=1)
        other = self.make_repo(name="other", commits=3)
        reader = GitReader(self.box.environment(GIT_DIR=str(other / ".git"),
                                                GIT_WORK_TREE=str(other)))
        self.assertEqual(GitRepo(path, reader).commit_count(), 1)

    def test_version(self):
        version = self.reader.version()
        self.assertGreaterEqual(len(version), 2)
        self.assertGreaterEqual(version[0], 2)


if __name__ == "__main__":
    unittest.main()
