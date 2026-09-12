# Same-file commit splitting

Read this for commits that share a file or require isolating selected edits. Planning uses only the selection and grouping guidance below; it never prepares indexes or writes objects.

## Selection and grouping

Capture the initial HEAD (or unborn branch state), staged diff, unstaged diff, and selected paths. Prefer staged edits within the command's path scope. If any are selected, do not incorporate unstaged edits, even from the same file. Staged paths outside `gitx files` remain excluded. If there are no staged edits within the scope, select safe working-tree changes there. Do not expand the selection to satisfy a dependency; group selected edits together or explain the missing prerequisite.

Group by behavior, not by Git's hunk boundaries. Separate hunks may depend on each other; adjacent changes in one hunk may be independent. Keep imports, callers, schema changes, and relevant tests with the change that needs them. A later commit may depend on an earlier commit, but each prefix of the sequence must form a coherent project snapshot.

For example, `auth.py` may contain both an expiration fix and a login analytics event:

```text
1. fix(auth): reject tokens at their expiration time
   auth.py — change the boundary comparison in is_expired()
2. feat(auth): record successful logins
   auth.py — add the event in login()
```

If two intents edit the same line, construct the proposed intermediate version separately and inspect both transitions. Split only if this preserves each intent without inventing behavior. Otherwise combine them and explain why. Keep binary files, file mode changes, renames, symlinks, and submodule changes atomic unless their representation can be preserved confidently; do not force text-hunk splitting onto them.

## Prepare a commit without changing working files

Use temporary indexes and tree-to-tree patches to prepare exact snapshots. Do not use whole-file `git add`, checkout, stash, or reset on the user's working tree to stage a partial group. Do not mutate an index containing unresolved entries; finish resolving the operation first. Stop if another process changes HEAD, the index, or relevant working files after inspection.

For each approved group:

1. Record the real index tree with `git write-tree` as `I`. Keep the original staged and unstaged diffs as recovery evidence in a private temporary directory; they can contain private content. Record the real index path via `git rev-parse --git-path index`, including linked-worktree support. Do not print raw recovery diffs containing secrets.
2. Prepare a temporary index using an absolute, initially nonexistent path and command-scoped `GIT_INDEX_FILE`. Initialize it with `git read-tree HEAD`, or `git read-tree --empty` on an unborn branch. Apply a patch containing only the current group's changes with `git apply --cached --check`, then `git apply --cached`. Write its tree as `C`, the candidate commit. Generate patches against the actual current parent; do not reuse stale hunk offsets after earlier commits.
3. Prepare a second temporary index for the desired real index after this commit, `R`. For staged-only selection, `R = I`: the same indexed contents compared with the new HEAD naturally retain deferred and excluded staging. For working-tree selection, start from `I` and apply the current group's patch to its selected paths, which have no staged changes under the selection rule. This records newly committed edits without disturbing staged paths outside the selection. Write the resulting tree as `R`.
4. Produce an index transition patch from `I` to `C`, and a restoration patch from `C` to `R`, using `git diff --binary --full-index --no-ext-diff --no-textconv <from-tree> <to-tree> --`. Save both. Validate both transitions in temporary indexes before touching the real index. Apply only to indexes with `--cached`; an empty patch is a no-op. Do not use `--3way` or force a failed patch through.
5. Recheck the captured repository state. Apply the `I` → `C` patch to the real index with `git apply --cached --check`, followed by `git apply --cached`. Confirm `git write-tree` equals `C`. Inspect the entire staged diff for unintended paths, whitespace errors, missing prerequisites, and accidental secrets. Unselected staged changes are temporarily absent from this candidate and must be restored after the attempt.
6. Run any requested checks against `C` as described below, then use normal `git commit -m ...` without path arguments or `-a`. Do not bypass hooks. Confirm the new commit has the expected parent and tree `C`, and the real index still has tree `C`. Then apply the saved `C` → `R` restoration patch and verify the real index equals `R`.
7. Confirm working files are unchanged and review the remaining staged and unstaged diffs before proceeding. Keep recovery files until preservation checks pass. Stop on unexpected changes, rather than automatically overwriting new work or retrying the commit.

The temporary indexes are preparation tools; committing uses the real index so normal Git hooks run in their usual environment. Keep `GIT_INDEX_FILE` scoped to individual preparation commands, never exported across the commit workflow. Do not replace the real index by copying a temporary one over it, which can discard index metadata.

## Failures and recovery

Before a commit succeeds, if HEAD and the candidate index are still as expected, reverse the saved `I` → `C` patch to restore the original staging. This includes a check failure when the user does not choose to commit anyway. After a successful commit, restore `R`, not `I`, so newly committed unstaged changes are not staged as reversions. Verify applicability before any recovery patch.

If a hook or another process changes the index, files, or HEAD, inspect those differences first. Never blindly restore over them, amend the unexpected commit, reset history, or discard hook edits. Report completed commit hashes, what remains, and the recovery file locations when safe automatic recovery is no longer possible. Do not leave excluded staging removed without explaining the state.

## Checking intermediate snapshots

Structural inspection is always required. Run tests, typechecks, or other project checks when requested by `gitx check`, `gitx branch check`, the user, or repository instructions.

Materialize candidate tree `C` in an isolated temporary directory, for example using `git archive` and extraction there. Run the project's relevant checks inside that snapshot, not the complete original working tree. Use existing dependencies only when doing so preserves isolation; do not share writable build output or silently download dependencies. If checks need Git metadata, submodules, LFS content, ignored configuration, or unavailable dependencies, use an appropriate isolated checkout or report the limitation. Be aware that archive attributes can omit or transform files; verify the exported snapshot contains the inputs the checks require.

A failure blocks the sequence under the existing Checks workflow unless the user explicitly chooses to commit anyway. A check that could not run is unverified, not passed. Do not claim intermediate commits were tested merely because hooks or tests ran against the full working tree.

## Final verification

Compare the final committed tree with the original selected target on selected paths, including modes and deletions. Confirm no excluded paths entered the commits, deferred groups are exhausted, previously excluded staging remains staged, and unselected working-tree content remains byte-for-byte intact. Report commit hashes and messages, shared-file splits, and validation results.

The repository's `tests/test_same_file_splitting.py` builds disposable Git repositories to exercise these index transitions for separate hunks, overlapping edits, partially staged files, excluded staging, and failures. These examples validate Git mechanics, not an agent's semantic grouping decisions.
