# Maintaining the kit

This file is for sessions that change the kit itself. `scripts/kit/init.py`
removes it from a new project.

This repository is both the place where the kit is maintained and the
template projects are made from. What a project gets is the copy made by
"Use this template", with the kit-only parts removed by `init.py`; nobody
starting a project clones this repository. Keep it that way: a change here
must leave `main` ready to be copied, and the README must keep saying what
a new project needs and what it does not.

## Rules

1. **No domain.** Nothing about a product, a customer, an employer or a
   vendor: no names, product names, specifications, hostnames or machine
   names. Examples are neutral ("a delivery-van fleet", "devices, sign-in,
   payments"). A third-party document is summarised and cited, never copied.
2. **Placeholders stay unfilled** here. A new placeholder goes into the
   table of `README.md` and the `values` of `scripts/kit/init.py`.
3. **A change comes from a project.** Each pull request says which
   project's experience it comes from (its lesson, ruling or review),
   in general words, and whether a project rule was made more general on
   the way.
4. **One owner.** Only the kit's owner merges. The rules of
   `docs/process.md` apply here too, except the ones about requirements,
   phases and the product.
5. **Lessons.** A lesson a project learned goes into
   `docs/chronicle/lessons.md` ("Inherited from earlier projects") when it
   is not already a rule; when it is, the rule is enough.

## Checks

`.github/workflows/kit.yml` runs the CI scripts' tests, among them
`scripts/ci/tests/test_kit_init.py`: it makes a project with
`scripts/kit/init.py`, checks no placeholder is left, and runs that
project's document checks. The project workflow, `docs.yml`, is skipped
here (the placeholders are not filled). Locally:

```
python3 -m pytest -q scripts/ci/tests
```

## Releases

1. `KIT_VERSION` holds the version; `CHANGELOG.md` says what changed, newest
   first, in plain words a project can act on.
2. Semantic versions: the minor number for new or changed rules, the patch
   number for wording and fixes. 1.0.0 once a second project has started
   from the kit.
3. A release is a git tag `vX.Y.Z` on `main`, made by the owner.
