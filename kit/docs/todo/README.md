# The kit's own to-do list

What is open on the kit itself, not on a project. It lives here, under
`kit/`, because `docs/todo/` is the first to-do list of every new project
made from the kit; `scripts/kit/init.py` removes this folder.

The rules and columns are those of [docs/todo/](../../../docs/todo/README.md):
one file per reserved number range, rows never move, closing sets the Status
to `Done YYYY-MM-DD`. The Owner of an item waiting on the kit's owner is
`owner`. An item that came from a project says so in its Item, with the
project's own to-do number, in general words (`KIT.md`, rule 3).

Reading the list:

```
python3 scripts/ci/todo_view.py kit --owner owner
```

The kit's tests run the to-do checks on these files
(`scripts/ci/tests/test_kit_init.py`).
