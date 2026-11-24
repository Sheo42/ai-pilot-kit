# Lessons

What to keep, change or avoid in the way of working, one or two sentences
each, with the step that showed it and the to-do item that applies it.
"Kept" lessons need no to-do item.

## Inherited from earlier projects

Lessons a project learned that are not rules of the kit, in general words.
The ones that became rules are in `docs/process.md`, `docs/coordinator.md`
or an agent, and are not repeated here.

### Deciding with the owner

| # | Lesson |
|---|---|
| 1 | **Keep.** Numbered questions with suggested answers let the owner decide many items in one message; a ranked recommendation with reasons helps more than a list of every option. |
| 2 | **Keep.** Something clickable (a POC) gets faster and more concrete feedback than a list of questions; a short product definition first makes the POC quick to build and close to the intended design. |
| 3 | **Change.** Assumptions the AI writes early travel into later documents, and defaults age fast: put them to the owner early, dated, and re-check them before they become ADRs. |
| 4 | **Change.** A "let the user edit it" request hides a source-of-truth question: answer it in a requirement first. |
| 5 | **Change.** A requirement that pins a deliberate limitation also says what the user sees because of it, or opens a to-do to lift it; otherwise the owner meets it later as a bug. |
| 6 | **Change.** A name check searches general tech brands, not only the product's own field. |
| 7 | **Change.** Ask the owner for a decision once its challenge has reported, or say on the question that a challenge is still running. |

### Planning and documents

| # | Lesson |
|---|---|
| 8 | **Change.** Walk the skeleton early; documents are nearly free for AI to write, but each one costs the owner a review and must stay consistent. |
| 9 | **Keep.** A gate is useful only if it can be passed; phases cut by who uses the product give natural gates. |
| 10 | **Keep.** Splitting a "minimum" from declared "extensions" turns an unagreed roadmap into a contract usable now. |
| 11 | **Keep.** Asking "how would the system know?" of each rule finds rules with no signal behind them. |
| 12 | **Change.** A phase is read per requirement, not per acceptance criterion: a criterion that belongs to a later phase means a separate requirement. |
| 13 | **Change.** Read the code before writing a design brief, and check the design's nouns against the code: the brief usually changes. |
| 14 | **Keep.** Before starting a "design X" thread, check whether X is already designed; a delta ADR is cheaper than a second design. |
| 15 | **Change.** When two agents write requirements and an ADR in parallel, one owns the names first, each owns its own files, and the lead thread relays what one finds for the other. |
| 16 | **Change.** Answers agreed in a PR description are copied into the ADR or requirement in the same change. |
| 17 | **Change.** Rules the owner gives in chat land in project memory first, which does not travel: move them into the repository, and the general ones into the kit. |

### Reviews and challenges

| # | Lesson |
|---|---|
| 18 | **Keep.** A reviewer who took no part in a decision finds what the authors stopped seeing, mostly in the gaps between documents; a global pass finds another class of problems (contradictions between documents, requirements nobody owns, a plan too big). |
| 19 | **Keep.** A code review checks code against its design; a challenge questions the design. On contract, schema and sign-in changes, run both: their findings rarely overlap. |
| 20 | **Keep.** Run the blind challenge on a security design even after an in-thread security review: the engineer who shaped a design misses what it hides. |
| 21 | **Keep.** Challenge the build even when the design was challenged, and challenge the commit that holds the review's fixes: a fix can open the next finding. |
| 22 | **Keep.** Let the challenger run the real stack and play the outside party (a device, a client, an attacker) with the inputs it may choose; reading alone misses behaviour. |
| 23 | **Keep.** The challenger checks a design against the vendor reference and the files already on `main`, not only against the design's own documents. |
| 24 | **Change.** Fixes can land between a challenge and its triage: before passing verdicts, the challenger reads the fix commits again. |
| 25 | **Keep.** Review what sits next to a change, not only the change, and when a change alters what CI runs, review its concurrency and cancel rules with it. |
| 26 | **Keep.** Check a review finding about test code against the last green run before fixing it: a run can disprove it. |
| 27 | **Keep.** Challenge a practice taken from an outside article against the project's own constraints before adopting it. |

