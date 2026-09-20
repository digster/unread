# Prompts

## 2026-03-09

Implement the following plan:

Plan: Unread Articles — Raindrop URL Fetcher + GitHub Pages Random Redirect

Context: The user wants a simple utility that pulls bookmarked URLs from Raindrop.io by tag(s), saves them to a text file, and optionally commits+pushes. The repo doubles as a GitHub Pages site that redirects visitors to a random saved URL.

File structure includes: pyproject.toml, src/unread_articles/ (cli.py, raindrop.py, git_ops.py), tests/, index.html, urls.txt.

Implementation: Raindrop API client with pagination, Typer CLI with fetch/sync commands, git operations module, GitHub Pages index.html with random redirect, pytest tests with httpx mocking.

---

## 2026-03-09 (2)

Fix: Handle "nothing to commit" gracefully in sync command. When `sync` fetches URLs identical to what's already in `urls.txt`, `git commit` exits with status 1. Modify `git_ops.py` to check for staged changes using `git diff --cached --quiet` before committing, return a boolean, and update `cli.py` to show an appropriate message.

---

## 2026-09-19 — Tag matching investigation and implementation

Initial request (investigated without changing repository files):

- check if we can use multiple tags with the sync command
- check if multiple tags are used as OR or AND
- do not change anything in the repo yet

Follow-up request:

- ok, keep the default AND behavior and add another flag which adds OR behavior.

Planning clarification: the user selected **Both commands (Recommended)** when
asked whether `--or` should apply to both `fetch` and `sync` or only `sync`.

Implementation request:

PLEASE IMPLEMENT THIS PLAN:
# Add optional OR tag matching

## Summary
Add `--or` to both `fetch` and `sync`. Default behavior remains AND: bookmarks must match every supplied tag. With `--or`, bookmarks can match any supplied tag.

```bash
uv run unread-articles fetch python ai --or
uv run unread-articles sync python ai --or
```

## Implementation
- Define a shared boolean `--or` option, defaulting to `False`, with help explaining “match any supplied tag.”
- Add a keyword-only `match_any: bool = False` parameter to the query builder and API fetch function. Pass it from both commands.
- Preserve the existing default query: `#"python" #"ai"`.
- When enabled, append Raindrop’s documented operator: `#"python" #"ai" match:OR`.
- Preserve quoted tags containing spaces. Single-tag OR searches remain valid; an empty tag list still produces an empty query.
- Update CLI help and progress output to identify the selected matching mode. Keep collection filtering, pagination, URL saving, and sync’s git behavior unchanged.
- Update usage and architecture documentation, relevant code comments, and required prompt/work records.

## Verification
- Test unchanged default AND queries and explicit OR queries, including single tags, tags containing spaces, and empty lists.
- Verify mocked API requests receive the correct query and retain OR matching across pagination.
- Add CLI tests for both commands with and without `--or`, including compatibility with collection and sync commit-message options.
- Confirm missing tags still fail CLI validation.
- Mock network and git operations; use temporary output files.
- Run the full suite with `uv run pytest -v`.

## Delivery
No new dependencies or environment variables. Provide the verification results, edge cases covered, and a suggested commit message: `feat: add optional OR tag matching to fetch and sync`. Do not commit or push changes.
