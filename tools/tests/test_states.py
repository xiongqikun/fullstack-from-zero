"""The state ladder S0-S7 of the learner's website (plan I6, tools/courselib/states.py)."""

import datetime
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import helpers

from courselib import scenario, states
from courselib.errors import ToolTrouble
from courselib.gitread import GitReader, GitRepo

NOW = datetime.datetime(2026, 11, 19, 10, 0, 0)
STARTER = helpers.REPO / "starter" / "my-site"
CONVENTIONAL = r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-]+\))?!?: \S"


def make_hostile_home(base):
    """A simulation home with the common bad case of plan G7 (built as in G8): signing on, no working gpg.

    ``gpg.program`` is ``gpg`` and a fake ``gpg`` that always fails is first on
    PATH, so any attempt to sign makes the commit fail.  Returns the environment.
    """
    home = Path(base) / "home"
    fake_bin = Path(base) / "bin"
    home.mkdir(parents=True)
    fake_bin.mkdir()
    gpg = fake_bin / "gpg"
    gpg.write_text("#!/bin/sh\necho 'gpg: signing failed: No secret key' >&2\nexit 2\n",
                   encoding="utf-8")
    os.chmod(str(gpg), 0o755)
    (home / ".gitignore_global").write_text(
        ".DS_Store\n._*\n.Spotlight-V100\n.Trashes\n.idea/\n*.swp\n*.swo\n*.log\n", encoding="utf-8")
    (home / ".gitconfig").write_text(
        "[user]\n\tname = Learner\n\temail = learner@example.com\n\tsigningkey = FAKEKEY0000\n"
        "[commit]\n\tgpgsign = true\n[gpg]\n\tformat = openpgp\n\tprogram = gpg\n"
        "[tag]\n\tforceSignAnnotated = false\n"
        "[core]\n\texcludesfile = {}\n".format(home / ".gitignore_global"), encoding="utf-8")
    env = {
        "PATH": str(fake_bin) + os.pathsep + os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "TMPDIR": tempfile.gettempdir(),
        "LANG": "C.UTF-8",
        "XDG_CONFIG_HOME": str(home / ".config"),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    return home, env


def plain_commit_fails(env, folder):
    """Precondition of the hostile home: a learner's plain ``git commit`` fails."""
    folder.mkdir(parents=True)
    run = lambda *a: subprocess.run(["git"] + list(a), cwd=str(folder), env=env,
                                    capture_output=True, check=False, timeout=60)
    run("init", "-q")
    (folder / "a.txt").write_text("a\n", encoding="utf-8")
    run("add", "a.txt")
    done = run("commit", "-q", "-m", "x")
    return done.returncode != 0


class LadderTest(unittest.TestCase):
    def setUp(self):
        self.base = Path(os.path.realpath(tempfile.mkdtemp(prefix="states-test-")))
        self.addCleanup(shutil.rmtree, str(self.base), True)
        self.env = dict(os.environ)
        self.env.update({"GIT_CONFIG_NOSYSTEM": "1", "HOME": str(self.base / "nohome")})

    def build(self, name, folder=None, seed=7, now=NOW):
        target = self.base / (folder or name)
        return states.build(name, target, workspace=helpers.REPO, now=now, seed=seed,
                            env=self.env)

    def repo(self, path):
        return GitRepo(path, GitReader(self.env))

    def files(self, site):
        return sorted(p.relative_to(site).as_posix() for p in site.rglob("*")
                      if p.is_file() and ".git" not in p.relative_to(site).parts)

    # -- every row of plan I6 ---------------------------------------------------
    def test_s0_my_site_does_not_exist(self):
        built = self.build("S0")
        self.assertEqual(built.site, self.base / "S0" / "my-site")
        self.assertFalse(built.site.exists())
        self.assertEqual(built.facts["commits"], 0)

    def test_s1_starter_files_copied(self):
        site = self.build("S1").site
        self.assertEqual(self.files(site), ["index.html", "style.css"])
        for name in ("index.html", "style.css"):
            self.assertEqual((site / name).read_bytes(), (STARTER / name).read_bytes())
        self.assertFalse((site / ".git").exists())

    def test_s2_heading_and_one_paragraph_edited(self):
        built = self.build("S2")
        site = built.site
        self.assertEqual(self.files(site), [".editorconfig", "index.html", "style.css"])
        page = (site / "index.html").read_text(encoding="utf-8")
        original = (STARTER / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("____", page)
        self.assertIn("<h1>你好，我是{}</h1>".format(built.facts["owner"]), page)
        self.assertIn("<p>{}</p>".format(built.facts["paragraph"]), page)
        self.assertNotIn(states.STARTER_PARAGRAPH, page)
        changed = [(a, b) for a, b in zip(original.splitlines(), page.splitlines()) if a != b]
        self.assertEqual(len(changed), 2, changed)       # the heading and one paragraph
        self.assertEqual(len(original.splitlines()), len(page.splitlines()))
        self.assertEqual((site / "style.css").read_bytes(), (STARTER / "style.css").read_bytes())
        # lesson 1.4c: the outermost .editorconfig, UTF-8, LF, final newline, 2 spaces
        config = (site / ".editorconfig").read_text(encoding="utf-8")
        for line in ("root = true", "charset = utf-8", "end_of_line = lf",
                     "insert_final_newline = true", "[*.{html,css}]", "indent_style = space",
                     "indent_size = 2"):
            self.assertIn(line + "\n", config)

    def test_s3_plus_readme(self):
        built = self.build("S3")
        self.assertEqual(self.files(built.site),
                         [".editorconfig", "README.md", "index.html", "style.css"])
        readme = (built.site / "README.md").read_text(encoding="utf-8")
        self.assertTrue(readme.startswith("# my-site\n"))
        self.assertIn(built.facts["owner"], readme)
        # lesson 1.5b wants a code block or a link: the command is a fenced zsh block
        self.assertIn("```zsh\nopen index.html\n```\n", readme)
        self.assertFalse((built.site / ".git").exists())

    def test_s4_repository_with_two_commits(self):
        built = self.build("S4")
        repo = self.repo(built.site)
        self.assertTrue(repo.is_repo)
        self.assertEqual(repo.branch, "main")
        self.assertEqual(repo.commit_count(), 2)
        self.assertEqual(repo.commit_count(), built.facts["commits"])
        self.assertTrue(repo.is_clean())
        self.assertEqual(repo.tracked(), [".editorconfig", "README.md", "index.html", "style.css"])
        self.assertEqual(repo.remotes(), {})
        self.assertEqual(built.facts["head"], repo.head)
        # lesson 1.6c: after the first version, one more commit that changes README.md
        self.assertEqual([c.subject for c in repo.commits()],
                         ["在 README 里写上用 Git 记录改动", "第一版网页"])
        self.assertEqual(repo.changed_files("HEAD"), [("M", "README.md")])

    def test_s5_plus_gitignore_drafts_and_five_commits(self):
        built = self.build("S5")
        repo = self.repo(built.site)
        self.assertIn(".gitignore", repo.tracked())
        self.assertEqual(repo.commit_count(), 5)
        self.assertTrue(repo.is_clean())
        self.assertTrue(repo.is_ignored("drafts/idea.txt"))
        self.assertTrue(repo.is_ignored(".env"))
        # lesson 1.9a: a drafts note that stays on the computer only
        self.assertTrue((built.site / "drafts" / "colors.md").is_file())
        self.assertTrue(repo.is_ignored("drafts/colors.md"))
        self.assertNotIn("drafts/colors.md", repo.tracked())
        added = [path for letter, path in repo.changed_files("HEAD") if letter == "A"]
        self.assertEqual(added, [".gitignore"])
        subjects = [c.subject for c in repo.commits()]
        self.assertEqual(subjects[:3], ["添加 .gitignore", "换了一个标题颜色", "改了标题的颜色"])
        # lesson 1.7b gives every learner the same colour; 1.9a lets them pick another
        self.assertIn("color: #c2410c;", repo.file_at("HEAD~2", "style.css"))
        css = (built.site / "style.css").read_text(encoding="utf-8")
        self.assertIn("color: {};".format(built.facts["color"]), css)
        self.assertNotEqual(built.facts["color"], states.LESSON_COLOR)

    def test_s6_seven_commits_latest_conventional(self):
        import re
        built = self.build("S6")
        repo = self.repo(built.site)
        commits = repo.commits()
        self.assertEqual(len(commits), 7)
        self.assertTrue(re.match(CONVENTIONAL, commits[0].subject), commits[0].subject)
        self.assertTrue(re.match(CONVENTIONAL, commits[1].subject), commits[1].subject)
        # a bigger heading changes what the page shows: feat, not style (commitlint's
        # config-conventional: style is formatting that does not change meaning)
        self.assertEqual(commits[0].subject, "feat: 调大标题的字号")
        self.assertFalse(any(c.subject.startswith("style:") for c in commits))
        # the early ones were written before lesson 1.10 taught the convention
        self.assertFalse(re.match(CONVENTIONAL, commits[-1].subject))
        self.assertTrue(repo.is_clean())
        self.assertIn(built.facts["plan"], (built.site / "index.html").read_text(encoding="utf-8"))

    def test_s7_public_remote_license_and_page_online(self):
        built = self.build("S7")
        repo = self.repo(built.site)
        self.assertIn("LICENSE", repo.tracked())
        self.assertTrue((built.site / "LICENSE").read_text(encoding="utf-8").startswith("MIT License"))
        self.assertIn(built.facts["owner"], (built.site / "LICENSE").read_text(encoding="utf-8"))
        remote_path = self.base / "S7" / "remote" / "my-site.git"
        self.assertEqual(repo.remotes(), {"origin": str(remote_path)})
        self.assertEqual(repo.upstream(), "origin/main")
        self.assertEqual(repo.ahead_behind(), (0, 0))
        remote = self.repo(remote_path)
        self.assertTrue(remote.is_bare)
        # "online": what the stand-in for GitHub serves is the learner's latest commit
        self.assertEqual(remote.ref("main"), repo.head)
        readme = (built.site / "README.md").read_text(encoding="utf-8")
        self.assertIn(states.PAGES_URL, readme)
        # lesson 1.13a: LICENSE and the README's licence section in one commit
        self.assertIn("[LICENSE](LICENSE)", readme)
        licence = repo.query("log", "--format=%H", "--diff-filter=A", "--", "LICENSE").lines
        self.assertEqual(sorted(p for _l, p in repo.changed_files(licence[0].strip())),
                         ["LICENSE", "README.md"])
        # lesson 1.13c: a list line made true and a footer link to the repository
        page = (built.site / "index.html").read_text(encoding="utf-8")
        self.assertIn(states.LIST_AFTER, page)
        self.assertNotIn(states.LIST_BEFORE, page)
        self.assertIn('<a href="https://github.com/你的用户名/my-site">这个网页的源代码</a>', page)
        self.assertTrue(repo.is_clean())
        self.assertEqual(repo.commit_count(), 11)

    def test_subjects_and_lessons_tell_one_story(self):
        """Every commit subject is made by the lesson the ladder table names."""
        self.assertEqual(len(states.COMMITS), states.COMMIT_COUNT["S7"])
        source = (helpers.TOOLS / "courselib" / "states.py").read_text(encoding="utf-8")
        expected = {"第一版网页": "1.6c", "在 README 里写上用 Git 记录改动": "1.6c",
                    "改了标题的颜色": "1.7b", "换了一个标题颜色": "1.9a",
                    "添加 .gitignore": "1.9a", "feat: 在首页加一条学习计划": "1.10b",
                    "feat: 调大标题的字号": "1.10b", "docs: 添加 MIT 许可证": "1.13a",
                    "docs: 在 README 里写上网页地址": "1.13b",
                    "feat: 列表里写上网页已经上线": "1.13c",
                    "feat: 在页脚加上源代码的链接": "1.13c"}
        for entry in states.COMMITS:
            line = next(text for text in source.splitlines()
                        if '"subject": "{}"'.format(entry["subject"]) in text)
            lesson = expected[entry["subject"]]
            self.assertIn("# " + lesson, line)
            # the commit's lesson ends before (or at) the state that first has it
            first = next(n for n in states.NAMES
                         if states.COMMIT_COUNT[n] > states.COMMITS.index(entry))
            self.assertLessEqual(states._lesson_key(lesson[:-1]),
                                 states._lesson_key(states.REACHED_AT[first]))
            self.assertIn("-> " + first, line)
        self.assertNotIn("style: 调大标题的字号", source)

    def test_commit_counts_grow_along_the_ladder(self):
        counts = []
        for name in states.NAMES[4:]:
            counts.append(self.repo(self.build(name).site).commit_count())
        self.assertEqual(counts, sorted(counts))
        self.assertEqual(counts, [states.COMMIT_COUNT[n] for n in states.NAMES[4:]])

    def test_commits_use_the_practice_identity_and_no_future_dates(self):
        built = self.build("S7", now=datetime.datetime(2026, 11, 19, 0, 30))
        for commit in self.repo(built.site).commits():
            self.assertEqual((commit.author_name, commit.author_email),
                             ("练习场", "playground@example.invalid"))
            self.assertLessEqual(commit.date[:19], "2026-11-19T00:30:00")
        self.assertIsNone(self.repo(built.site).config("user.name", scope="local"))

    # -- determinism and seeds ------------------------------------------------
    def test_same_seed_same_state(self):
        for name in ("S3", "S7"):
            one = self.build(name, folder=name + "-one", seed=11)
            two = self.build(name, folder=name + "-two", seed=11)
            self.assertEqual(self.files(one.site), self.files(two.site))
            for rel in self.files(one.site):
                self.assertEqual((one.site / rel).read_bytes(), (two.site / rel).read_bytes(), rel)
            self.assertEqual(one.facts, two.facts)
        self.assertEqual(self.build("S6", "a", seed=5).facts["head"],
                         self.build("S6", "b", seed=5).facts["head"])

    def test_different_seeds_give_different_names(self):
        owners = {self.build("S2", folder=f"seed-{seed}", seed=seed).facts["owner"]
                  for seed in range(1, 13)}
        self.assertGreater(len(owners), 1)

    # -- safety -----------------------------------------------------------------
    def test_writes_only_under_base(self):
        outer = self.base / "outer"
        outer.mkdir()
        states.build("S7", outer / "inner", workspace=helpers.REPO, now=NOW, seed=1, env=self.env)
        self.assertEqual(sorted(p.name for p in outer.iterdir()), ["inner"])
        self.assertEqual(sorted(p.name for p in (outer / "inner").iterdir()), ["my-site", "remote"])
        self.assertFalse((self.base / "nohome").exists())   # no global config was created

    def test_refuses_an_existing_site(self):
        (self.base / "busy" / "my-site").mkdir(parents=True)
        (self.base / "busy" / "my-site" / "mine.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(ToolTrouble):
            self.build("S3", folder="busy")
        self.assertEqual(os.listdir(str(self.base / "busy" / "my-site")), ["mine.txt"])

    def test_unknown_state_name(self):
        with self.assertRaises(ToolTrouble):
            self.build("S8")
        self.assertEqual(states.normalise_name(" s4 "), "S4")

    def test_build_state_returns_the_site_path(self):
        path = states.build_state("S4", self.base / "x", workspace=helpers.REPO, now=NOW,
                                  seed=3, env=self.env)
        self.assertEqual(path, self.base / "x" / "my-site")
        self.assertTrue((path / ".git").is_dir())

    # -- which state comes before which lesson --------------------------------
    def test_state_before_and_after_lessons(self):
        before = {"0.1": "S0", "0.4": "S0", "1.1": "S0", "1.2": "S0", "1.3": "S1", "1.4": "S1",
                  "1.5": "S2", "1.6": "S3", "1.7": "S4", "1.9": "S4", "1.10": "S5",
                  "1.11": "S6", "1.13": "S6", "1.14": "S7", "1.16": "S7"}
        for lesson, name in before.items():
            self.assertEqual(states.state_before(lesson), name, lesson)
        after = {"1.1": "S0", "1.2": "S1", "1.3": "S1", "1.6": "S4", "1.10": "S6", "1.13": "S7"}
        for lesson, name in after.items():
            self.assertEqual(states.state_after(lesson), name, lesson)


class HostileHomeTest(unittest.TestCase):
    """Commits succeed where the learner's own plain ``git commit`` fails."""

    def setUp(self):
        self.base = Path(os.path.realpath(tempfile.mkdtemp(prefix="states-sim-")))
        self.addCleanup(shutil.rmtree, str(self.base), True)
        self.home, self.env = make_hostile_home(self.base)

    def test_plain_commit_fails_but_every_state_builds(self):
        self.assertTrue(plain_commit_fails(self.env, self.base / "probe"))
        before = (self.home / ".gitconfig").read_bytes()
        for name in states.NAMES:
            built = states.build(name, self.base / name, workspace=helpers.REPO, now=NOW,
                                 seed=2, env=self.env)
            if states.COMMIT_COUNT[name]:
                repo = GitRepo(built.site, GitReader(self.env))
                self.assertEqual(repo.commit_count(), states.COMMIT_COUNT[name], name)
        self.assertEqual((self.home / ".gitconfig").read_bytes(), before)


class BuilderHelpersTest(unittest.TestCase):
    """``sc.state`` and ``sc.site_before`` inside a real scenario build."""

    def setUp(self):
        self.box = helpers.Sandbox(self)
        # a workspace whose starter/ the learner has edited: never read (plan G11a)
        shutil.copytree(str(helpers.REPO / "starter"), str(self.box.root / "starter"))
        (self.box.root / "starter" / "my-site" / "index.html").write_text("坏了\n", encoding="utf-8")
        self.app = self.box.app()

    def test_sc_state_builds_inside_the_scenario(self):
        def builder(sc):
            site = sc.state("S5", base="copy")
            sc.fact("site", site.relative_to(sc.root).as_posix())

        info = scenario.build(self.app, builder, "ladder", seed=4)
        self.assertEqual(info.facts["site"], "copy/my-site")
        repo = GitRepo(info.path / "copy" / "my-site", GitReader(self.box.environment()))
        self.assertEqual(repo.commit_count(), 5)
        self.assertIn(b"<!DOCTYPE html>", (info.path / "copy" / "my-site" / "index.html").read_bytes())
        # the learner's real site is never touched by a builder
        self.assertFalse((self.box.home / "Developer" / "my-site").exists())

    def test_site_before_records_facts(self):
        def builder(sc):
            sc.site_before()

        info = scenario.build(self.app, builder, "before-1.7", lesson_id="1.7", seed=4)
        self.assertEqual(info.facts["site_state"], "S4")
        self.assertEqual(info.facts["site"], "my-site")
        self.assertEqual(info.facts["site_commits"], 2)
        self.assertTrue(info.facts["site_owner"])
        info = scenario.build(self.app, lambda sc: sc.site_before("1.14", base="w"),
                              "before-1.14", seed=4)
        self.assertEqual((info.facts["site"], info.facts["site_state"]), ("w/my-site", "S7"))
        self.assertEqual(info.facts["site_remote"], "w/remote/my-site.git")
        info = scenario.build(self.app, lambda sc: sc.site_before("1.2"), "before-1.2", seed=4)
        self.assertEqual((info.facts["site_state"], info.facts["site_commits"]), ("S0", 0))
        self.assertIsNone(info.facts["site_owner"])
        self.assertFalse((info.path / "my-site").exists())

    def test_same_seed_same_site_in_two_scenarios(self):
        one = scenario.build(self.app, lambda sc: sc.state("S6"), "one", seed=9)
        two = scenario.build(self.app, lambda sc: sc.state("S6"), "two", seed=9)
        reader = GitReader(self.box.environment())
        self.assertEqual(GitRepo(one.path / "my-site", reader).head,
                         GitRepo(two.path / "my-site", reader).head)


class LessonChecksOnTheLadderTest(unittest.TestCase):
    """The state a lesson leaves passes that lesson's own checks on the real site.

    The real lesson module is copied into a sandbox workspace and the ladder
    state is built where the learner's site lives (``~/Developer/my-site`` of
    the sandbox home).  When a lesson changes what it asks for, this fails and
    the ladder has to follow.
    """

    CASES = (
        ("1.4c", "04-editor", "S2", ()),
        ("1.5b", "05-markdown-readme", "S3", ()),
        ("1.6c", "06-first-commit", "S4", ()),
        ("1.9a", "09-gitignore", "S5", ("3",)),
        ("1.13a", "13-publish-site", "S7", ()),
    )

    def run_case(self, station, folder, name, answers):
        source = helpers.REPO / "stages" / "01-foundations" / folder
        if not (source / "lesson.py").is_file():
            self.skipTest("lesson " + station + " is not there")
        box = helpers.Sandbox(self)
        shutil.copytree(str(source), str(box.root / "stages" / "01-foundations" / folder))
        # after lesson 1.6a: an identity and signing switched off
        box.write_gitconfig("[user]\n\tname = Learner\n\temail = learner@example.com\n"
                            "[commit]\n\tgpgsign = false\n[core]\n\teditor = nano\n")
        env = box.environment()
        states.build(name, box.home / "Developer", now=NOW, seed=7, env=env)
        argv = ["check", station]
        for answer in answers:
            argv += ["--answer", answer]
        return box.run(*argv, noninteractive=True)

    def test_each_state_passes_the_check_of_the_lesson_that_ends_in_it(self):
        for station, folder, name, answers in self.CASES:
            with self.subTest(station=station):
                result = self.run_case(station, folder, name, answers)
                self.assertEqual(result.code, 0, result.text)
                self.assertIn("✅ 通过", result.out)

    def test_s3_readme_has_the_code_block_that_check_1_5b_wants(self):
        result = self.run_case("1.5b", "05-markdown-readme", "S3", ())
        self.assertIn("有代码块或链接", result.out)


if __name__ == "__main__":
    unittest.main()