### Tests

| # | Lesson |
|---|---|
| 28 | **Keep.** Test against the real component (its image, the running service, the full stack), not only its configuration or unit tests; and a spike runs the service with the stack's own settings. |
| 29 | **Change.** Show that a new test fails without the line it protects, and make tests that need a service fail, not skip, when it is missing. |
| 30 | **Avoid.** A test that accepts several outcomes ("403 or 404") hides a gap between the code and the approved text: assert the exact value. |
| 31 | **Change.** Test a rule with the innocent case that looks like the attack, with inputs beside its own list, and with the worst input an outsider can write; test a clean-up with an item it cannot remove. |
| 32 | **Change.** Measure a limit with the costliest shape of input the sender may choose, and give a default sized on a count a test that measures the count. |
| 33 | **Change.** When accepting "a wrong case happens once" as a residual, follow it one message further: check what happens to the next correct one. |
| 34 | **Change.** A fix for "this person is refused" is tested in every order the person can meet the refusal, starting with the order the product's own message leads to. |
| 35 | **Keep.** Test a parser with captured real lines from the source, not hand-written ones; check a claim about what a component keeps or drops by running it. |
| 36 | **Keep.** Test a conformance kit with senders that break rules its own tests did not think of. |
| 37 | **Keep.** Test a machine interface with an AI acting as the real client, given only the interface document. |
| 38 | **Change.** A user-facing message about a wait or a limit is computed from the limit's settings and tried once. |
| 39 | **Change.** A new public route or field breaks tests that list routes or compare answers exactly: grep for them before pushing. |
| 40 | **Change.** The local check covers every project CI type-checks, not only the main build. |
| 41 | **Change.** An ID format outgrows the patterns that read it: test the scripts with the next digit count before it arrives. |

### Security habits

| # | Lesson |
|---|---|
| 42 | **Avoid.** Test secrets shaped like real keys; answer a secret-scan false positive by allowlisting exact values, never file paths; look for secrets in the raw text, not through a parser that may stop first. |
| 43 | **Avoid.** A cheap filter kept beside a digest leaks the secret: count what every stored value says about it. |
| 44 | **Change.** A rate limit placed after the checks that can refuse does not limit the refusals; count the call first. |
| 45 | **Change.** A filter in front of a server reads requests the way the server does (decoded), or fails closed. |
| 46 | **Change.** When a rule moves to another layer (a route to the database), list every condition it had; when a counter or an alarm is narrowed, list what else falls silent. |
| 47 | **Change.** A rule that drops input for good needs a way out (a time limit) and a trace (a log line or stored count). |
| 48 | **Change.** Text for an AI reader gets its own review: give fixed values parsed from the source, never free text, and totals by default with the detail on request. |
| 49 | **Avoid.** Removing a guard on outside data because a linter calls it unnecessary: the types promise what nothing checks. |

### Running the project

| # | Lesson |
|---|---|
| 50 | **Keep.** When a symptom may come from the platform, first test with a trivial server that bypasses the stack. |
| 51 | **Keep.** Measure before parallelizing CI: log timestamps give durations without a new run, and the biggest cut is often a repeated set-up. |
| 52 | **Change.** A new required setting ships with its upgrade path, and stopping or checking the service never depends on it. |
| 53 | **Change.** An accepted risk with no upstream fix gets an exception with an expiry date in every scanner that reads it. |
| 54 | **Change.** When a grouped dependency update fails, test each package alone before ignoring the group. |
| 55 | **Keep.** Have worker agents save their state as they go, so a usage limit does not lose the work. |
| 56 | **Avoid.** Copying a repository file back from a shared files folder: it may come back changed (added metadata). Write repository files directly in the repository. |
| 57 | **Change.** Code that runs on a device is checked on its target machine (no clock until the network answers, for example), not only in tests. |
| 58 | **Keep.** When a strict linter lands during a parallel migration, skip the files the other PR rewrites; whichever PR merges second finishes them. |

## This project

| # | Lesson | Shown by | To-do |
|---|---|---|---|
