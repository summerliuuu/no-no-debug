#!/usr/bin/env bash
# PostToolUseFailure hook — log tool failures to error_log.md.
#
# Claude Code delivers the failure payload on stdin as JSON. We parse it
# with jq (or fall back to a generic entry if jq is missing / the payload
# is malformed) and append a single line:
#   [YYYY-MM-DD HH:MM] <CATEGORY> | <tool_name> | <error summary>
# where CATEGORY is BUILD_FAIL for Bash, FILE_FAIL for Write/Edit,
# TOOL_FAIL otherwise.
#
# Fails silent on any error.

set -u

log_dir="$HOME/.claude/memory"
log_file="$log_dir/error_log.md"
mkdir -p "$log_dir" 2>/dev/null || exit 0
touch "$log_file" 2>/dev/null || exit 0

ts="$(date '+%Y-%m-%d %H:%M')"

if ! command -v jq >/dev/null 2>&1; then
  printf '[%s] TOOL_FAIL | unknown | jq_not_installed\n' "$ts" >> "$log_file"
  exit 0
fi

payload="$(cat)"
tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // empty' 2>/dev/null)" || tool_name=""
error_summary="$(printf '%s' "$payload" | jq -r '.error // .stderr // .message // "unknown_error"' 2>/dev/null)" || error_summary=""

if [ -z "$tool_name" ]; then
  printf '[%s] TOOL_FAIL | unknown | parse_error\n' "$ts" >> "$log_file"
  exit 0
fi

case "$tool_name" in
  Bash) category="BUILD_FAIL" ;;
  Write|Edit) category="FILE_FAIL" ;;
  *) category="TOOL_FAIL" ;;
esac

# Flatten newlines and cap length so a huge stderr dump can't bloat the log.
error_summary="$(printf '%s' "$error_summary" | tr '\n' ' ' | head -c 120)"

printf '[%s] %s | %s | %s\n' "$ts" "$category" "$tool_name" "$error_summary" >> "$log_file"
exit 0
