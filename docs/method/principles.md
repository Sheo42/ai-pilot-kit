# Principles

Everything in the method follows from a few ideas. When a rule seems odd,
check it against these.

1. **The AI does the work; one person decides.** Every document, test and
   line of code is written by AI threads and agents. The product owner
   approves requirements, accepts ADRs, merges pull requests and deploys.
   Agents propose; nothing becomes true until the owner merges it. Merging a
   pull request approves the requirements and accepts the ADRs in it.

2. **The scarce resource is the owner's attention, not work time.** Cost is
   counted in pull requests and minutes of the owner's review, never in
   hours or weeks of work. A process step is worth adding only if it saves
   more review time than it costs. A finding the owner must triage is a
   cost too.

3. **Everything is numbered so it can be answered by number.** Questions,
   options, findings and list items are numbered; each question, option
   and finding comes with a suggested answer (plain steps and instructions
   do not); the owner answers "1 yes, 2 no, 3 as suggested". Requirements,
   acceptance criteria, ADRs and to-do items have stable IDs that are never
   reused.

4. **The repository is the memory.** AI sessions start without the
   discussion that came before. Anything that must survive a session is
   written in the repository (requirements, ADRs, to-do list, glossary,
   chronicle) or in project memory, never left in a conversation.

5. **Trace everything.** Every piece of code traces to a requirement, every
   acceptance criterion to a test, every decision to an ADR. Traceability is
   what lets one person check the work of many agents.

6. **The author never reviews alone.** Each change is reviewed by roles that
   did not write it; big decisions are attacked by an independent
   challenger, in a fresh session, on a different model, reading only the
   repository.

7. **Small, gated steps.** Work is cut into phases named after who uses the
   product at that point, each with its own small Must set and a gate that
   can actually be passed. One branch and one pull request per task.

8. **Rules are checked by tools where possible.** A rule that only lives in
   a document is soon ignored; a rule a CI script checks is kept.

9. **Record how it was built.** A chronicler records the steps and lessons,
   so the method can be judged and reused. This kit is the result.

10. **Do not trust the tests the AI wrote.** The tests come from the same
    agents as the code, so a green build proves less than it seems. At each
    phase gate the code is mutated (a line changed on purpose) and a test
    must fail each time; each mutant that survives in a critical module gets
    a verdict. In the first project, the first baseline scored 72 to 86% per
    part with every test green, most survivors in the critical modules were
    real gaps, and one was a real bug, fixed the same day.
