#!/usr/bin/env python3
"""UserPromptSubmit hook — log genuine user corrections to error_log.md.

Claude Code delivers the UserPromptSubmit payload to this script via stdin
as JSON. We extract the user's prompt, strip all XML-style context blocks
(<system-reminder>, <task-notification>, <project-memory-context>, etc.)
so that keywords appearing in system-injected context or past-work memory
cannot false-trigger the detector, then match the remaining user-authored
text against a tight list of second-person correction phrases.

On a match, appends a single line to ~/.claude/memory/error_log.md:
    [YYYY-MM-DD HH:MM] USER_CORRECTION | <first 200 chars, whitespace flattened>

Fails silent on any error. A broken hook must never interrupt the user.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

LOG_PATH = Path.home() / ".claude" / "memory" / "error_log.md"

# Tight second-person correction phrases only.
# Bare `不对` / `错了` / `wrong` / `again` false-trigger on memory context,
# code snippets, documentation and injected system reminders that happen to
# contain the word, so they are NOT included here.
PATTERNS = [
    r"你又错了",
    r"你错了",
    r"你搞错",
    r"你说错",
    r"不对啊",
    r"不对不对",
    r"这不对",
    r"这明显不对",
    r"不是这样",
    r"不是这个意思",
    r"不是这么",
    # Python 3's \b treats CJK chars as word chars, so we use ASCII-only
    # lookarounds instead — this avoids false matches where an English phrase
    # is embedded in Chinese text and vice versa.
    r"(?<![A-Za-z])wrong again(?![A-Za-z])",
    r"(?<![A-Za-z])that'?s wrong(?![A-Za-z])",
    r"(?<![A-Za-z])that'?s not right(?![A-Za-z])",
    r"(?<![A-Za-z])you already (did|said)(?![A-Za-z])",
    r"(?<![A-Za-z])nope(?![A-Za-z])",
]
CORRECTION_RE = re.compile("|".join(PATTERNS), re.IGNORECASE)

# Strip <tag>...</tag> blocks (with attributes), looping until stable so
# adjacent / nested blocks all get removed, then drop any stray tags.
XML_BLOCK_RE = re.compile(r"<([A-Za-z][\w:-]*)\b[^>]*>.*?</\1>", re.DOTALL)
XML_STRAY_RE = re.compile(r"<[^>]+>")
# Strip fenced code blocks (``` … ```) and inline code spans (` … `) so a
# user pasting code that contains a correction phrase (e.g. a string literal
# "wrong again") doesn't false-trigger.
FENCED_CODE_RE = re.compile(r"```[\s\S]*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
WHITESPACE_RE = re.compile(r"\s+")

# Normalise Unicode smart quotes and dashes to ASCII so macOS auto-correct
# (' → ' / ’, " → “ / ”) doesn't cause matches like "that's wrong" to miss.
SMART_CHARS = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201A": "'", "\u201B": "'",
    "\u201C": '"', "\u201D": '"', "\u201E": '"', "\u201F": '"',
})


def strip_xml(text: str) -> str:
    prev = None
    while prev != text:
        prev = text
        text = XML_BLOCK_RE.sub(" ", text)
    text = XML_STRAY_RE.sub(" ", text)
    text = FENCED_CODE_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)
    text = text.translate(SMART_CHARS)
    return WHITESPACE_RE.sub(" ", text).strip()


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    prompt = payload.get("prompt") or ""
    if not prompt:
        return 0
    cleaned = strip_xml(prompt)
    if not cleaned or not CORRECTION_RE.search(cleaned):
        return 0
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        excerpt = cleaned[:200].replace("\n", " ")
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            fh.write(f"[{stamp}] USER_CORRECTION | {excerpt}\n")
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
