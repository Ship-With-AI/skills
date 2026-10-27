---
name: write-it-down
description: Use this skill whenever the user wants to turn a repeated task into an Agent Skill, write a SKILL.md, or check an existing skill. Trigger on "turn this into a skill", "write a skill for my weekly X", "I keep explaining this every week", "make this repeatable", "write it down as a skill", "review my SKILL.md", "why doesn't my skill trigger", or "/write-it-down". Also use it when the user pastes the same context they have pasted before and complains the output is "almost right". It interviews the user one question at a time, fills a one-file SKILL.md template that follows the open Agent Skills spec, and reviews skills for the four mistakes that stop them from working.
---

# Write It Down

Turn work the user repeats every week into a portable Agent Skill, or fix a skill that doesn't work.

## Overview

This skill has two modes. Pick one based on context:

- **INTERVIEW mode**: The user has a task but no skill yet. Interview them, then fill the template.
- **REVIEW mode**: The user has a SKILL.md (a path or pasted text). Check it and propose fixes.

If unclear, ask: "Do you want to write a new skill, or check one you already have?"

The output follows the Agent Skills open standard (agentskills.io), so it loads in any agent that supports skills, not only the one running this conversation.

---

## INTERVIEW Mode

### Step 1: Name the task

Ask for the task in one line, and when they last did it. If they list several tasks, ask them to pick one. One skill per job.

### Step 2: Interview, one question at a time

Ask one question, wait for the answer, then ask the next. Never send the whole list at once. Cover these six areas in order:

1. **Trigger**: what makes them start the task, and the exact words they'd type to ask an agent for it.
2. **Inputs**: what they start from (files, tools, dashboards, data) and where each one lives.
3. **Steps**: the steps in order, including the ones they'd skip when explaining it to someone.
4. **Judgment calls**: where a smart newcomer would get it wrong, and the rule they apply.
5. **Output**: what "done" looks like, who reads it, and one real past output they were happy with.
6. **Never**: anything they never include or never do.

Follow up when an answer is vague ("it depends", "the usual way", "I just know"). Ask what it depends on. Those follow-ups are where the judgment calls come out. Stop when another question wouldn't change the file.

### Step 3: Fill the template

Read `assets/SKILL-template.md` and fill every placeholder from the answers.

- `name`: lowercase letters, numbers and hyphens only, 64 characters max, no leading, trailing or double hyphens. It must match the folder name.
- `description`: under 1024 characters. Say what the skill does AND when to use it, using the trigger words from area 1.
- Write steps as commands that start with a verb, never as a story.
- Paste the real example from area 5 under `## Example`, trimmed if it's long.

### Step 4: Self-review

Run the REVIEW mode checks on the file you just wrote and fix anything that fails before showing it.

### Step 5: Output

Give the user:

1. The folder path to create: `<name>/SKILL.md`.
2. The full file.
3. A short list titled **"I guessed these"**: every detail you filled in without a direct answer. The user corrects these before saving.
4. How to test it: put the folder in the agent's skills directory, ask for the task in plain words *without* naming the skill, then try the same folder in a second tool.

---

## REVIEW Mode

### Step 1: Load the skill

Read the SKILL.md (and its folder, if a path was given). If there's no frontmatter, say so first. Nothing else matters until it's there.

### Step 2: Check the spec rules

Read `references/spec-checklist.md` and check every rule in it. Report each failure with the line and the fix.

### Step 3: Check the four mistakes

1. **Description too vague to trigger**: would an agent match it against the words the user actually types? If the user has to name the skill to make it run, it fails.
2. **Narrating instead of instructing**: flag sentences like "I usually start by…" and rewrite them as commands.
3. **Five jobs in one skill**: if the description covers more than one job, propose a split, with a name and description for each part.
4. **No example output**: if there's no example, ask the user for a real past output to add.

### Step 4: Output

List the fixes in priority order (description first, because it decides whether the skill runs at all). Then offer the corrected file in full. Don't rewrite the user's voice or rules. Change only what the checks flagged.

---

## Important Principles

- **One question at a time.** A list of six questions gets six short answers. One question gets the real answer.
- **The description is the trigger.** It's the only part an agent reads before deciding to load the skill. Spend the most care there.
- **Commands, not stories.** Every step should have a clear finish line.
- **Show, then tell.** One real example fixes more drift than three extra rules.
- **Keep it short.** Keep SKILL.md under 500 lines. Move long reference material into `references/` and link it.
- **Never invent the user's rules.** Anything you guessed goes in the "I guessed these" list, not silently into the file.
