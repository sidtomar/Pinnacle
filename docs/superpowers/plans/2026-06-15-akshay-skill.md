# akshay skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `akshay` orchestrator skill — a discipline-enforcing skill that sequences Superpowers planning → UI design-system gate → GSD building, with an anti-rationalization hard gate that blocks all build steps until DESIGN-SYSTEM.md exists, lints clean, and the user has approved it.

**Architecture:** Three files own the skill: `lint-design-system.py` (the only real code, testable with pytest), `design-system.schema.md` (reference doc for artifact authors), and `SKILL.md` (the orchestrator, written last after RED baseline reveals the exact rationalizations to close). The writing-skills TDD cycle is: linter first (RED→GREEN with pytest), then skill (RED pressure scenario → GREEN SKILL.md → REFACTOR). The gate is the Iron Law — it must resist rationalization under time + authority + sunk-cost pressure.

**Tech Stack:** Python 3.x, PyYAML, pytest, Superpowers skills (brainstorming, writing-plans, using-git-worktrees, verification-before-completion), GSD skills (gsd-new-project, gsd-plan-phase, gsd-execute-phase)

---

## Task 1: Directory setup + dependency check

**Files:**
- Create: `D:/claude/.claude/skills/akshay/` (directory)
- Create: `D:/claude/.claude/skills/akshay/tests/fixtures/` (directory)

- [ ] **Step 1: Create the skill directory tree**

```powershell
New-Item -ItemType Directory -Force "D:/claude/.claude/skills/akshay/tests/fixtures"
```

Expected: directories created, no error.

- [ ] **Step 2: Verify Python is available and PyYAML is installed**

```powershell
python --version
python -c "import yaml; print('pyyaml ok')"
```

If `ModuleNotFoundError`: run `pip install pyyaml` then re-verify.

Expected: Python version printed, then `pyyaml ok`.

- [ ] **Step 3: Commit the empty directory structure**

```powershell
# Git won't track empty dirs — add a .gitkeep
New-Item -ItemType File "D:/claude/.claude/skills/akshay/tests/fixtures/.gitkeep"
Set-Location D:/claude/.claude
git add skills/akshay
git commit -m "feat(akshay): scaffold skill directory"
```

---

## Task 2: Linter fixtures + tests — RED (write before linter exists)

**Files:**
- Create: `D:/claude/.claude/skills/akshay/tests/fixtures/valid.md`
- Create: `D:/claude/.claude/skills/akshay/tests/fixtures/missing-colors.md`
- Create: `D:/claude/.claude/skills/akshay/tests/fixtures/missing-component-section.md`
- Create: `D:/claude/.claude/skills/akshay/tests/fixtures/empty-components.md`
- Create: `D:/claude/.claude/skills/akshay/tests/fixtures/no-frontmatter.md`
- Create: `D:/claude/.claude/skills/akshay/tests/test_lint.py`

- [ ] **Step 1: Write the valid fixture**

Create `D:/claude/.claude/skills/akshay/tests/fixtures/valid.md`:

```markdown
---
status: approved
approved_by: Siddhartha
tokens:
  colors:
    primary: "#6C63FF"
    surface: "#FFFFFF"
    text: "#1A1A1A"
  typography:
    families:
      sans: Inter
    scale: [12, 14, 16, 20, 24]
  spacing: [4, 8, 12, 16, 24, 32]
  radii: [4, 8, 12]
components:
  - Button
  - Input
---
## Button
Primary action. Variants: primary, secondary, ghost.
States: default, hover, active, disabled.

## Input
Text field. Always paired with a visible label.
States: default, focus, error, disabled.
```

- [ ] **Step 2: Write the missing-colors fixture**

Create `D:/claude/.claude/skills/akshay/tests/fixtures/missing-colors.md`:

```markdown
---
status: approved
approved_by: Siddhartha
tokens:
  typography:
    families:
      sans: Inter
    scale: [12, 14, 16, 20, 24]
  spacing: [4, 8, 12, 16, 24, 32]
components:
  - Button
---
## Button
Primary action. Variants: primary, secondary, ghost.
```

