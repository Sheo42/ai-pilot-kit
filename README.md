# AI pilot kit

A way of running a software project where AI sessions do the work and one
person, the product owner, decides. This repository is the starting point:
the rules every session follows, seven AI roles, the coordinator's
playbook, the document templates and the CI checks that keep them honest.

It was written from a first project run this way, then stripped of that
project's domain. The ideas behind it, and why each rule exists, are in
[docs/method/](docs/method/README.md).

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
| [.github/workflows/docs.yml](.github/workflows/docs.yml) | The project's document checks, on GitHub's hosted runners |

## Placeholders

| Placeholder | Meaning |
|---|---|
| `{{PROJECT}}` | Project name, as written in titles |
| `{{OWNER}}` | First name of the product owner |
| `{{PRODUCT}}` | One sentence: what the product is, for whom |
| `{{STACK}}` | Main languages and frameworks, once chosen |
| `{{SECURITY_AREAS}}` | The areas that need the security engineer |
| `{{DATE}}` | The start date |

Maintaining the kit itself: [KIT.md](KIT.md). Versions:
[CHANGELOG.md](CHANGELOG.md).
