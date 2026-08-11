---
name: gitx
description: "Turn messy AI-generated changes into clean, safe Git history with smart commits, branches, checks, safe pulls and pushes, GitHub PRs, and GitHub issue creation or fixes. Use when the user asks for gitx, a commit, a branch, checks, pull, push, a pull request or PR, a GitHub issue, to create an issue, to fix an issue, a merge conflict, Git status, or a commit plan."
---

# GitX

## Dispatch

Treat a bare GitX invocation as Smart commit. This includes `$gitx`, `gitx`, and a skill-UI invocation that loads GitX without extra command text. Immediately inspect the repository and run the Smart commit workflow. Return a command list only for an explicit help or available-commands request. Ask only when Smart commit finds two or more logical commit groups, as specified below.

| Command | Action |
| --- | --- |
| `gitx` | Create a smart commit. |
| `gitx body` | Create a smart commit with a useful commit body. |
| `gitx branch [name]` | Create and switch to a branch. |
| `gitx branch check` | Create a default branch, run checks, then create a smart commit. |
| `gitx pull` | Safely pull updates for the current branch. |
| `gitx push` | Push the current branch to `origin`. |
| `gitx pr [base]` | Create a GitHub pull request into the default branch or the supplied base branch. |
| `gitx issue <description>` | Create a GitHub issue with a generated title and body. |
| `gitx issue <number>` | Fix the GitHub issue with that number. |
| `gitx resolve` | Resolve an in-progress merge or rebase conflict. |
| `gitx check` | Run relevant checks, then create a smart commit. |
| `gitx status` | Show Git status and changed-file summary; make no changes. |
| `gitx tree` | Show a compact Git history tree and repository context; make no changes. |
| `gitx plan` | Preview the proposed commit groups and messages; make no changes. |
| `gitx type <type>` | Create a smart commit using the given Conventional Commit type. |
| `gitx scope <scope>` | Create a smart commit using the given scope. |
| `gitx files <paths>` | Create a smart commit using only the given files. |
| `gitx amend` | Ask for confirmation, then amend the most recent commit. |

## Smart commit

1. Inspect `git status` and the relevant diff. Prefer staged changes; otherwise use all safe changed files. For `gitx files <paths>`, select only those paths.
2. Include modified tracked files, safe untracked files, and deletions. Exclude ignored files and warn before including risky files.
3. Group the selected changes into logical commits.
4. If one commit is appropriate, create one clear Conventional Commit. For `gitx type <type>` or `gitx scope <scope>`, use the supplied type or scope.
5. If two or more commits are appropriate, calculate the real number of logical groups and ask:

   > Do you want me to create N commits or one commit?

   Replace `N` with the real number. Never show `N` or `{count}` literally. Create multiple commits only if the user chooses multiple commits; otherwise create one commit.
6. For `gitx body`, add a useful body to each commit message.
7. Do not push as part of a smart commit. Push only for `gitx push` or when the user explicitly asks to push.

## Status and plan

For `gitx status`, show the current branch, staged files, unstaged files, untracked files, and a concise changed-file summary. Do not modify the repository.

For `gitx tree`, show the current branch and upstream, a working-tree summary, ahead/behind counts against the upstream or `origin`, the current PR when available, and a compact graph of the most recent 20 commits. Do not fetch, pull, push, create branches, or otherwise modify the repository.

For `gitx plan`, inspect the selected changes and show the proposed commit group count, files per group, and proposed Conventional Commit messages. Do not create commits, branches, or pushes.

## Branch

For `gitx branch [name]`:

1. Keep existing changes; do not discard or stash them unless the user explicitly asks.
2. Use a valid supplied branch name exactly. If no name is supplied, derive a lowercase kebab-case name and an appropriate prefix from the intended work: `feat/` for new functionality, `fix/` for bug fixes, `hotfix/` only for urgent production fixes, `docs/` for documentation, `refactor/` for restructuring, `test/` for tests, or `chore/` for maintenance. If the prefix is unclear, ask the user; never default to `hotfix/`.
3. Check whether the branch exists locally or on `origin`. If it does, ask whether to switch to it or choose another name. Never overwrite it.
4. Create and switch with `git switch -c <branch-name>`.
5. Do not commit or push unless the command is `gitx branch check` or the user explicitly asks.

For `gitx branch check`, create a branch using the inferred prefix, then follow the Checks behavior and Smart commit behavior.

## Checks

For `gitx check`, detect and run relevant checks such as `npm test`, `npm run lint`, `pnpm test`, `pytest`, `cargo test`, `go test ./...`, or `make test`. If checks fail, ask whether to commit anyway.

