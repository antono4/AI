---
name: file-removal-workflow
description: Workflow command scaffold for file-removal-workflow in AI.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /file-removal-workflow

Use this workflow when working on **file-removal-workflow** in `AI`.

## Goal

Removes obsolete or deprecated files from the repository, often as part of a migration, refactor, or project cleanup.

## Common Files

- `*.py`
- `*.md`
- `*.json.example`
- `*.sh`
- `*.html`
- `*.yaml`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Identify files that are obsolete or deprecated.
- Delete the files from the repository.
- Commit the deletions with a message indicating removal.

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.