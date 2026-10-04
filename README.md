# GitX

Turn messy AI-generated changes into clean, safe Git history.

GitX is a portable Git workflow skill for AI coding agents that turns working-tree changes into logical Conventional Commits and handles branches, project checks, safe pull and push workflows, GitHub pull requests and issues, secret scanning, merge and rebase conflict resolution, repository status and history, and commit planning across Agent Skills-compatible tools.

## Install

```bash
npx skills add musoyangrigor/gitx-skill --skill gitx
```

The Skills CLI configures the skill for the selected supported AI agent. Start a new agent session after installation.

A bare `$gitx` invocation immediately inspects the repository and runs Smart commit. GitX shows its command list only when you ask for help.

## Commands

| Command | Description |
| --- | --- |
| `$gitx` | Inspect changes and create a smart commit. |
| `$gitx setup` | Preview and save project preferences in `.gitx.json`. |
| `$gitx body` | Create a smart commit with a useful commit body. |
| `$gitx branch` | Create and switch to a branch with an inferred prefix, such as `feat/` or `fix/`. |
| `$gitx branch fix/token-refresh` | Create and switch to the named branch. |
| `$gitx branch check` | Create an inferred branch, run checks, then commit. |
| `$gitx pull` | Safely pull updates for the current branch. |
| `$gitx push` | Push the current branch to `origin`; create its upstream if needed. |
| `$gitx pr` | Create a GitHub pull request into the configured base or `origin`'s default branch with a generated title and body. |
| `$gitx pr develop` | Create a GitHub pull request from the current branch into `develop`. |
| `$gitx ship` | Create a feature branch if needed, run checks, commit, push, and open a PR into the configured or default base branch. |
| `$gitx ship dev` | Run the ship workflow and open a PR targeting `dev`. |
| `$gitx issue Login fails after token expiry` | Create a GitHub issue with a generated title and body. |
| `$gitx issue 123` | Read GitHub issue `#123` and implement the requested fix in the current working tree. |
| `$gitx resolve` | Resolve an in-progress merge or rebase conflict. |
| `$gitx check` | Run relevant checks, then create a smart commit. |
| `$gitx status` | Show repository status without changing anything. |
| `$gitx doctor` | Diagnose common Git problems and suggest next steps without changing anything. |
| `$gitx doctor push rejected` | Focus diagnosis on a specific problem or supplied error. |
| `$gitx tree` | Show a compact Git history tree, branch, sync, PR, and working-tree information. |
| `$gitx scan` | Scan changes and Git history for exposed secrets and sensitive files; summarize the project’s security state, findings, positives, recommended actions, and a secret-exposure rating without modifying anything. |
| `$gitx plan` | Preview commit groups and messages without changing anything. |
| `$gitx type fix` | Create a smart commit with the `fix` type. |
| `$gitx scope auth` | Create a smart commit with the `auth` scope. |
| `$gitx files README.md package.json` | Commit only the specified files. |
| `$gitx amend` | Ask before amending the most recent commit. |

If GitX finds several logical commit groups, it asks whether to create the real number of commits or one commit.

For `gitx issue`, only a number such as `123` or `#123` tells GitX to implement an existing issue. Any other text creates a new GitHub issue, including descriptions that use words such as “fix” or “update.”

## Usage

Invoke GitX through your AI agent's skill interface, then use the same command words. For example: `gitx plan`, `gitx check`, or `gitx branch fix/token-refresh`.

GitX follows the portable `SKILL.md` Agent Skills format.

## Project preferences

Run `$gitx setup` to inspect local conventions, preview the proposed configuration, and save `.gitx.json` at the repository root. Setup preserves existing choices, omits uncertain defaults, and does not run checks or commit the file. Commit it when you want to share the preferences with your team.

Example configuration:

```json
{
  "prBase": "dev",
  "branchPrefix": ["feat/", "fix/", "chore/", "docs/", "refactor/", "test/"],
  "commitScopes": ["auth", "api", "ui", "docs"],
  "checks": ["npm run lint", "npm test"],
  "draftPR": false
}
```

Every field is optional. With this example, `$gitx ship` and `$gitx pr` target `dev`, while `$gitx ship main` explicitly targets `main`. Generated branches choose a prefix from `branchPrefix` based on the work, such as `fix/` for a bug fix or `chore/` for maintenance. Use a string such as `"branchPrefix": "feat/"` to force one prefix, or omit the field for unrestricted inference. If no listed prefix fits or the choice is ambiguous, GitX asks before creating the branch. Inferred commit scopes use the listed vocabulary. Check workflows run the configured commands in order, and new PRs are ready for review unless a draft is explicitly requested.

Explicit requests override saved preferences, and preferences override inferred defaults. Required repository rules still apply. Without `.gitx.json`, GitX works as before. See [project preferences](gitx/references/preferences.md) for setup behavior and validation, and the [JSON Schema](gitx/references/gitx.schema.json) for field types.

## Workflow references

Detailed behavior: [pull requests](gitx/references/pull-requests.md), [GitHub issues](gitx/references/github-issues.md), [secret scanning](gitx/references/secret-scanning.md), [shipping](gitx/references/ship.md), [diagnosis](gitx/references/doctor.md), and [splitting edits within one file](gitx/references/same-file-splitting.md).

## Development

Run the disposable Git examples with Python 3 and Git installed:

```bash
python3 -m unittest discover -s tests -v
```