## Push

For `gitx push`:

1. Check that a remote named `origin` exists. If it does not, say that nothing was pushed; do not select another remote automatically.
2. Push the current branch to `origin`. If it has no upstream, create one immediately with `git push -u origin <branch>`.

## Pull

For `gitx pull`:

1. Inspect the current branch, upstream, and working tree. Do not pull with uncommitted changes that could be overwritten; explain the state and ask the user how to proceed.
2. Check that a remote named `origin` exists. If it does not, say that nothing was pulled; do not select another remote automatically.
3. Pull the current branch from `origin`, using the repository's existing pull/rebase configuration. If `origin` has no branch with that name, explain that there is nothing to pull. Do not use `--force` or discard local work.
4. If integration creates conflicts, stop the pull workflow and follow the Resolve behavior.

## Pull request

For `gitx pr [base]`:

1. Require a remote named `origin`, a named current branch, and a GitHub repository with an authenticated `gh` CLI. If any is unavailable, explain what is missing and do not create a PR.
2. Use the supplied `[base]` branch exactly after verifying it exists on `origin`. Without `[base]`, detect the default branch from `origin/HEAD`; if it cannot be determined, ask the user which base branch to use. Never hardcode `main`.
3. Inspect the working tree, commits, and diff from the resolved base branch to the current branch. Do not include uncommitted changes in the PR. If the current branch is the base branch or has no commits ahead of it, stop and explain why.
4. Check whether a PR already exists for the current branch and resolved base branch. If it does, return its URL and do not create another one.
5. Push the current branch to `origin` when needed. If it has no upstream, create one with `git push -u origin <branch>` because `gitx pr` explicitly requests publication. Never force-push.
6. Generate a concise PR title from the commits and diff. Generate a normal Markdown body using this structure, with only facts supported by the changes:

   ```md
   ## Summary

   - <actual change>

   ## Testing

   - <checks run during this task, or "Not run (not requested)">
   ```

7. Create the ready-for-review PR with `gh pr create --base <resolved-base> --head <current-branch> --title <generated-title> --body <generated-body>` and return its URL. Do not create a draft PR unless the user explicitly asks.

## Issue

For `gitx issue <number>` where `<number>` is numeric:

1. Require a remote named `origin` and an authenticated `gh` CLI. Read the issue title, body, comments, and status with `gh issue view <number>`. If the issue is closed or lacks enough information to implement safely, explain why and ask for direction.
2. Implement only the issue's requested change in the current working tree. Do not create or switch branches, run checks, commit, push, or create a PR unless the user explicitly asks.

For `gitx issue <description>`:

1. Require a remote named `origin` and a GitHub repository with an authenticated `gh` CLI. If either is unavailable, explain what is missing and do not create an issue.
2. Require a concrete issue description. If none is supplied, ask the user what the issue is about and do not create an issue yet.
3. Generate a concise issue title and a normal Markdown body using only facts supplied by the user or available task context:

   ```md
   ## Problem

   <actual problem>

   ## Expected behavior

   <expected result, or "Not specified">

   ## Notes

   - <relevant reproduction, context, or "No additional details provided">
   ```

4. Create the issue with `gh issue create --title <generated-title> --body <generated-body>` and return its URL. Do not add labels, assignees, milestones, or projects unless the user explicitly asks.

## Resolve merge conflicts

For `gitx resolve` or an in-progress merge or rebase conflict:

1. Inspect the operation state, history, and every conflicting file.
2. Trace both sides of each conflict to their source commits and understand each change's intent. Read commit messages and locally available issue or PR context when present.
3. Resolve every hunk by preserving both intents where compatible. If they conflict, choose the behavior that best fits the integration goal and clearly note the trade-off. Do not invent unrelated behavior or abort the operation unless the user explicitly asks.
4. Run the project's relevant checks—normally typecheck, tests, then formatting—and fix problems introduced by the resolution.
5. Stage the resolved files and finish the operation: commit the merge, or run `git rebase --continue` and repeat until the rebase completes. Do not force-push.

## Amend

For `gitx amend`, first ask for confirmation and show the proposed amended commit message. Only after the user confirms, amend the most recent commit. Do not amend a merge commit. Do not force-push; if the amended commit was already pushed, explain that a normal push will be rejected and ask the user how they want to proceed.

## Risky files

Always warn before including likely secrets, credentials, private keys, logs, or build artifacts, including `.env`, `*.pem`, `*.key`, `credentials`, `token`, `secret`, `api_key`, `*.log`, `dist/`, `build/`, and `node_modules/`.
