# AI pilot kit

A way of running a software project where AI sessions do the work and one
person, the product owner, decides. The kit is what you take: the rules
every session follows, seven AI roles, the coordinator's playbook, the
document templates and the CI checks that keep them honest.

It was written from a first project run this way, then stripped of that
project's domain. The ideas behind it, and why each rule exists, are in
[docs/method/](docs/method/README.md).

## What you need, and what you do not

1. **You need only the kit.** A new project is a copy of this template,
   made by GitHub's **Use this template**. Everything the method needs is
   in that copy.
2. **You do not clone this repository.** It is where the kit itself is
   maintained (`KIT.md`, its own CI and tests); `scripts/kit/init.py`
   removes those parts from your copy. Your project never works here and
   never pushes here, except to send an improvement back by pull request.
3. **You do not need the first project.** The kit was written from it, but
   carries its rules and lessons; nothing in a new project refers to it.
4. **Your copy starts with its own history.** "Use this template" copies
   the files of `main`, not the kit's commits; `KIT_VERSION` and
   [CHANGELOG.md](CHANGELOG.md) say which kit version you started from.

## Start a project from it

1. On GitHub, **Use this template** → **Create a new repository**
   (private).
2. In a Claude project with the new repository attached, ask a session to
   run:

   ```
   python3 scripts/kit/init.py --project "<name>" --owner "<first name>" \
       --product "<one sentence: what it is, for whom>" \
       --security-areas "<for example: devices, sign-in, payments>"
   ```

   It fills the placeholders, removes the files only the kit needs, keeps
   `KIT_VERSION`, and lists what is left to decide by hand.
3. Follow [docs/method/bootstrap.md](docs/method/bootstrap.md) from
   "First pull request" on: adapt the roles' "Domain notes", write the
   project definition, merge.

The project then keeps its own copy and adapts it. Improvements that are
not specific to its domain come back here by pull request
(`docs/process.md`, "The kit").

## What is in it

| Path | Content |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Rules every session follows; role table |
| [.claude/agents/](.claude/agents/) | The seven roles |
| [.claude/skills/verify/](.claude/skills/verify/SKILL.md) | The `verify` skill: the checks a session runs before each commit |
| [docs/process.md](docs/process.md) | The team process |
| [docs/coordinator.md](docs/coordinator.md) | Coordinator playbook: threads, reviews, merge order, talking with the owner |
| [docs/todo/](docs/todo/README.md) | To-do list: one file per number range, its rules and the first items |
| [docs/glossary.md](docs/glossary.md) | Glossary with the process terms |
| [docs/traceability.md](docs/traceability.md) | How the requirements ↔ tests matrix is generated |
| [docs/requirements/](docs/requirements/README.md) | ID scheme, categories, priorities, statuses |
| [docs/templates/](docs/templates/) | Requirement and ADR templates |
| [docs/adr/](docs/adr/) | ADR index and ADR-0001 |
| [docs/reviews/](docs/reviews/README.md) | Independent challenge: brief for the challenger and file format |
| [docs/chronicle/](docs/chronicle/) | Chronicle README, agents history, lessons |
| [docs/method/](docs/method/README.md) | Why: principles, roles, workflow, artefacts, bootstrap checklist |
| [scripts/ci/](scripts/ci/) | Document checks, to-do view, traceability matrix, and their tests |
| [.github/workflows/docs.yml](.github/workflows/docs.yml) | The project's document checks, on GitHub's hosted runners or the runner `CI_RUNS_ON` names ([docs/method/ci-runners.md](docs/method/ci-runners.md)) |

## Placeholders

| Placeholder | Meaning |
|---|---|
| `{{PROJECT}}` | Project name, as written in titles |
| `{{OWNER}}` | First name of the product owner |
| `{{PRODUCT}}` | One sentence: what the product is, for whom |
| `{{STACK}}` | Main languages and frameworks, once chosen |
| `{{SECURITY_AREAS}}` | The areas that need the security engineer |
| `{{DATE}}` | The start date |

Maintaining the kit itself: [KIT.md](KIT.md); its own to-do list:
[kit/docs/todo/](kit/docs/todo/README.md). Versions:
[CHANGELOG.md](CHANGELOG.md).

The kit is under the MIT licence ([LICENSE](LICENSE)). A project made from
it does not inherit it: `scripts/kit/init.py` removes the file, and the
project's owner chooses the project's own licence, if any.
