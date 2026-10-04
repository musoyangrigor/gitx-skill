# Pull requests

Use the standalone workflow for `gitx pr [base]`. Ship uses only the shared title, body, and readiness conventions below; its own reference controls publication sequencing and repository selection.

## Standalone workflow

1. Require a remote named `origin`, a named current branch, and a GitHub repository with an authenticated `gh` CLI. If any is unavailable, explain what is missing and do not create a PR.
2. Resolve the base in this order: supplied `[base]`, configured `prBase`, then the default branch from `origin/HEAD`. Verify the resolved branch exists on `origin`; do not fall back when a supplied or configured branch is missing. If no base can be determined, ask the user which one to use. Never hardcode `main`.
3. Inspect the working tree, commits, and diff from the resolved base branch to the current branch. Do not include uncommitted changes in the PR. If the current branch is the base branch or has no commits ahead of it, stop and explain why.
4. Check whether a PR already exists for the current branch and resolved base branch. If it does, return its URL and do not create another one.
5. Push the current branch to `origin` when needed. If it has no upstream, create one with `git push -u origin <branch>` because `gitx pr` explicitly requests publication. Never force-push.
6. Generate the title, body, and readiness using the shared conventions below.
7. Create the PR with `gh pr create --base <resolved-base> --head <current-branch> --title <generated-title> --body <generated-body>`, adding `--draft` when required below, and return its URL.

## Title, body, and readiness

Generate a concise PR title from the commits and diff. Generate a normal Markdown body using this structure, with only facts supported by the changes:

```md
## Summary

- <actual change>

## Testing

- <checks run during this task, or "Not run (not requested)">
```

Add `--draft` if explicitly requested or if configured `draftPR` is true without an explicit readiness override; otherwise create it ready for review. Do not change an existing PR's readiness merely to match a preference.
