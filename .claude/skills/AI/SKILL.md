```markdown
# AI Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill introduces the core development patterns and workflows found in the "AI" Python codebase. You'll learn the project's coding conventions, file organization, and how to efficiently perform common tasks such as removing obsolete files and updating documentation. The repository is Python-based, with no specific framework, and emphasizes clear file naming, relative imports, and named exports.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - Example: `data_loader.py`, `model_utils.py`

### Import Style
- Use **relative imports** within modules.
  - Example:
    ```python
    from .utils import preprocess_data
    ```

### Export Style
- Use **named exports** (explicitly define what is exported).
  - Example:
    ```python
    def train_model(...):
        ...
    __all__ = ["train_model"]
    ```

### Commit Patterns
- Commit messages are freeform, typically concise (~26 characters).
  - Example: `fix: update data loader logic`

## Workflows

### File Removal Workflow
**Trigger:** When you need to remove obsolete or deprecated files from the repository (e.g., after a refactor or cleanup).  
**Command:** `/remove-files`

1. **Identify** files that are no longer needed (e.g., old scripts, configs, docs).
2. **Delete** the files from the repository.
3. **Commit** the deletions with a clear message indicating what was removed.

**Files commonly involved:**
- `*.py`, `*.md`, `*.json.example`, `*.sh`, `*.html`, `*.yaml`, `*.toml`, `*.txt`, `*.yml`
- `.dockerignore`, `.env.example`, `.gitignore`, `.nojekyll`, `.LICENSE`
- Folders: `src/**`, `tests/**`, `app/**`, `config/**`
- `Dockerfile`

**Example:**
```bash
git rm src/old_module.py
git commit -m "remove: deprecated old_module.py"
```

---

### Documentation Update Workflow
**Trigger:** When you need to update or correct project documentation (e.g., after adding features or changing instructions).  
**Command:** `/update-docs`

1. **Edit** documentation files such as `README.md` to reflect the latest project state.
2. **Commit** the changes with a descriptive message.

**Files commonly involved:**
- `README.md`

**Example:**
```bash
nano README.md
git add README.md
git commit -m "docs: update usage instructions"
```

## Testing Patterns

- **Testing framework:** Unknown (not detected)
- **Test file pattern:** `*.test.ts` (TypeScript test files, though main code is Python)
- Tests may be written in TypeScript, possibly for frontend or API layers.
- No explicit Python testing framework detected; consider standardizing on `pytest` or similar for Python code.

## Commands

| Command        | Purpose                                            |
|----------------|----------------------------------------------------|
| /remove-files  | Remove obsolete or deprecated files from the repo  |
| /update-docs   | Update project documentation (e.g., README.md)     |
```
