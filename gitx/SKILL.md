---
name: gitx
description: "Portable Git workflow skill for AI coding agents that turns messy AI-generated changes into clean Git history. Use for smart Conventional Commits, logical commit splitting, branches, checks, pull and push, GitHub PRs and issues, secret scanning, commit planning, Git status and history, repository diagnosis, and merge or rebase conflict resolution with Claude Code, OpenAI Codex, Cursor, and other Agent Skills-compatible tools."
---

# GitX

## Default action

On a bare invocation—`$gitx`, `gitx`, or a skill-UI invocation with no extra command—immediately execute the Smart commit workflow. Make the first action a repository inspection with Git status and the relevant diff. After inspecting, create the appropriate commit or report that there is nothing to commit.

Treat a bare invocation as an action, never as a help request. Do not announce that GitX was loaded, list commands or examples, ask which command to run, or wait for more instructions. Show the command list only when the user explicitly asks for help or available commands.

## Commands and dispatch

Match natural-language requests to the commands below. Route “check my changes” or “show git status” to Status when the user wants a read-only summary; route “run tests before committing” to Checks. Use Doctor for Git workflow diagnosis and Plan for a commit preview. Read supporting references only when their workflow or loading condition applies.

Route `gitx issue` by argument shape, not by the intent implied by its wording. An argument containing only an issue number, such as `123` or `#123`, selects the existing-issue implementation workflow. Treat every other non-empty argument as a description for a new GitHub issue, even when it contains words such as “fix,” “update,” or “resolve.” With no argument, ask for the issue description. Never implement a problem supplied as a non-numeric `gitx issue` description.

For `gitx ship [base]`, the optional argument is the PR's destination branch, never the name of a new feature branch. For example, `gitx ship dev` targets `dev`. Dispatch to Ship, not directly to Branch or Pull requests.

| Command | Action |
| --- | --- |
| `gitx` | Create a smart commit. |
| `gitx setup` | Preview and save project preferences in the repository's `.gitx.json`. |
| `gitx body` | Create a smart commit with a useful commit body. |
| `gitx branch [name]` | Create and switch to a branch. |
| `gitx branch check` | Create a default branch, run checks, then create a smart commit. |
| `gitx pull` | Safely pull updates for the current branch. |
| `gitx push` | Push the current branch to `origin`. |
| `gitx pr [base]` | Create a GitHub pull request into the supplied, configured, or default base branch. |
| `gitx ship [base]` | Create a feature branch when needed, run checks, commit, push, and open a PR into the supplied, configured, or default base branch. |
| `gitx issue <description>` | Create a GitHub issue with a generated title and body. |
| `gitx issue <number>` | Fix the GitHub issue with that number. |
| `gitx resolve` | Resolve an in-progress merge or rebase conflict. |
| `gitx check` | Run relevant checks, then create a smart commit. |
| `gitx status` | Show Git status and changed-file summary; make no changes. |
| `gitx doctor [problem]` | Diagnose repository problems and suggest next steps; make no changes. |
| `gitx tree` | Show a compact Git history tree and repository context; make no changes. |
| `gitx scan` | Scan changes and history for exposed secrets and sensitive files; make no changes. |
| `gitx plan` | Preview the proposed commit groups and messages; make no changes. |
| `gitx type <type>` | Create a smart commit using the given Conventional Commit type. |
| `gitx scope <scope>` | Create a smart commit using the given scope. |
| `gitx files <paths>` | Create a smart commit using only the given files. |
| `gitx amend` | Ask for confirmation, then amend the most recent commit. |

## Project preferences and setup

Before applying defaults for commits, planning, branches, checks, PRs, or ship, look for `.gitx.json` at the current working-tree root (`git rev-parse --show-toplevel`). If present, read [Project preferences](references/preferences.md), validate it, and apply only fields relevant to the requested workflow. If absent, preserve the existing behavior. Never create configuration during an ordinary command or execute configured checks merely because the file exists.

Explicit user choices override saved preferences; saved preferences override GitX's inferred defaults. Required repository instructions and execution permissions still apply. Invalid configuration must be explained before a dependent mutation; read-only commands may report it without stopping unrelated inspection.

