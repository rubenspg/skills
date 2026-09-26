---
name: wrap-up
description: Close out a coding or debugging session by filing what was learned in the right place in the repo (a regression test, the commit or PR body, a CLAUDE.md rule, a runbook, or a decision record). Use when the user says "wrap up", "wrap this up", "we're done", "close this out", "write this down", or "document the fix", and after fixing a bug, resolving an incident, or changing a design decision.
---

# Wrap-up

A session is not done until what it taught is stored where the next person, or the next Claude session, will find it. Chat history and Claude Code's auto memory don't count: one disappears, the other stays on a single machine.

## 1. Summarize and confirm

Write a four-line summary and show it to the user before filing anything:

- **Symptom**: what was observed, in the user's terms
- **Root cause**: the actual reason, not the first suspect
- **Fix**: what changed, with file paths
- **Verified by**: the test, query, or manual check that proves it

If any line is unknown, ask. Don't guess a root cause.

## 2. Route each lesson

Use only the rows that apply. Most sessions need the first two and nothing else.

| What was learned | Where it goes |
|---|---|
| The bug must not come back | A regression test next to the code it protects |
| What broke and why | The commit message or PR body (use the summary above) |
| A rule every future session must follow | One imperative line in `CLAUDE.md` |
| How to diagnose or fix it if it recurs | `docs/runbooks/<symptom-slug>.md` |
| A change to how the system is designed | `docs/decisions/NNNN-<slug>.md` |

Tests for "is this a CLAUDE.md rule?": would a competent newcomer break it without being told, and does it apply beyond this one bug? If either answer is no, it belongs somewhere else.

## 3. Write

- **CLAUDE.md**: add one line under the most relevant heading. State the rule and, briefly, why. Don't duplicate an existing line; tighten it instead. Keep the file short.
- **Runbook / decision**: use the templates in `references/templates.md`. Create the `docs/` folders if missing. Decision numbers are the next unused four-digit number in `docs/decisions/`.
- Never write secrets, tokens, customer data, or internal hostnames into any of these files. Refer to where a secret lives, never its value.

## 4. Hand back

- Propose a commit message built from the summary. Don't commit or push unless the user asks.
- List each file you created or changed, one line each.
- If a decision record was written, say so explicitly: it may need to reach other places the user keeps product context.