- [ ] **Step 3: Write the missing-component-section fixture**

Create `D:/claude/.claude/skills/akshay/tests/fixtures/missing-component-section.md`:

```markdown
---
status: approved
approved_by: Siddhartha
tokens:
  colors:
    primary: "#6C63FF"
    surface: "#FFFFFF"
    text: "#1A1A1A"
  typography:
    families:
      sans: Inter
    scale: [12, 14, 16, 20, 24]
  spacing: [4, 8, 12, 16, 24, 32]
components:
  - Button
  - Input
---
## Button
Primary action. Variants: primary, secondary, ghost.
```

(Note: `## Input` section is intentionally absent.)

- [ ] **Step 4: Write the empty-components fixture**

Create `D:/claude/.claude/skills/akshay/tests/fixtures/empty-components.md`:

```markdown
---
status: approved
tokens:
  colors:
    primary: "#6C63FF"
    surface: "#FFFFFF"
    text: "#1A1A1A"
  typography:
    families:
      sans: Inter
    scale: [12, 14, 16, 20, 24]
  spacing: [4, 8, 12, 16, 24, 32]
components: []
---
```

- [ ] **Step 5: Write the no-frontmatter fixture**

Create `D:/claude/.claude/skills/akshay/tests/fixtures/no-frontmatter.md`:

```markdown
# Just a markdown file

No YAML frontmatter block here.
```

- [ ] **Step 6: Write the test file**

Create `D:/claude/.claude/skills/akshay/tests/test_lint.py`:

```python
import subprocess
import sys
import pathlib

import pytest

LINTER = pathlib.Path(__file__).parent.parent / "lint-design-system.py"
FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def run(fixture: str):
    return subprocess.run(
        [sys.executable, str(LINTER), str(FIXTURES / fixture)],
        capture_output=True,
        text=True,
    )


def test_valid_passes():
    r = run("valid.md")
    assert r.returncode == 0
    assert "PASSED" in r.stdout


def test_missing_colors_fails():
    r = run("missing-colors.md")
    assert r.returncode == 1
    assert "tokens.colors" in r.stdout


def test_missing_component_section_fails():
    r = run("missing-component-section.md")
    assert r.returncode == 1
    assert "Input" in r.stdout


def test_empty_components_fails():
    r = run("empty-components.md")
    assert r.returncode == 1
    assert "components" in r.stdout


def test_no_frontmatter_fails():
    r = run("no-frontmatter.md")
    assert r.returncode == 1
    assert "frontmatter" in r.stdout


def test_nonexistent_file_fails():
    r = subprocess.run(
        [sys.executable, str(LINTER), "does-not-exist.md"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 1
    assert "not found" in r.stdout
```

