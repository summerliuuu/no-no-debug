# Changelog

All notable changes to this project will be documented in this file.

## [1.2.0] — 2026-04-16

### Fixed (critical — affects every previous install)

- **`settings.json` hook template was broken.** The v1.0/v1.1 template referenced environment variables `$CLAUDE_TOOL_NAME` and `$CLAUDE_USER_PROMPT` that do not exist in Claude Code's hook contract. Hook context is delivered as a **JSON payload on stdin**, so every tool-failure log line ended up as `TOOL_FAIL |  failed` with empty fields, and the UserPromptSubmit correction detector never matched anything. Anyone who installed this skill per the README was silently getting zero useful data in their `error_log.md`.
- **UserPromptSubmit false-triggered on past context.** The previous pattern list (`不对`, `错了`, `wrong`, `again`, …) matched bare substrings, so injected `<system-reminder>`, memory snippets, task notifications, and documentation containing any of those words would fire USER_CORRECTION on every turn — creating closed-loop pollution where the fake correction got saved to memory and then re-injected on the next session.
- **Python `\b` on CJK text.** Python 3's word-boundary metacharacter treats Chinese characters as word characters, so `\bwrong\b` did not match `wrong` inside a predominantly-Chinese prompt. Replaced with ASCII-only lookarounds `(?<![A-Za-z])…(?![A-Za-z])`.

### Added

- `hooks/user_prompt_filter.py` — standalone Python hook that reads stdin JSON, strips all XML-style context blocks (`<system-reminder>`, `<task-notification>`, `<project-memory-context>`, …) plus fenced and inline code blocks from the prompt, normalises Unicode smart quotes to ASCII (so macOS auto-corrected `that's wrong` still matches), then checks against a tight list of second-person correction phrases only. Fails silent on any error.
- `hooks/post_tool_failure.sh` — standalone Bash hook that parses stdin JSON with `jq`, categorises the failure (`BUILD_FAIL` / `FILE_FAIL` / `TOOL_FAIL`), and appends a properly-filled log line. Fails silent if `jq` is missing.
- **Two new tracked dimensions** (now 18 total):
  - **真实环境验证 / Real-env Verification** — claimed a fix worked based on a sandbox / simplified test harness, but it failed under the real production command string (extra shell-escape layer, missing `$PATH`, different stdin format).
  - **跨 agent 采信 / Cross-agent Trust** — trusted another agent's "pass" report without independent re-verification; over-adopted a reviewer's over-engineering suggestions; under-challenged a reviewer's flagged issue that was actually wrong.
- **Gate 2 strengthened**: verification must use the exact production command string, not a locally-equivalent variant. Explicit callout for shell/hook changes with multiple escape layers.
- **Gate 3 strengthened**: for changes reviewed by a second agent, re-run verification independently in your own environment — a sandbox pass is not a real-environment pass.

### Changed

- `settings.json` template now invokes the two standalone scripts above with a single command line each, removing all multi-layer shell-escape fragility from the config file.
- Mechanism 1 correction trigger condition now points at the exact pattern list in Mechanism 6 instead of inlining loose keywords.
- Mechanism 6 documentation rewritten to explain the stdin JSON contract up-front, so future installers know not to reach for `$CLAUDE_*` env vars.

### Migration from 1.1.0

1. Pull the new `hooks/` directory and copy both files to `~/.claude/hooks/`:
   ```bash
   mkdir -p ~/.claude/hooks
   cp hooks/user_prompt_filter.py ~/.claude/hooks/
   cp hooks/post_tool_failure.sh ~/.claude/hooks/
   chmod +x ~/.claude/hooks/post_tool_failure.sh
   ```
2. Replace the `PostToolUseFailure` and `UserPromptSubmit` blocks in your `~/.claude/settings.json` with the new single-line invocations from `SKILL.md` → Mechanism 6 → Settings.json format.
3. Optionally clean old noise from `~/.claude/memory/error_log.md` — entries like `TOOL_FAIL |  failed` with empty fields came from the broken template and can be safely deleted.

## [1.1.0] — 2026-04-11

- Expanded compatibility to all AI coding assistants (ChatGPT, Cursor, Copilot, …) via pasting `SKILL.md` into system prompts.
- English `README.md` promoted to primary, Chinese version moved to `README.zh-CN.md`.

## [1.0.0] — 2026-04-08

- Initial release: six-mechanism self-evolution system.
