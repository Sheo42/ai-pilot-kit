# Starting a new project with this method

A checklist, in order. Each step says who does it.

## Before the repository

1. **Owner:** write the need in a few sentences: who the users are, what
   problem it solves, what "first useful version" means.
2. **AI:** turn it into a project definition (scope, users, first
   architecture ideas, roadmap, open questions, numbered). Every assumption
   the AI makes is listed and dated, for the owner to confirm.
3. **Owner:** answer the open questions by number.
4. **Owner:** create the repository from the kit ("Use this template",
   private) and one Claude project for it, with the repository attached.
   Write the project instructions: "Always number questions and list items
   so the user can answer by number", plus the owner's language
   preferences.

## First pull request: the method

1. **AI:** run `scripts/kit/init.py` (see the kit's `README.md`), then
   decide each item it lists as left to do.
2. **AI:** adapt the roles to the domain: each agent's "Domain notes", the
   architect's views, the security engineer's areas, the tester's tagging
   syntax, the developer's stack; delete the notes that do not apply. Fill
   in the `verify` skill's commands per level, and `PHASES` in
   `scripts/ci/trace.py`.
3. **AI:** add the project definition as `docs/project-definition.md`.
4. **AI:** check that `.github/workflows/docs.yml` runs green on the pull
   request.
5. **Owner:** review and merge. From now on, merging approves.

## First week

1. **AI:** define the phases, named after who uses the product at each
   step (for example: simulator only, the owner's own lab, an internal
   reviewer, a first customer), each with a gate and a small Must set.
2. **AI (optional):** build one exploratory POC to click through, kept in
   `poc/`, closed by turning what the owner says about it into
   requirements.
3. **AI:** write only the requirements of phase 1 and the ADRs they need.
   Run one independent challenge on them (fresh session, other model).
4. **Owner:** triage the findings by number.
5. **AI:** build the walking skeleton: the thinnest end-to-end version,
   with tests tagged by acceptance criterion and CI green.

## Every session after that

1. Start: check which PRs merged since the last to-do update and close
   their items; reserve an ID range for the thread if it will add
   requirements or to-do items.
2. Work: one branch and one PR per task; reviews sized to the PR; a
   challenge for big decisions.
3. End: update the to-do list and glossary; the chronicler writes the
   journal entry; every lesson or proposal becomes a to-do item.
4. Owner: note the minutes spent reviewing, in the merge comment or the
   to-do item.

## At each phase gate

1. Global independent challenge over the whole design.
2. Tester's release report says Go; Must set verified.
3. Chronicler writes the phase entry and checks the open lessons.
4. Re-read this method: drop rules nobody followed, keep the ones that
   caught something, and send the general ones back to the kit.
