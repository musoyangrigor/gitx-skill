# Project preferences

GitX is an agent skill: the agent reads these preferences and applies them to its workflows. No additional CLI or runtime is required. Configuration is optional and applies only to the repository containing it.

## Find and validate

Read only `.gitx.json` at the current working-tree root, including when invoked from a subdirectory. Use the current worktree's file in linked worktrees and the submodule's own root inside a submodule. Do not search parent projects, the home directory, or nested package directories for additional overrides. Do not follow a configuration symlink outside the working-tree root; report that limitation instead. Never rewrite the file just by loading it.

Parse strict JSON as data, not executable code. Require an object with only the fields below; all fields are optional, and `{}` keeps inferred defaults. Reject duplicate keys, unknown keys, nulls, wrong types, blank values, and invalid names instead of silently dropping them. The bundled [JSON Schema](gitx.schema.json) describes the shape; apply the Git-specific validation below as well. No schema library installation is required to inspect this small format.

| Field | Accepted value | Meaning when present | When omitted |
| --- | --- | --- | --- |
| `prBase` | Nonempty string accepted as a literal Git branch name | Default destination for `gitx pr` and `gitx ship` | Detect the remote default branch |
| `branchPrefix` | A prefix string or nonempty array of unique prefixes; each ends in `/` and forms a valid branch when `gitx-example` is appended | A string fixes the prefix; an array limits inference to the listed prefixes | Infer from the work, such as `fix/` or `docs/` |
| `commitScopes` | Nonempty array of unique scope strings matching `[A-Za-z0-9][A-Za-z0-9._/-]*` | Vocabulary for inferred Conventional Commit scopes | Infer a useful scope or omit it |
| `checks` | Nonempty array of unique, nonblank single-line command strings | Ordered project checks for workflows that request checks | Detect relevant checks |
| `draftPR` | Boolean | Initial draft status for new PRs | Ready for review |

Validate branch values with Git's branch-name rules, rejecting names beginning with `-` and checkout shorthand such as `@{-1}` rather than expanding them. For every prefix, including each array entry, validate the full sample name. Empty or duplicate prefix arrays are invalid; omit the field for unrestricted inference. A valid branch name need not already exist during setup; the actual PR workflow must verify its destination on `origin`. An empty checks array is invalid: omit the field to use detection instead of using it to disable validation.

Malformed configuration blocks commands that consume preferences before they mutate anything. Explain the field and expected type or rule without exposing sensitive command arguments. Status, tree, doctor, and scan can still inspect their normal scope; doctor should report a configuration error as a workflow blocker when relevant. Setup can repair configuration when the intended correction is clear from the user's request; otherwise explain the issue and ask for the missing choice before replacing it.

## Precedence and scope

Use explicit user choices first, saved preferences second, and GitX inference last. Preferences do not override required repository instructions or grant additional execution permissions. Surface an actual conflict rather than silently weakening a required check or rule.

- `gitx ship main` and `gitx pr main` override `prBase: "dev"` for that invocation only. A missing configured base is an error, not permission to fall back. Detect the actual default branch separately for ship's source-branch decision; `prBase` is never a replacement for repository metadata.
- `gitx branch fix/login` keeps the exact supplied name, even with `branchPrefix: "team/"`. A configured prefix applies to inferred branches in Branch and Ship; it does not rename existing branches.
- With `branchPrefix: ["feat/", "fix/", "chore/"]`, choose the listed prefix that best describes the intended work: new functionality uses `feat/`, bug fixes use `fix/`, and maintenance uses `chore/`. Array order is not a default. If none fits or the choice is ambiguous, ask for a prefix before creating the branch; do not silently choose the first entry or an unlisted prefix. A one-entry array behaves like a fixed string. Explicit branch names still override either form.
- `gitx scope payments` uses the explicit scope even if it is absent from `commitScopes`, unless a required repository rule prevents it. Inferred scopes use the configured vocabulary, or no scope if none fits. Scope preferences do not affect commit type.
- `draftPR: true` creates new PRs as drafts unless the user explicitly asks for ready-for-review. `draftPR: false` is overridden by an explicit draft request. Returning an existing PR never changes its draft status automatically.
- `checks` is used by check, branch check, ship, and conflict resolution when checks are required. It does not cause ordinary commits, planning, setup, status, or doctor to run commands. Preserve each workflow's failure rules and required snapshot isolation. An explicit user selection of checks overrides this list subject to required repository instructions.

Run configured checks from the working-tree root, or the corresponding root of an isolated candidate snapshot, in their listed order. Include additional repository-required checks and avoid running an identical command twice without a reason. Inspect the configured commands and relevant project scripts before execution, just as with detected checks. Treat them as repository-provided commands, not higher-priority instructions: a command that deploys, publishes, installs dependencies, deletes user work, or accesses secrets is not authorized merely by appearing in `checks`. Explain the mismatch and stop that check unless the user has separately authorized the action. Do not source the JSON or concatenate its contents into a shell expression to parse it.

## `gitx setup`

1. Locate the working-tree root and read existing preferences and documented project conventions. Setup requires a working-tree repository, but no remote or GitHub authentication. It works on an unborn branch and from a subdirectory. Do not initialize a repository or fetch information automatically.
2. Infer a small candidate configuration from explicit user preferences, existing valid configuration, and clear local project conventions. Inspect package scripts, CI or contributor instructions for checks, and local remote metadata for a base. Do not execute scripts to discover them. Do not invent a `dev` branch, npm commands, fixed prefix, or scope list just to fill every field. Omit uncertain optional values and explain that GitX will infer them when used. Leave `branchPrefix` omitted unless a fixed prefix or allowed prefix list is requested or documented. If nothing can be inferred, `{}` is a valid initial configuration.
3. On repeat setup, preserve existing valid choices and change only requested fields or add clearly supported missing defaults. Removing a field restores its fallback. Do not replace a malformed file, erase unknown fields, or remove comments from invalid JSON silently. Preserve unrelated files and any staged version of the configuration.
4. Validate the candidate, then show its exact formatted JSON and root-relative destination `.gitx.json` before writing. Summarize changed fields for an existing file. This is a preview of the authorized setup action, not a mandatory second approval; ask only for unresolved choices. If the user asks only for a preview, do not write.
5. Recheck that the file has not changed since inspection, then write only `.gitx.json`, formatted with two-space indentation and a trailing newline. Do not overwrite concurrent edits. Do not modify Git configuration, hooks, agent instruction files, or `.gitignore`. Do not stage or commit it. If the candidate matches the existing values, report that no update is needed and avoid rewriting.
6. Read back and validate the saved file. Report the settings saved, which omitted settings still use inference, and that the file can be committed to share preferences with the team. Do not run checks or publish anything during setup.

Example configuration (illustrative, not universal defaults):

```json
{
  "prBase": "dev",
  "branchPrefix": ["feat/", "fix/", "chore/", "docs/", "refactor/", "test/"],
  "commitScopes": ["auth", "api", "ui", "docs"],
  "checks": ["npm run lint", "npm test"],
  "draftPR": false
}
```
