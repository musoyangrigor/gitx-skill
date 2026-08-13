# GitX

Turn messy AI-generated changes into clean, safe Git history.

GitX is a portable Git workflow skill for AI coding agents that turns working-tree changes into logical Conventional Commits and handles branches, project checks, safe pull and push workflows, GitHub pull requests and issues, secret scanning, merge and rebase conflict resolution, repository status and history, and commit planning across Agent Skills-compatible tools.

## Install

```bash
npx skills add musoyangrigor/gitx-skill --skill gitx
```

The Skills CLI configures the skill for the selected supported AI agent. Start a new agent session after installation.

## Commands

| Command | Description |
| --- | --- |
| `$gitx` | Inspect changes and create a smart commit. |
| `$gitx body` | Create a smart commit with a useful commit body. |
| `$gitx branch` | Create and switch to a branch with an inferred prefix, such as `feat/` or `fix/`. |
| `$gitx branch fix/token-refresh` | Create and switch to the named branch. |
| `$gitx branch check` | Create an inferred branch, run checks, then commit. |
| `$gitx pull` | Safely pull updates for the current branch. |
| `$gitx push` | Push the current branch to `origin`; create its upstream if needed. |
| `$gitx pr` | Create a GitHub pull request into `origin`'s default branch with a generated title and body. |
| `$gitx pr develop` | Create a GitHub pull request from the current branch into `develop`. |
| `$gitx issue Login fails after token expiry` | Create a GitHub issue with a generated title and body. |
| `$gitx issue 123` | Read GitHub issue `#123` and implement the requested fix in the current working tree. |
| `$gitx resolve` | Resolve an in-progress merge or rebase conflict. |
| `$gitx check` | Run relevant checks, then create a smart commit. |
| `$gitx status` | Show repository status without changing anything. |
| `$gitx tree` | Show a compact Git history tree, branch, sync, PR, and working-tree information. |
| `$gitx scan` | Scan changes and Git history for exposed secrets and sensitive files; summarize the project’s security state, findings, positives, recommended actions, and a secret-exposure rating without modifying anything. |
| `$gitx plan` | Preview commit groups and messages without changing anything. |
| `$gitx type fix` | Create a smart commit with the `fix` type. |
| `$gitx scope auth` | Create a smart commit with the `auth` scope. |
| `$gitx files README.md package.json` | Commit only the specified files. |
| `$gitx amend` | Ask before amending the most recent commit. |

If GitX finds several logical commit groups, it asks whether to create the real number of commits or one commit.

## Usage

Invoke GitX through your AI agent's skill interface, then use the same command words. For example: `gitx plan`, `gitx check`, or `gitx branch fix/token-refresh`.

GitX follows the portable `SKILL.md` Agent Skills format.
