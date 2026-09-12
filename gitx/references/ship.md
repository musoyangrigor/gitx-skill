# Ship workflow

`gitx ship [base]` takes finished work through checks, commits, push, and PR creation. The argument is always the destination branch: `gitx ship dev` means `<source> → dev`. It does not mean creating or switching to a source branch named `dev`.

## 1. Resolve the destination before changing work

- Require a normal working-tree repository, a named current branch, a remote named `origin`, and an authenticated `gh` CLI for the GitHub repository identified by `origin`. Scope GitHub queries and PR creation to that repository rather than relying on an unrelated CLI default. Explain missing prerequisites before creating branches or commits.
- Stop for detached HEAD, an unborn branch with no existing remote base, unresolved entries, or an unfinished merge/rebase/cherry-pick/revert/apply operation. Do not run conflict resolution automatically as part of shipping.
- Load and validate project preferences as directed by `SKILL.md`. Resolve the PR base in this order: explicit argument, configured `prBase`, then the remote default branch. Discover the remote default from `origin/HEAD`, verifying against GitHub's repository metadata when necessary. Ask if no base can be determined. Validate the chosen base as a literal branch name and verify the exact branch exists on `origin`. Do not create a missing base or fall back to another branch. Reject ambiguous extra arguments rather than interpreting them as a second command.
- Resolve the default branch even with an explicit base so it can be distinguished from a feature branch. If that cannot be established, ask before deciding whether to reuse the current branch. Refresh the relevant remote refs for comparison; fetching is part of ship's publication preparation. Do not pull, merge, rebase, or overwrite local branches during this step. A failed remote query is an unknown state, not evidence that the branch is absent.
- Inspect selected changes, source commits, and the diff relative to the resolved remote base. Use Smart commit's staged-first selection, including partial staging; do not silently include leftover unstaged edits. A ship request publishes all commits on the source branch that are absent from the target, not just commits created during this invocation. Explain the outgoing scope, especially when the chosen base differs from the default branch.

## 2. Select the source branch

- If there are neither selected changes nor a meaningful outgoing diff, return the matching open PR if one exists, otherwise report that there is nothing to ship. Do not create an empty branch, commit, or PR.
- When the current branch is the default branch or equals the resolved base, create a feature branch at the current HEAD using Branch naming and collision rules. Preserve existing local commits and working files; do not switch to the target base or reset the original branch. Derive the name from the selected changes or outgoing commits. Otherwise reuse the current feature branch.
- Show the resulting `<source> → <base>` relationship. Never push the default/base branch as the source of this workflow. If branch creation fails, stop before committing or publishing.
- Compare the source with its existing branch on `origin`, if present. If a normal push would require integrating remote source commits, stop and explain that blocker. Divergence from the PR base alone is normal for a feature branch; stop when actual merge conflicts or a known repository requirement make integration necessary. Do not infer conflicts solely from ahead/behind counts.

## 3. Check and commit

- Select relevant checks using Checks behavior, including configured `checks` when present. For selected uncommitted changes, use Smart commit's grouping and existing multiple-commit choice. Validate the exact proposed snapshots, including a single commit when unselected edits remain, using the isolation guidance in `same-file-splitting.md`. For already committed work, check the outgoing HEAD snapshot; do not let unrelated working-tree edits affect validation.
- Unlike standalone `gitx check`, ship stops on a failed check or an unavailable required check; do not offer to publish anyway automatically. If no relevant checks are defined, proceed and state that clearly. Never report checks as passed when they did not run.
- Create the selected commits only after their checks pass. Skip commit creation when there are no selected changes. Preserve excluded files and staging; report any work left uncommitted. Do not repeatedly commit leftovers that were outside the initial selection.
- Verify that hooks or other processes have not changed the validated snapshots. If the committed content changed, revalidate it before publication. Verify the resulting outgoing diff is nonempty and appropriate for the resolved base.

## 4. Push and open the PR

- Query for an **open** PR in the `origin` repository matching both source and base. A closed/merged PR or one targeting a different base is not a match. Do not retarget or reopen it automatically.
- Push the source branch to the same-named branch on `origin`, creating its upstream if absent. This step is required even when an open PR already exists and there are new local commits; do not take the standalone Pull requests early-return path. If already up to date, skip the redundant push. Never force-push. If publication fails, stop before creating a PR and report the error.
- After a successful push, return the matching open PR's URL if one exists. Otherwise create a PR with the resolved base explicitly passed as `--base`, the source as `--head`, and the `origin` repository explicitly selected. Follow Pull requests title, body, and draft conventions; describe actual outgoing changes and actual checks. Use configured `draftPR` unless an explicit request overrides it. Leave existing PR readiness unchanged.
- If PR creation reports a duplicate or its result is uncertain, query for the same open source/base PR before retrying. Do not create duplicates, merge the PR, enable auto-merge, or delete branches.

## Completion and partial failure

Report the source and destination, created commits (or that commits already existed), check results, push result, PR URL, and any uncommitted work that remains. Keep the report proportional to the work.

If the workflow stops, report which stages completed and the next step. Preserve created branches, successful local commits, and pushed commits; do not roll back by deleting work or rewriting history. A retry should inspect the current state, reuse the feature branch and existing commits, and push pending commits or return/create the matching open PR as needed. Never claim the work is shipped until the push and PR are confirmed.

## Expected scenarios

| Invocation and state | Expected result |
| --- | --- |
| `gitx ship dev` from `main` (the default) with changes | Create an inferred feature branch from current work; check, commit, push, open `<feature> → dev`. |
| `gitx ship dev` while on `dev` | Create a feature branch; do not push changes directly to `dev`. |
| `gitx ship dev` from `feat/login` with existing commits | Reuse `feat/login`, run checks, skip empty commit creation, push and open `feat/login → dev`. |
| `gitx ship` without `prBase`, when the remote default is `trunk` | Target `trunk`, regardless of whether a branch named `main` exists. |
| `gitx ship` with `prBase: "dev"` from the actual default `main` | Create a feature branch and target `dev`; keep treating `main` as the actual default branch. |
| `gitx ship main` with `prBase: "dev"` | Target the explicit `main`; do not rewrite the saved preference. |
| `gitx ship dev` with no remote `dev` | Stop before creating a branch or commit; report the missing base. |
| Matching open PR plus new local commits | Check and push new commits before returning the existing URL. |
| Open PR from the source into `main`, request targets `dev` | Leave the existing PR's base unchanged; create or reuse the separate PR into `dev`. |
| Check failure, unavailable required check, or rejected push | Stop publication at that stage; report completed work and the blocker. |
