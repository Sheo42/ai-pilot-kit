# Where CI runs

The checks of `.github/workflows/docs.yml` are scripts any computer can run.
This page says which computer: GitHub's hosted runners or a self-hosted
runner, and how one machine can serve several repositories.

## Rules

1. **A public repository never uses a self-hosted runner.** A pull request
   from a fork would run its code on the runner's machine. A public
   repository runs on GitHub's hosted runners, which cost nothing there.
2. **A private repository** runs on the hosted runners while its plan's
   free minutes last and the account's billing allows it, and otherwise on
   a self-hosted runner.
3. **The choice is a setting, not an edit.** `docs.yml` reads the
   repository variable `CI_RUNS_ON` (Settings, Secrets and variables,
   Actions, Variables). Unset, the job runs on `ubuntu-latest`. Set, it is
   the runner's labels as JSON, for example `["self-hosted", "linux"]`.
   Only the owner changes repository settings.

| Repository | Runner | `CI_RUNS_ON` |
|---|---|---|
| Public (the kit itself) | Hosted | Unset |
| Private, light checks, minutes left | Hosted | Unset |
| Private, heavy checks or no minutes | Self-hosted | `["self-hosted", "linux"]` |

## One machine, several repositories

1. **On a personal account**, a self-hosted runner belongs to one
   repository. One machine can still serve several: install one runner
   instance per repository, each in its own folder and running as its own
   service. Give them all the same labels, so every project sets the same
   `CI_RUNS_ON`.
2. **In an organisation**, one runner can be shared by its repositories,
   which gives one queue for all of them. This needs the repositories moved
   into the organisation, which changes their addresses.
3. Each runner instance takes one job at a time, but instances on the same
   machine share it. Two projects' runs at the same moment slow each
   other; heavy suites keep the turn-taking rules of `docs/process.md`
   ("Merge order") for each runner.
4. The machine needs `bash`, `git`, Python (installed by `setup-python`)
   and Node.js (for `npx` and the Markdown lint).
5. A new push to a pull request cancels the older run of the same
   workflow, so a runner never works on a commit nobody will merge. Runs on
   `main` always finish.

## Assumptions

Dated 2026-11-25, from GitHub Docs ("About billing for GitHub Actions",
"About self-hosted runners"), not re-checked against the current pages:

1. Hosted runners are free for public repositories; private repositories
   get a monthly allowance of minutes that depends on the plan.
2. A failed payment or a spending limit can stop hosted jobs before they
   start, even within the allowance: the job fails in seconds with no step
   run.
3. On a personal account, self-hosted runners are added per repository;
   runners shared across repositories need an organisation.