For `gitx setup`, follow the reference to inspect local conventions, preview the exact proposed JSON, and create or update only the root `.gitx.json`. Setup does not run checks, stage, commit, push, create a PR, or require GitHub authentication.

## Smart commit

1. Inspect `git status` and both staged and unstaged diffs. Prefer staged changes; otherwise use all safe changed files. For `gitx files <paths>`, apply this preference within only those paths. A partially staged file contributes only its staged edits when staged changes are selected. Preserve excluded staged changes and all unselected working-tree edits.
2. Include modified tracked files, safe untracked files, and deletions. Exclude ignored files and warn before including risky files.
3. Group the selected changes by purpose, including individual edits within the same file. Read [Same-file commit splitting](references/same-file-splitting.md) when a file contributes to multiple groups or staging must be isolated from unselected edits. Keep overlapping or dependent edits together unless a coherent sequence of intermediate versions exists; order prerequisites first.
4. If one commit is appropriate, create one clear Conventional Commit. For `gitx type <type>` or `gitx scope <scope>`, use the supplied type or scope. When inferring a scope, use configured `commitScopes` if present; omit the scope when none fits rather than inventing one. Apply this to every proposed group, including `gitx plan`.
5. If two or more commits are appropriate, calculate the real number of logical groups and ask:

   > Do you want me to create N commits or one commit?

   Before asking, show each proposed message and the edits belonging to it, identifying functions or hunks when a file appears in multiple groups. Replace `N` with the real number. Never show `N` or `{count}` literally. Create multiple commits only if the user chooses multiple commits; otherwise create one commit. Execute the approved groups with index-only patches as described in the reference; do not stage a whole file containing unselected or deferred edits.
6. For `gitx body`, add a useful body to each commit message.
7. Do not push as part of a smart commit. Push only for `gitx push` or when the user explicitly asks to push.

## Commit planning

For `gitx plan`, use Smart commit's selection and grouping rules and show the proposed commit group count, files and edit summaries per group, and proposed Conventional Commit messages. Identify shared files, dependencies, and edits that must stay together. Do not change files or the index, create Git objects, commits, branches, or pushes; the reference's execution steps apply only to committing.

## Branch

For `gitx branch [name]`:

1. Keep existing changes; do not discard or stash them unless the user explicitly asks.
2. Use a valid supplied branch name exactly. If no name is supplied, derive a lowercase kebab-case name and apply configured `branchPrefix` when present: use a string as the fixed prefix, or choose the best-fitting prefix from an array according to [Project preferences](references/preferences.md). Otherwise infer an appropriate prefix from the intended work: `feat/` for new functionality, `fix/` for bug fixes, `hotfix/` only for urgent production fixes, `docs/` for documentation, `refactor/` for restructuring, `test/` for tests, or `chore/` for maintenance. If the prefix is unclear, ask the user; never default to `hotfix/`.
3. Check whether the branch exists locally or on `origin`. If it does, ask whether to switch to it or choose another name. Never overwrite it.
4. Create and switch with `git switch -c <branch-name>`.
5. Do not commit or push unless the command is `gitx branch check` or the user explicitly asks.

For `gitx branch check`, create a branch using the naming rules above, then follow the Checks behavior and Smart commit behavior.

## Checks

For `gitx check`, use configured `checks` in order when present; otherwise detect relevant checks such as `npm test`, `npm run lint`, `pnpm test`, `pytest`, `cargo test`, `go test ./...`, or `make test`. Follow the preferences reference's command inspection and working-directory rules. Include checks required by repository instructions even if absent from the configured list. If checks fail, ask whether to commit anyway. Ship retains its stricter stop-on-failure behavior.

When splitting commits, run requested checks against each proposed staged snapshot in isolation, following the reference. A passing check on the complete working tree does not validate intermediate commits. Ordinary smart commits require diff and dependency inspection but do not implicitly request running the test suite. Report which snapshots were tested and any checks that could not run.

## Pull

For `gitx pull`:

