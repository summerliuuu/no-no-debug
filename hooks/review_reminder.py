#!/usr/bin/env python3
"""UserPromptSubmit hook — remind when error review is overdue.

Reads ~/.claude/memory/error_tracker.md for the Last Review Date and the
configured review frequency (default: 3 days). If enough days have elapsed,
prints a one-line reminder that the AI will act on to start the Mechanism 3
review cycle. A 4-hour cooldown (via a temp file) prevents the reminder from
firing on every single user message within the same session.

Fails silent on any error. A broken hook must never interrupt the user.
"""
from __future__ import annotations

import sys
import os
from datetime import datetime
from pathlib import Path

TRACKER = Path.home() / ".claude" / "memory" / "error_tracker.md"
COOLDOWN_FILE = Path("/tmp/.nnd_review_reminded")
COOLDOWN_HOURS = 4


def main() -> int:
    try:
        sys.stdin.read()
    except Exception:
        pass

    if not TRACKER.exists():
        return 0

    if COOLDOWN_FILE.exists():
        try:
            mtime = COOLDOWN_FILE.stat().st_mtime
            if (datetime.now().timestamp() - mtime) / 3600 < COOLDOWN_HOURS:
                return 0
        except Exception:
            pass

    try:
        content = TRACKER.read_text(encoding="utf-8")
    except Exception:
        return 0

    freq = 3
    for line in content.splitlines():
        if "review_frequency:" in line:
            try:
                freq = int(line.split("review_frequency:")[1].strip().rstrip(" ->"))
            except (ValueError, IndexError):
                pass

    for line in content.splitlines():
        if line.startswith("Last Review Date:"):
            date_str = line.split(":", 1)[1].strip()
            try:
                last_review = datetime.strptime(date_str, "%Y-%m-%d")
                days_since = (datetime.now() - last_review).days
                if days_since >= freq:
                    print(
                        f"[no-no-debug] Error review overdue "
                        f"({days_since} days since last review on {date_str}). "
                        f"Run: error review"
                    )
                    try:
                        COOLDOWN_FILE.write_text(str(datetime.now()))
                    except Exception:
                        pass
            except ValueError:
                pass
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
