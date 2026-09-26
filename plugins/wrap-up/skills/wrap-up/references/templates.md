# Templates

## Runbook: `docs/runbooks/<symptom-slug>.md`

```markdown
# <Symptom as a user or alert would describe it>

Last seen: YYYY-MM-DD

## How to confirm
<The query, command, or log search that shows this is the problem.>

## Cause
<One or two sentences.>

## Fix
1. <Step>
2. <Step>

## Prevention
<The test, guard, or alert that now exists, with a path or link.>
```

## Decision: `docs/decisions/NNNN-<slug>.md`

```markdown
# NNNN. <Decision as a short statement>

Date: YYYY-MM-DD
Status: accepted

## Context
<What forced the decision. Link the incident or PR if there was one.>

## Decision
<What we now do.>

## Consequences
<What gets easier, what gets harder, what to revisit and when.>
```