1. Inspect the current branch, upstream, and working tree. Do not pull with uncommitted changes that could be overwritten; explain the state and ask the user how to proceed.
2. Check that a remote named `origin` exists. If it does not, say that nothing was pulled; do not select another remote automatically.
3. Pull the current branch from `origin`, using the repository's existing pull/rebase configuration. If `origin` has no branch with that name, explain that there is nothing to pull. Do not use `--force` or discard local work.
4. If integration creates conflicts, stop the pull workflow and follow the Conflict resolution behavior.

## Push

For `gitx push`:

1. Check that a remote named `origin` exists. If it does not, say that nothing was pushed; do not select another remote automatically.
2. Push the current branch to `origin`. If it has no upstream, create one immediately with `git push -u origin <branch>`.

## Pull requests

For `gitx pr [base]`, read [Pull requests](references/pull-requests.md) for base resolution, publication, existing-PR handling, and creation. That reference also owns the title, body, and readiness conventions shared with Ship.

## Ship

For `gitx ship [base]`, read [Ship workflow](references/ship.md). The command authorizes creating a feature branch when needed, running checks, committing selected changes, pushing the source branch to `origin`, and creating or updating an open PR through that push. It does not authorize merging the PR, force-pushing, or automatic integration of diverged history.

Reuse Branch naming, Smart commit selection and grouping, Checks detection, and project preferences. Read the shared [PR conventions](references/pull-requests.md#title-body-and-readiness) when preparing a PR. Ship's reference owns publication sequencing, including check failures and pushing before returning an existing PR.

## GitHub issues

For `gitx issue`, use the argument-shape dispatch above, then read the selected workflow in [GitHub issues](references/github-issues.md). The reference defines prerequisites, implementation boundaries, and the new-issue template.

## Conflict resolution

For `gitx resolve` or an in-progress merge or rebase conflict:

1. Inspect the operation state, history, and every conflicting file.
2. Trace both sides of each conflict to their source commits and understand each change's intent. Read commit messages and locally available issue or PR context when present.
3. Resolve every hunk by preserving both intents where compatible. If they conflict, choose the behavior that best fits the integration goal and clearly note the trade-off. Do not invent unrelated behavior or abort the operation unless the user explicitly asks.
4. Run the project's relevant checks, using configured `checks` in their listed order when present and including repository-required checks; otherwise normally run typecheck, tests, then formatting. Fix problems introduced by the resolution.
5. Stage the resolved files and finish the operation: commit the merge, or run `git rebase --continue` and repeat until the rebase completes. Do not force-push.

## Status and history

For `gitx status`, show the current branch, staged files, unstaged files, untracked files, and a concise changed-file summary. Do not modify the repository.

For `gitx tree`, show the current branch and upstream, a working-tree summary, ahead/behind counts against the upstream or `origin`, the current PR when available, and a compact graph of the most recent 20 commits. Do not fetch, pull, push, create branches, or otherwise modify the repository.

## Repository diagnosis

For `gitx doctor [problem]`, read [Repository diagnosis](references/doctor.md). Inspect local repository state and any error supplied by the user, explain observed blockers and their practical consequences, and recommend the smallest appropriate next step. An optional problem description focuses the diagnosis; it is not authorization to repair anything. Without one, inspect common workflow blockers.

Keep diagnosis read-only: do not fetch, change files or Git state, run project checks or hooks, test a push, start authentication, or apply repairs. Distinguish confirmed findings from possible causes and unavailable information. Local remote-tracking refs may be stale, and a failed Git operation cannot always be explained from local state. Do not route a doctor request into Smart commit or Conflict resolution merely because changes or conflicts are present.

## Secret scanning

For `gitx scan`, read [Secret scanning](references/secret-scanning.md) for read-only scan scope, tool selection, exposure classification, redaction, and the report format and rating.

## Amend

For `gitx amend`, first ask for confirmation and show the proposed amended commit message. Only after the user confirms, amend the most recent commit. Do not amend a merge commit. Do not force-push; if the amended commit was already pushed, explain that a normal push will be rejected and ask the user how they want to proceed.

## Safety and risky files

Always warn before including likely secrets, credentials, private keys, logs, or build artifacts, including `.env`, `*.pem`, `*.key`, `credentials`, `token`, `secret`, `api_key`, `*.log`, `dist/`, `build/`, and `node_modules/`.
