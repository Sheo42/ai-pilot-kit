<!-- Copy this block into the module's file in docs/requirements/ (see the table in its README). Keep the field names exactly. -->

### REQ-<MOD>-<NNN>: <short title, verb first>

| Field | Value |
|---|---|
| Category | FUN \| SEC \| PRF \| REL \| DAT \| INT \| UX \| OPS \| CMP \| TEC |
| Priority | Must \| Should \| Could \| Won't |
| Phase | <phase number and name, from docs/process.md> |
| Status | Draft |
| Version | 1 |
| Source | <who asked, where: meeting, doc, message> |
| Users | <organization type and role, e.g. Customer admin / Field technician> |
| Related | <other REQ IDs> |
| Related ADRs | <ADR IDs, filled by the architect> |

**Statement.** As a <user>, I need <capability> so that <value>.
(For non-functional requirements: The system shall <measurable property>.)

**Acceptance criteria**

- **AC1** (method: Test)
  Given <starting state: tenant, role, data>
  When <action or event>
  Then <observable, measurable outcome>
- **AC2** (method: Test)
  Given ...
  When ...
  Then ...

**Assumptions.** <what is assumed until confirmed, or "None">

**Numbers.** <for each number in the ACs: setting default, target or contract
value (see "Numbers in requirements" in the README); omit when obvious>

**Notes.** <context, examples, out of scope>

**Change log**
- v1, YYYY-MM-DD: created.
