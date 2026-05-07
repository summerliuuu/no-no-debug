#!/usr/bin/env bash
# PostToolUseFailure hook — log failures + warn on consecutive same-tool failures.
#
# 1. Appends a log line to error_log.md (original behavior)
# 2. Tracks recent failures in /tmp/.nnd_tool_fail_history
# 3. If the same tool fails 2+ times within 5 minutes, outputs a warning
#    that tells the AI to switch to an alternative tool.
#
# Fails silent on any error.

set -u

log_dir="$HOME/.claude/memory"
log_file="$log_dir/error_log.md"
history_file="/tmp/.nnd_tool_fail_history"
mkdir -p "$log_dir" 2>/dev/null || exit 0
touch "$log_file" 2>/dev/null || exit 0

ts="$(date '+%Y-%m-%d %H:%M')"
now_epoch="$(date +%s)"

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

error_summary="$(printf '%s' "$error_summary" | tr '\n' ' ' | head -c 120)"
printf '[%s] %s | %s | %s\n' "$ts" "$category" "$tool_name" "$error_summary" >> "$log_file"

# --- Consecutive failure detection ---

touch "$history_file" 2>/dev/null || exit 0

# Append this failure
printf '%s|%s|%s\n' "$now_epoch" "$tool_name" "$error_summary" >> "$history_file" 2>/dev/null

# Clean entries older than 5 minutes
cutoff=$((now_epoch - 300))
if [ -f "$history_file" ]; then
  awk -F'|' -v cutoff="$cutoff" '$1 >= cutoff' "$history_file" > "${history_file}.tmp" 2>/dev/null && \
    mv "${history_file}.tmp" "$history_file" 2>/dev/null
fi

# Count recent failures for this tool
count=0
if [ -f "$history_file" ]; then
  count="$(grep -c "|${tool_name}|" "$history_file" 2>/dev/null)" || count=0
fi

if [ "$count" -ge 2 ]; then
  case "$tool_name" in
    Grep|Glob)
      alt="Bash with 'find' and 'grep -r'" ;;
    Read)
      alt="Bash with 'ls' to verify path first, then Read" ;;
    mcp__playwright__*|mcp__pinchtab__*|mcp__agent-browser__*)
      alt="a different browser tool, or Bash with 'curl'" ;;
    *)
      alt="Bash or an alternative approach" ;;
  esac
  printf '[no-no-debug] %s has failed %d times in 5 minutes. Switch to %s.\n' "$tool_name" "$count" "$alt"
fi

exit 0
