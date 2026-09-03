---
name: case-study
description: Turns an existing internal script or tool into a buyer-facing case study and outreach message by inspecting the repository, recovering evidence, and interviewing only for facts the code cannot prove. Use when someone says "/case-study", wants to turn internal work into portfolio proof, document an automation, extract a case study from a repository, or pitch an existing tool to prospective clients.
---

# Case Study

Turn one internal tool that already works into a concise client-facing case study. Do not write new product code.

The goal is credible proof: one real problem, measurable before and after, two or three judgment calls, one reusable problem archetype, and one message the user can send today.

## Evidence rules

- Never invent users, metrics, outcomes, costs, incidents, or prospect names.
- Distinguish facts found in the repository from estimates supplied by the user.
- Cite repository evidence with file paths and symbols where useful, but translate it into buyer language in the final case study.
- Exclude secrets, personal data, private client identifiers, and proprietary implementation details unless the user explicitly approves them.
- Write for the buyer, not a code reviewer: outcomes and avoided costs before implementation details.

## Workflow

Work through these steps in order. Inspect first; ask only for facts the repository cannot establish. Ask one compact batch of questions rather than repeating questions already answered by files or the user.

### 1. Name the problem, not the tool

Inspect the README, entry points, tests, examples, documentation, and relevant git history. Identify:

- who used the tool;
- the single input it receives;
- the useful output or decision it produces;
- the manual or fragile process it replaced.

Write one sentence in the affected person's language. A non-programmer with the same problem should recognize their bad day.

If multiple tools or workflows are present, select the one with the strongest evidence of real use. Ask the user to choose only when two candidates are genuinely tied.

### 2. Quantify before and after

Look for timings, volumes, failure counts, support incidents, benchmarks, logs, or documented outcomes. Capture comparable before-and-after measures: time, error rate, volume, cost, or risk.

If the repository cannot prove them, ask the user for rough ranges. Label estimates as estimates. If no honest comparison is available, say so and use a concrete qualitative outcome instead of manufacturing precision.

### 3. Extract the judgment calls

Find two or three decisions a naive implementation would get wrong: validation, matching rules, deduplication, exception handling, safety limits, fallbacks, or deliberate refusal paths.

For each decision, state:

1. what the tool does;
2. why the obvious approach fails;
3. what failure or cost the decision prevents.

If no meaningful judgment call exists, explain that this tool is a receipt rather than a strong case study and ask whether to inspect another tool.

### 4. Generalize the archetype

Strip away company and domain-specific nouns. Name the broader problem pattern and the buyer role that repeatedly encounters it.

Ask the user for three real prospects from their network or target market if none were provided. Never fabricate relationships or claim a company has the problem without evidence.

### 5. Produce the case study

Write `CASE-STUDY.md` in the current project with this structure:

```markdown
# [Outcome-focused title]

## The problem
[The user's bad day, in buyer language.]

## Before and after
[Comparable evidence, with estimates labeled.]

## What I built
[One plain-language sentence.]

## Judgment calls
- **[Decision]:** [Why it mattered and what it prevented.]

## Who else has this problem
[Problem archetype, buyer role, and three user-confirmed prospects when available.]

## Outreach message
> I built a tool that took [before] down to [after] for [problem in buyer language], and designed it to [key judgment call] so [costly failure] does not happen. You're dealing with [archetype]. Worth 15 minutes?

## Evidence notes
[Repository paths supporting the claims; facts still requiring confirmation.]
```

Keep the client-facing case study near 200 words, excluding evidence notes. Replace the outreach placeholders with verified facts. If a fact is missing, leave a clearly labeled bracket rather than guessing.

Finish by showing the outreach message in chat and naming the one unresolved fact that would most strengthen it. Do not send the message or publish the case study without an explicit request.
