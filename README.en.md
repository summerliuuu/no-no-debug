# no-no-debug

A self-evolution system for AI coding assistants

## What problem does this solve?

10 minutes writing code, 2 hours debugging.

This skill fills the gap in AI's cross-session error memory, delivering three things:

1. Dramatically less debug time
2. Higher code quality
3. A self-evolution feedback loop

The longer you use it, the fewer mistakes get repeated.

## How it works

### 1. Real-time Logging (automatic)
When the AI is corrected, code errors occur, deploys fail, or tests don't pass — it automatically appends to a local error_log.md with a timestamp. No need to say "write that down."

### 2. Three Gates (on every code change)
Before the change: what does this affect?
After the change: did you actually verify it?
Before deploying: did you test with a non-admin account?

Runs silently. No output when all gates pass.

### 3. Periodic Review (auto-triggers every 3 days)
Reads error_log.md, categorizes by dimension, updates error_tracker.md, outputs an evolution report.
Review frequency is configurable: 1 day / 3 days (default) / 7 days.

### 4. Rule Accumulation
New error type → automatically creates a prevention rule.
Repeated offense → counter increments, rule strengthens.
4 consecutive clean periods → marked as cured.

Rules persist across sessions — nothing gets lost.

### 5. Confirmation Gate
The following situations require user confirmation before proceeding:
- New feature development (not a bug fix)
- Changes involving databases, environments, or deployments
- Publishing to external platforms
- When the user raises a new idea or new direction mid-task

### 6. Auto Hooks
Automatically configures Claude Code hooks on install:
- Command errors → auto-logged to error_log.md
- After editing a file → auto-reminder to verify
- When user corrects the AI → correction content auto-logged

## Tracked Dimensions

| Dimension | What it tracks |
|-----------|---------------|
| Data Accuracy | Do displayed numbers/formulas match actual code |
| Environment Safety | Did config changes break login or the database |
| Foresight | Were permission, migration, or cache issues caught before deploy |
| User Perspective | Does the feature work end-to-end from the user's account |
| Verification | Was there a real end-to-end test after the fix |
| Memory Consistency | Did the AI read existing records instead of asking again |
| Tool Judgment | Did failing tools get swapped out promptly |
| Review Completeness | Were reviews and summaries thorough with nothing missed |
| Operational Precision | Did changes produce unintended side effects |
| Check Before Doing | With unfamiliar tools/versions, was documentation checked first |
| Conciseness | Was a 3-line solution turned into 300 lines |
| Regression Awareness | Did fixing one bug introduce a new one |
| Style Consistency | Does new code follow the project's existing style and architecture |
| Independent Judgment | When the user's premise is wrong, does the AI push back instead of blindly executing |
| Dumb things humans will do | Not yet committed, but inevitable |
| Dumb things AI will do | Same, but the AI edition |

## Real-world data

| Period | Errors | Notes |
|--------|--------|-------|
| Week 1 | 29 | Baseline, 10 dimensions identified |
| Week 2 | 6 | Rules starting to take effect |
| Week 3 | ~0 | Still running |

## Installation

```bash
claude skill add summerliuuu/no-no-debug
```

Zero configuration. Tracking files and hooks are initialized automatically on first run.

## Sample evolution report

```
Evolution Report R1 (4/8 – 4/11)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dimension              This period  Total   Status
──────────────────────────────────────────────────
Data Accuracy               4        4     Rule established
Environment Safety          4        4     Rule established
Foresight                   3        3     Rule established
User Perspective            3        3     Rule established
Verification                2        2     Rule established
Memory Consistency          3        3     Rule established
Tool Judgment               5        5     Alternative adopted
Review Completeness         3        3     Rule established
Operational Precision       1        1     Rule established
Check Before Doing          1        1     Rule established

Total: 29 | Cured: 0/14
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hot spots: Tool Judgment(5) > Data Accuracy(4) = Environment Safety(4)
Next review: 4/14
```

## Compatibility

- Claude Code CLI / Desktop / Web
- Any project, any language
- Pairs well with claude-mem (for session search)

## ⭐

Thank you for starring this project during installation.

📕 [Xiaohongshu @Summer的AI日常](https://xhslink.com/m/6fWf0EN8e6) — AI coding in practice

---

🇨🇳 [中文版](./README.md)

## License

MIT — [@summerliuuu](https://github.com/summerliuuu)
