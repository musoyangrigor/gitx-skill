"""Executable examples of the reference's staging protocol, not an AI splitter."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


# Enough unchanged context to put the two functions in separate default hunks.
BASE = "def expired(now, expiry):\n    return now > expiry\n" + "\n" * 8 + "def login():\n    return 'ok'\n"
FIX = BASE.replace("now > expiry", "now >= expiry")
FINAL = FIX.replace("    return 'ok'", "    print('login')\n    return 'ok'")


class SplittingExamples(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="gitx-split-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        # Keep examples independent of the caller's Git configuration/index.
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.git("init", "-q")
        self.git("config", "user.name", "GitX Example")
        self.git("config", "user.email", "example@example.invalid")
        self.git("config", "core.hooksPath", str(self.root / "hooks"))
        self.git("config", "commit.gpgSign", "false")
        self.path = self.repo / "auth.py"
        self.path.write_text(BASE)
        (self.repo / "notes.txt").write_text("original\n")
        self.git("add", ".")
        self.git("commit", "-qm", "initial")
        self.serial = 0

    def git(self, *args, data=None, index=None, check=True):
        env = self.env.copy()
        if index is not None:
            env["GIT_INDEX_FILE"] = str(index)
        return subprocess.run(
            ["git", *args], cwd=self.repo, env=env, input=data,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check,
        ).stdout

    def tree(self, base, edits):
        """Build a desired snapshot without touching real files or staging."""
        self.serial += 1
        index = self.root / f"index-{self.serial}"
        self.git("read-tree", base, index=index)
        for name, content in edits.items():
            blob = self.git("hash-object", "-w", "--stdin", data=content.encode()).strip().decode()
            self.git("update-index", "--add", "--cacheinfo", "100644", blob, name, index=index)
        return self.git("write-tree", index=index).strip().decode()

    def patch(self, old, new):
        return self.git("diff", "--binary", "--full-index", "--no-ext-diff",
                        "--no-textconv", old, new, "--")

    def apply(self, patch, reverse=False):
        if patch:
            flags = ["--reverse"] if reverse else []
            self.git("apply", "--cached", "--check", *flags, data=patch)
            self.git("apply", "--cached", *flags, data=patch)

    def commit_group(self, content, staged_selection=True, fail=False):
        before = {p.name: p.read_bytes() for p in self.repo.iterdir() if p.is_file()}
        parent = self.git("rev-parse", "HEAD").strip()
        original = self.git("write-tree").strip().decode()
        candidate = self.tree("HEAD", {"auth.py": content})
        restore = original if staged_selection else self.tree(original, {"auth.py": content})
        transition = self.patch(original, candidate)
        self.apply(transition)
        self.assertEqual(self.git("write-tree").strip().decode(), candidate)

        # Check the indexed snapshot: working files can contain later changes.
        staged = self.git("show", ":auth.py").decode()
        scope = {}
        exec(compile(staged, "auth.py", "exec"), scope)
        self.assertTrue(scope["expired"](10, 10))
        if fail:
            with self.assertRaises(subprocess.CalledProcessError):
                self.git("commit", "-qm", "must fail")
            self.assertEqual(self.git("rev-parse", "HEAD").strip(), parent)
            self.apply(transition, reverse=True)
            self.assertEqual(self.git("write-tree").strip().decode(), original)
        else:
            self.git("commit", "-qm", "example group")
            self.assertEqual(self.git("rev-parse", "HEAD^").strip(), parent)
            self.assertEqual(self.git("rev-parse", "HEAD^{tree}").strip().decode(), candidate)
            self.apply(self.patch(candidate, restore))
            self.assertEqual(self.git("write-tree").strip().decode(), restore)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.repo.iterdir() if p.is_file()})

    def test_two_groups_in_one_file(self):
        self.path.write_text(FINAL)
        self.git("add", "auth.py")
        self.commit_group(FIX)
        self.assertEqual(self.git("show", "HEAD:auth.py").decode(), FIX)
        self.assertIn(b"print('login')", self.git("diff", "--cached"))
        self.commit_group(FINAL)
        self.assertEqual(self.git("status", "--porcelain"), b"")

    def test_partially_staged_file_preserves_unstaged_edits(self):
        self.path.write_text(FINAL)
        self.git("add", "auth.py")
        unstaged = FINAL + "\n# unfinished work\n"
        self.path.write_text(unstaged)
        original_unstaged = self.git("diff", "--binary")
        self.commit_group(FIX)
        self.commit_group(FINAL)
        self.assertEqual(self.git("diff", "--cached"), b"")
        self.assertEqual(self.git("diff", "--binary"), original_unstaged)
        self.assertEqual(self.path.read_text(), unstaged)

    def test_excluded_staging_survives_working_tree_selection(self):
        (self.repo / "notes.txt").write_text("staged outside selected paths\n")
        self.git("add", "notes.txt")
        excluded = self.git("diff", "--cached", "--", "notes.txt")
        self.path.write_text(FINAL)
        self.commit_group(FIX, staged_selection=False)
        self.commit_group(FINAL, staged_selection=False)
        self.assertEqual(self.git("diff", "--cached", "--", "notes.txt"), excluded)
        self.assertEqual(self.git("show", "HEAD:notes.txt"), b"original\n")
        self.assertEqual(self.git("diff", "HEAD", "--", "auth.py"), b"")

    def test_excluded_staging_survives_staged_selection(self):
        self.path.write_text(FINAL)
        (self.repo / "notes.txt").write_text("excluded staged change\n")
        self.git("add", ".")
        excluded = self.git("diff", "--cached", "--", "notes.txt")
        self.commit_group(FIX)
        self.commit_group(FINAL)
        self.assertEqual(self.git("diff", "--cached", "--", "notes.txt"), excluded)
        self.assertEqual(self.git("show", "HEAD:notes.txt"), b"original\n")

    def test_stale_patch_leaves_index_untouched(self):
        original = self.git("write-tree").strip().decode()
        candidate = self.tree("HEAD", {"auth.py": FIX})
        patch = self.patch(original, candidate)
        self.path.write_text(BASE.replace("now > expiry", "False"))
        self.git("add", "auth.py")
        changed_index = self.git("write-tree")
        with self.assertRaises(subprocess.CalledProcessError):
            self.apply(patch)
        self.assertEqual(self.git("write-tree"), changed_index)

    def test_overlapping_line_has_valid_intermediate_version(self):
        # Both the comparison and its spelling change on the same source line.
        final = FIX.replace("now >= expiry", "not now < expiry")
        self.path.write_text(final)
        self.git("add", "auth.py")
        self.commit_group(FIX)
        self.commit_group(final)
        self.assertEqual(self.git("status", "--porcelain"), b"")

    def test_failed_hook_restores_original_staging(self):
        self.path.write_text(FINAL)
        self.git("add", "auth.py")
        (self.repo / "notes.txt").write_text("also staged\n")
        self.git("add", "notes.txt")
        hooks = self.root / "hooks"
        hooks.mkdir()
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        before = self.git("diff", "--cached", "--binary")
        self.commit_group(FIX, fail=True)
        self.assertEqual(self.git("diff", "--cached", "--binary"), before)


if __name__ == "__main__":
    unittest.main()
