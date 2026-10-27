# SKILL.md spec checklist

Source: the Agent Skills specification at https://agentskills.io/specification. Check every item. Report failures with the line and the fix.

## Folder

- [ ] The skill is a folder containing a file named exactly `SKILL.md`.
- [ ] Optional extras live in `scripts/`, `references/` or `assets/`, linked from SKILL.md by relative path, one level deep.

## Frontmatter

- [ ] The file starts with YAML frontmatter between `---` lines.
- [ ] `name` is present.
- [ ] `name` is 1-64 characters, lowercase letters, numbers and hyphens only.
- [ ] `name` doesn't start or end with a hyphen, and has no `--`.
- [ ] `name` matches the folder name.
- [ ] `description` is present and non-empty.
- [ ] `description` is 1024 characters or fewer.
- [ ] `description` says what the skill does AND when to use it, with the words a user would actually type.
- [ ] Optional fields, if present, are only: `license`, `compatibility` (500 characters max), `metadata` (string keys to string values), `allowed-tools`.
- [ ] If `allowed-tools` is present, warn that it's experimental and support varies between agents. This is a portability risk, not a failure.

## Body

- [ ] SKILL.md is under 500 lines (the spec's recommendation, about 5000 tokens). Move long material into `references/`.
- [ ] There are step-by-step instructions written as commands.
- [ ] There's at least one example of a good output or a worked input and output.
- [ ] Edge cases or "never do" rules are written down, not left implicit.