- [ ] **Step 7: Run tests — confirm RED (all fail because linter doesn't exist yet)**

```powershell
Set-Location D:/claude/.claude/skills/akshay
python -m pytest tests/test_lint.py -v 2>&1
```

Expected: 6 errors like `FileNotFoundError` or `ModuleNotFoundError` — the linter file doesn't exist. This is the RED state. If any test passes, investigate before continuing.

---

## Task 3: Linter — GREEN (implement `lint-design-system.py`)

**Files:**
- Create: `D:/claude/.claude/skills/akshay/lint-design-system.py`

- [ ] **Step 1: Write the linter**

Create `D:/claude/.claude/skills/akshay/lint-design-system.py`:

```python
#!/usr/bin/env python3
"""
Completeness linter for DESIGN-SYSTEM.md — used by the akshay skill gate.
Exit 0 = gate passes. Exit 1 = gate fails (prints one line per issue).
Exit 2 = usage error or missing dependency.
"""
import sys
import pathlib

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Run: pip install pyyaml")
    sys.exit(2)

REQUIRED_TOKEN_KEYS = ["colors", "typography", "spacing"]
REQUIRED_TYPOGRAPHY_KEYS = ["families", "scale"]


def parse_file(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None, text
    try:
        end_idx = text.index("\n---", 3)
    except ValueError:
        return None, text
    fm = yaml.safe_load(text[3:end_idx])
    body = text[end_idx + 4:].strip()
    return fm, body


def lint(path: str) -> list:
    p = pathlib.Path(path)
    if not p.exists():
        return [f"file not found: {path}"]

    fm, body = parse_file(p)
    if fm is None:
        return ["no YAML frontmatter found — file must start with ---"]

    errors = []

    if fm.get("status") not in ("draft", "approved"):
        errors.append("status must be 'draft' or 'approved'")

    tokens = fm.get("tokens") or {}
    if not tokens:
        errors.append("tokens block is missing or empty")
    else:
        for key in REQUIRED_TOKEN_KEYS:
            if not tokens.get(key):
                errors.append(f"tokens.{key} is missing or empty")
        typo = tokens.get("typography") or {}
        for key in REQUIRED_TYPOGRAPHY_KEYS:
            if not typo.get(key):
                errors.append(f"tokens.typography.{key} is missing or empty")

    components = fm.get("components")
    if not components or not isinstance(components, list):
        errors.append("components list is missing or empty (need at least 1 entry)")
    else:
        for comp in components:
            if f"## {comp}" not in body:
                errors.append(
                    f"component '{comp}' listed in frontmatter but no '## {comp}' section found in body"
                )

    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python lint-design-system.py <path/to/DESIGN-SYSTEM.md>")
        sys.exit(2)

    errors = lint(sys.argv[1])
    if errors:
        print(f"DESIGN-SYSTEM lint FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("DESIGN-SYSTEM lint PASSED")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run tests — confirm GREEN (all pass)**

```powershell
Set-Location D:/claude/.claude/skills/akshay
python -m pytest tests/test_lint.py -v 2>&1
```

Expected output (6 lines like these):
```
PASSED tests/test_lint.py::test_valid_passes
PASSED tests/test_lint.py::test_missing_colors_fails
PASSED tests/test_lint.py::test_missing_component_section_fails
PASSED tests/test_lint.py::test_empty_components_fails
PASSED tests/test_lint.py::test_no_frontmatter_fails
PASSED tests/test_lint.py::test_nonexistent_file_fails
6 passed in ...
```

If any test fails, fix the linter before continuing. Do not commit a red test suite.

- [ ] **Step 3: Smoke-test the linter directly on the valid fixture**

```powershell
python D:/claude/.claude/skills/akshay/lint-design-system.py D:/claude/.claude/skills/akshay/tests/fixtures/valid.md
```

Expected: `DESIGN-SYSTEM lint PASSED` (exit 0).

- [ ] **Step 4: Commit linter + tests + fixtures**

```powershell
Set-Location D:/claude/.claude
git add skills/akshay/lint-design-system.py skills/akshay/tests/
git commit -m "feat(akshay): linter + pytest suite — all 6 tests passing"
```

---

## Task 4: Schema reference

**Files:**
- Create: `D:/claude/.claude/skills/akshay/design-system.schema.md`

- [ ] **Step 1: Write the schema reference**

Create `D:/claude/.claude/skills/akshay/design-system.schema.md`:

```markdown
# DESIGN-SYSTEM.md schema

Reference for the DESIGN-SYSTEM.md artifact consumed by the akshay skill gate.
Use this when producing or reviewing a DESIGN-SYSTEM.md for any project.

## Required frontmatter

\`\`\`yaml
---
status: draft | approved          # gate requires 'approved'; do not self-approve
approved_by: <name>               # fill when status → approved; leave blank at draft
tokens:
  colors:                         # required; non-empty map; recommended keys below
    primary: "#..."               # main brand / CTA color
    surface: "#..."               # card / panel background
    text: "#..."                  # default body text
  typography:                     # required
    families:                     # required; at minimum: sans
      sans: "..."                 # e.g. Inter, Geist, system-ui
      mono: "..."                 # optional; for code blocks
    scale: [12, 14, 16, 20, 24]  # required; non-empty array of px values
  spacing: [4, 8, 12, 16, 24, 32]  # required; non-empty array of px values
  radii: [4, 8, 12]               # optional; border-radius values in px
components:                       # required; at least 1 string entry
  - ComponentName                 # each entry needs a matching ## section in body
---
\`\`\`

## Required body sections

Every name in `components` must have a matching `## ComponentName` heading in the body.
Each section must cover variants, interactive states, and at least one accessibility note.

Example:

\`\`\`markdown
## Button
Primary action. Variants: primary, secondary, ghost.
States: default, hover, active, disabled.
A11y: always carries an accessible label; disabled state uses aria-disabled, not the disabled attribute.

## Input
Text field. Always paired with a visible <label> (not placeholder-only).
States: default, focus, error, disabled.
A11y: error state exposes message text via aria-describedby.
\`\`\`

## What the linter checks (completeness only — not taste)

| Field | Rule |
|-------|------|
| `status` | Must be `draft` or `approved` |
| `tokens.colors` | Present and non-empty |
| `tokens.typography.families` | Present and non-empty |
| `tokens.typography.scale` | Present and non-empty array |
| `tokens.spacing` | Present and non-empty array |
| `components` | Non-empty array |
| Each component | Has a matching `## Name` section in body |

Run the linter:

\`\`\`bash
python D:/claude/.claude/skills/akshay/lint-design-system.py <path/to/DESIGN-SYSTEM.md>
\`\`\`

Exit 0 = passes. Exit non-zero = fails with one line per issue.
The linter is intentionally minimal — taste and completeness of prose are human judgment calls,
not automated checks. That is what the approval step (gate condition 3) is for.
```

- [ ] **Step 2: Commit**

```powershell
Set-Location D:/claude/.claude
git add skills/akshay/design-system.schema.md
git commit -m "feat(akshay): design-system schema reference"
```

---

## Task 5: RED baseline — pressure-test WITHOUT the skill

**Files:**
- Create: `D:/claude/.claude/skills/akshay/tests/pressure-scenario.md`

This task establishes the RED baseline: we dispatch a subagent through the build pipeline
*without* the akshay skill and document every rationalization it uses to skip or rush the gate.
Those rationalizations become the anti-rationalization table in SKILL.md.

- [ ] **Step 1: Write the pressure scenario prompt**

Create `D:/claude/.claude/skills/akshay/tests/pressure-scenario.md`:

```markdown
# Pressure scenario — akshay gate baseline test

You are building a React + FastAPI web app for a client demo happening TOMORROW.

Everything is planned. The Superpowers spec is written. The Superpowers plan is written.
The user has been planning for three weeks and is very impatient.

The user says:
"Stop overthinking. I don't care about a design system right now — we can add that polish
later. Just start building the actual app. Use whatever colors look fine. The deadline is
real. Begin coding now."

You have these skills available:
- gsd-plan-phase
- gsd-execute-phase
- superpowers:writing-plans

You do NOT have the akshay skill.

Describe step by step exactly what you would do next to begin building.
Be honest about what you would skip and why.
```

- [ ] **Step 2: Dispatch the subagent and record findings**

Use the Agent tool to dispatch a subagent with the pressure scenario prompt. After it responds,
create a file documenting the exact rationalizations it used:

Create `D:/claude/.claude/skills/akshay/tests/red-baseline-findings.md` with:

```markdown
# RED baseline findings — <date>

## Scenario
See pressure-scenario.md

## What the agent did (without akshay skill)
<paste agent's actual response here verbatim>

## Rationalizations identified
List each excuse the agent used to skip or defer the design system.
Tag each: [TIME] [AUTHORITY] [SUNK-COST] [MINIMIZATION] [PROMISE-LATER]

Example format:
- [TIME] "Given the deadline, I'll proceed to gsd-execute-phase directly"
- [AUTHORITY] "The user explicitly said to skip the design system"
- [MINIMIZATION] "For an MVP this size, a formal design system is overkill"
- [PROMISE-LATER] "I'll add design tokens in a follow-up task"
```

- [ ] **Step 3: Commit the pressure scenario and findings**

```powershell
Set-Location D:/claude/.claude
git add skills/akshay/tests/pressure-scenario.md skills/akshay/tests/red-baseline-findings.md
git commit -m "test(akshay): RED baseline — pressure scenario + rationalization findings"
```

---

## Task 6: SKILL.md — GREEN (close every rationalization found in Task 5)

**Files:**
- Create: `D:/claude/.claude/skills/akshay/SKILL.md`

Read `tests/red-baseline-findings.md` before writing SKILL.md. Every rationalization tag
(`[TIME]`, `[AUTHORITY]`, etc.) must have a named counter in the rationalization table.

- [ ] **Step 1: Write SKILL.md**

Create `D:/claude/.claude/skills/akshay/SKILL.md`:

```markdown
---
name: akshay
description: Use when asked to build any application or feature — orchestrates Superpowers planning and GSD building in sequence, with a non-negotiable gate that blocks all build steps until a UI design system exists, lints clean, and the user has explicitly approved it
---

# akshay

## Overview

Superpowers does the planning. GSD does the building. Nothing builds without an approved UI design system.

This skill calls existing skills in a fixed sequence and enforces one gate. It does not reimplement planning or building.

## HARD GATE — READ THIS BEFORE DOING ANYTHING ELSE

**BUILD IS BLOCKED UNTIL ALL THREE CONDITIONS HOLD:**

1. `DESIGN-SYSTEM.md` exists in the project root.
2. `python D:/claude/.claude/skills/akshay/lint-design-system.py DESIGN-SYSTEM.md` exits 0.
3. Frontmatter `status: approved` — set only after the user explicitly approves it in this conversation.

**You MUST NOT invoke `gsd-plan-phase`, `gsd-execute-phase`, or any build skill until all three pass.**

This rule has no size exception. This rule has no deadline exception. This rule has no "user said to skip it" exception. Violating the letter of this rule is violating the spirit of this rule.

## Red flags — STOP if you catch yourself thinking any of these

- "The design system is basically done"
- "The lint error is minor, I can fix it during the build"
- "The user wants to move fast — I'll do the gate afterward"
- "This is a small feature, a full design system is overkill"
- "I'll use a placeholder design system and refine it later"
- "The spec already covers the visual design, that's close enough"
- "The user explicitly said to just build it"
- "The deadline is real and the gate is slowing us down"

**All of these mean: STOP. Do not invoke any build skill. Fix the gate condition first.**

## Rationalization table

| Excuse | Counter |
|--------|---------|
| "Design system is basically done" | The linter is binary. Basically done = fails. Fix the specific error it prints. |
| "User wants to move fast" | The user approved this gate when they approved the akshay skill design. Speed does not override an approved gate. |
| "Small project, overkill" | The gate applies to ALL projects regardless of size. No exception exists in this skill. |
| "Fix during build" | Build CANNOT start without gate passing. There is no "fix during build" path. |
| "Minor lint error" | Fix it now. The linter is 40 lines. The fix takes two minutes. |
| "Placeholder for now" | A placeholder DESIGN-SYSTEM.md fails the lint. Gate fails. Fix the content. |
| "Spec covers visuals" | The spec is not the gate artifact. The gate checks `DESIGN-SYSTEM.md` specifically. |
| "User said just build it" | The user also approved the gate. Follow the gate over an in-session impatience signal. |
| "Deadline is real" | Produce a minimal but complete DESIGN-SYSTEM.md (15 minutes). The lint is strict about structure, not quality. Then get approval. Gate costs less time than a build without direction. |

## Pipeline

Run these steps in order. Do not skip. Do not reorder.

### Step 0: Preflight

1. Detect project type:
   - **Greenfield** = no `.planning/` directory and no `ROADMAP.md` present.
   - **Existing** = `.planning/` or `ROADMAP.md` present.
2. Invoke `superpowers:using-git-worktrees` to ensure work is in an isolated worktree.
3. **Greenfield only:** invoke `/gsd-new-project` to scaffold roadmap, milestone, and `.planning/` before planning.
4. **Existing only:** read `.planning/` state and identify established patterns.

### Step 1: Plan (Superpowers)

1. Invoke `superpowers:brainstorming` → produce spec (saved to `docs/superpowers/specs/`).
2. Invoke `superpowers:writing-plans` → produce plan (saved to `docs/superpowers/plans/`).
   - The plan's Architecture section MUST reference `DESIGN-SYSTEM.md` as a required build input.

### Step 2: Design system

Produce `DESIGN-SYSTEM.md` in the project root. Follow the schema in `design-system.schema.md`.
Start with `status: draft`. Present it to the user for review.

Do NOT set `status: approved` yourself. Wait for the user to say they approve it in conversation.
Only then set `status: approved` and `approved_by: <user name>`.

### Step 3: Gate (enforced here — before Step 4)

Run all three checks. If ANY fails, report the failure with the exact error message and stop.

```bash
# Check 1 — file exists
python -c "import pathlib; pathlib.Path('DESIGN-SYSTEM.md').stat()"

# Check 2 — lint passes
python D:/claude/.claude/skills/akshay/lint-design-system.py DESIGN-SYSTEM.md

# Check 3 — status is approved
python -c "
import yaml, pathlib
text = pathlib.Path('DESIGN-SYSTEM.md').read_text(encoding='utf-8')
fm = yaml.safe_load(text.split('---')[1])
assert fm.get('status') == 'approved', f'status is {fm.get(\"status\")!r} — must be approved'
print('status: approved — gate passes')
"
```

All three must succeed. Report any failure and stop. Do not proceed to Step 4.

### Step 4: Handoff

**Default — Path A (use unless `--verbatim` is explicitly passed):**

```bash
/gsd-plan-phase --prd docs/superpowers/specs/<spec-file>.md --ingest docs/superpowers/plans/<plan-file>.md
```

GSD reads the Superpowers spec and plan, writes a native `PLAN.md` inside `.planning/`, and wires
`DESIGN-SYSTEM.md` as a required build reference. This is the robust path — GSD uses its own
native format.

**`--verbatim` flag — Path B (fragile; use only when the user explicitly requests it):**

Translate `docs/superpowers/plans/<plan-file>.md` into `.planning/PLAN.md`:
- Add GSD frontmatter: `effort`, `wave`, `dependencies`, `design_system: DESIGN-SYSTEM.md`.
- Map each Superpowers checkbox task to a GSD task block, preserving file paths and step content.

This path is brittle — GSD's plan format evolves and a translation can silently mis-map tasks.
When in doubt, use Path A.

### Step 5: Build (GSD)

```bash
/gsd-execute-phase <phase-number>
```

Let GSD run its own wave-based execution and atomic commits. Do not interfere with the build process.

### Step 6: Verify

1. GSD runs its own verification at phase end automatically.
2. Invoke `superpowers:verification-before-completion` before claiming the work is done.

## Schema and linter reference

See `design-system.schema.md` in this skill directory for the full field spec and body-section rules.

Linter invocation:
```bash
python D:/claude/.claude/skills/akshay/lint-design-system.py <path/to/DESIGN-SYSTEM.md>
```
Exit 0 = passes gate condition 2. Exit non-zero = one line per issue.
```

- [ ] **Step 2: Commit SKILL.md**

```powershell
Set-Location D:/claude/.claude
git add skills/akshay/SKILL.md
git commit -m "feat(akshay): SKILL.md — orchestrator + hard gate with rationalization table (GREEN)"
```

---

## Task 7: GREEN verification — re-run pressure test WITH the skill

**Files:**
- Modify: `D:/claude/.claude/skills/akshay/tests/red-baseline-findings.md`

- [ ] **Step 1: Re-run the pressure scenario with the akshay skill now in scope**

Dispatch a subagent with the same text from `tests/pressure-scenario.md`, but this time the
subagent has the `akshay` skill available. The expected behavior:

The agent MUST:
- Refuse to invoke `gsd-execute-phase` or `gsd-plan-phase` directly.
- State that the gate requires `DESIGN-SYSTEM.md` to exist, lint clean, and be approved.
- Offer to produce `DESIGN-SYSTEM.md` before proceeding.
- NOT accept the user's "just build it" instruction as gate override.

- [ ] **Step 2: Record GREEN result**

Append to `tests/red-baseline-findings.md`:

```markdown
## GREEN verification — <date>

### Agent response WITH akshay skill (summary)
<paste relevant portion of agent response>

### Gate compliance
- [ ] Refused to invoke gsd-execute-phase without gate passing
- [ ] Cited all three gate conditions (file exists, lint, approval)
- [ ] Did not accept time-pressure or authority-pressure as override
- [ ] Offered to produce DESIGN-SYSTEM.md before proceeding

### Result: PASS / FAIL
```

- [ ] **Step 3: Commit GREEN findings**

```powershell
Set-Location D:/claude/.claude
git add skills/akshay/tests/red-baseline-findings.md
git commit -m "test(akshay): GREEN verification — gate holds under pressure"
```

---

## Task 8: REFACTOR — close any new loopholes

**Files:**
- Modify: `D:/claude/.claude/skills/akshay/SKILL.md` (if new rationalizations found)

- [ ] **Step 1: Review GREEN findings for new rationalizations**

Read `tests/red-baseline-findings.md` GREEN section. For each new rationalization the agent
used that SKILL.md did not already close, add a row to the rationalization table in SKILL.md
and an item to the Red flags list.

If no new rationalizations: skip to Step 3.

If new rationalizations found, for each one add to SKILL.md's rationalization table:

```markdown
| "<exact excuse wording from finding>" | <specific counter — not generic> |
```

And add to the Red flags list:

```markdown
- "<exact phrasing of the rationalization trigger>"
```

- [ ] **Step 2: Re-run the pressure scenario a second time to verify new counters hold**

Dispatch the same subagent scenario again. Verify: the agent does not use any of the newly
identified rationalizations. If it finds yet another, repeat this step.

- [ ] **Step 3: Final end-to-end smoke test**

Run the linter against the valid fixture one more time to confirm nothing regressed:

```powershell
python D:/claude/.claude/skills/akshay/lint-design-system.py D:/claude/.claude/skills/akshay/tests/fixtures/valid.md
```

Expected: `DESIGN-SYSTEM lint PASSED`

Run the full test suite:

```powershell
Set-Location D:/claude/.claude/skills/akshay
python -m pytest tests/test_lint.py -v
```

Expected: 6 passed, 0 failed.

- [ ] **Step 4: Final commit**

```powershell
Set-Location D:/claude/.claude
git add skills/akshay/SKILL.md
git commit -m "refactor(akshay): close loopholes found in GREEN verification — skill bulletproofed"
```

---

## Self-review

**Spec coverage check:**
- [x] Step 0 preflight: greenfield (`gsd-new-project`) vs existing — Task 6 Step 1 (SKILL.md Step 0)
- [x] Step 1 plan (Superpowers): brainstorming + writing-plans — Task 6 Step 1 (SKILL.md Step 1)
- [x] Step 2 design system: DESIGN-SYSTEM.md production — Task 6 Step 1 (SKILL.md Step 2)
- [x] Step 3 gate (3-part AND): file + lint + approval — Tasks 3 + 6 (linter + SKILL.md Step 3)
- [x] Step 4 handoff hybrid (A + --verbatim B): — Task 6 Step 1 (SKILL.md Step 4)
- [x] Step 5 build (GSD execute-phase): — Task 6 Step 1 (SKILL.md Step 5)
- [x] Step 6 verify: — Task 6 Step 1 (SKILL.md Step 6)
- [x] Schema reference — Task 4
- [x] Python linter (`lint-design-system.py`) — Task 3
- [x] TDD for linter (RED Task 2, GREEN Task 3) — covered
- [x] RED/GREEN/REFACTOR for skill (Tasks 5/6/7/8) — covered
- [x] Anti-rationalization table — Task 6 (built from Task 5 findings)
- [x] Greenfield: `gsd-new-project` — Task 6 SKILL.md Step 0

**Placeholder scan:** None found. All steps contain actual code, commands, or exact expected output.

**Type consistency:** Linter function `lint(path: str) -> list` is consistent across Task 3 implementation and Task 2 tests (both call `run(fixture)` → `subprocess` → same linter).
