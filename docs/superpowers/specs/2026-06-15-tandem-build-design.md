# tandem-build — Superpowers-plans / GSD-builds skill with a design-system gate

> **Status:** Approved design (2026-06-15). Ready for implementation planning.
> **Author:** Siddhartha (with Claude)

## Goal

A single orchestrator skill that makes **Superpowers do the planning** and **GSD do the
building**, with a **hard gate**: no build may start until an approved UI design system is
incorporated into the plan. The skill does not reimplement planning or building — it calls
the real Superpowers and GSD skills in sequence and enforces one gate between them.

## Background & constraints

Two mature systems already exist on this machine:

- **Superpowers planning** = `superpowers:brainstorming` → `superpowers:writing-plans`, which
  produces a checkbox-task plan under `docs/superpowers/plans/…md` and normally hands off to
  its own executors.
- **GSD building** = `gsd-execute-phase`, which consumes **GSD-format `PLAN.md` files inside a
  `.planning/` phase directory** with GSD-specific frontmatter (waves, gap-closure, ROADMAP
  phases). It does not natively read Superpowers' plan format.
- `gsd-plan-phase` already accepts external input via `--prd <file>` and `--ingest <path>`,
  which is the door we use to bridge the two systems robustly.
- Authoring the skill itself is governed by `superpowers:writing-skills` (TDD for skills;
  Iron Law: no skill without a failing test first).

### Decisions locked during brainstorming

| Decision | Choice |
|----------|--------|
| Meaning of "design system" | Visual/UI design system (colors, typography, spacing, components, layout) |
| Handoff model | **Hybrid** — default A (ingest via GSD's `--prd`/`--ingest` door); `--verbatim` flag forces B (translate plan to `.planning/PLAN.md`) |
| Design-system artifact | **New dedicated format** owned by this skill |
| Gate strictness | **Strictest** — artifact must exist AND pass an automated lint AND be user-approved |
| Project scope | **Both** greenfield and existing codebases |

## Skill identity

- **Name (placeholder):** `tandem-build`
- **Location:** `D:\claude\.claude\skills\tandem-build\` (alongside the `gsd-*` skills; personal
  skills directory for Claude Code).
- **Type:** Discipline-enforcing orchestrator skill (the gate is a rule that must resist
  rationalization).
- **Owned files:**
  - `SKILL.md` — the orchestration workflow
  - `design-system.schema.md` — schema + field reference for the design-system artifact
  - `lint-design-system.mjs` — the automated completeness linter the gate runs

## Pipeline

```
0. Preflight   detect greenfield vs existing; ensure isolated worktree
               (superpowers:using-git-worktrees); init GSD scaffold if greenfield
1. PLAN (SP)   superpowers:brainstorming -> spec
               superpowers:writing-plans -> plan
2. DESIGN SYS  produce DESIGN-SYSTEM.md during planning; user reviews
3. GATE        HARD STOP unless: artifact exists + lint passes + status: approved
4. HANDOFF     default A: gsd-plan-phase --prd <spec> --ingest <plan> -> native PLAN.md
               flag --verbatim: path B translate plan -> .planning/PLAN.md
5. BUILD (GSD) gsd-execute-phase (waves, atomic commits)
6. VERIFY      GSD verification + superpowers:verification-before-completion
```

Steps 1–2 are "Superpowers does the planning." Steps 4–5 are "GSD does the building." Step 3
is the non-negotiable gate.

### Step detail

**0. Preflight.** Determine whether the target is greenfield (new app) or an existing codebase.
Ensure work happens in an isolated worktree via `superpowers:using-git-worktrees`. For
greenfield, initialize the minimum GSD scaffold needed for `gsd-plan-phase`/`gsd-execute-phase`
(roadmap + phase). For existing codebases, detect the established patterns and the existing
`.planning/` state if present.

**1. Plan (Superpowers).** Invoke `superpowers:brainstorming` to produce the spec, then
`superpowers:writing-plans` to produce the implementation plan. This is the planning the user
wants to live in Superpowers.

**2. Design system.** During planning, produce the `DESIGN-SYSTEM.md` artifact (see below) and
present it to the user for review.

**3. Gate (hard).** A three-part AND. The skill MUST NOT invoke any build skill until all three
hold:
1. `DESIGN-SYSTEM.md` exists, and
2. `lint-design-system.mjs` exits 0, and
3. frontmatter `status: approved` (set only after explicit user sign-off).
On any failure, the skill reports exactly what is missing and stops. The SKILL.md carries
explicit anti-rationalization language so a future agent cannot talk itself past the gate.

**4. Handoff.**
- **Default (A):** hand spec, plan, and `DESIGN-SYSTEM.md` to
  `gsd-plan-phase --prd <spec> --ingest <plan>`; GSD writes its own native `PLAN.md` that
  references the design system as a build input.
- **`--verbatim` (B):** translate the Superpowers plan directly into `.planning/PLAN.md` and run
  `gsd-execute-phase` task-for-task. Documented as the brittle path.
Either way, the design system is wired into the build plan so the builder consumes it — not just
gated on.

**5. Build (GSD).** `gsd-execute-phase` runs the native plan with its wave-based execution and
atomic commits.

**6. Verify.** GSD's verification plus `superpowers:verification-before-completion` before any
completion claim.

## Design-system artifact

File: `DESIGN-SYSTEM.md`. YAML frontmatter holds the structured, lintable parts; prose and
component specs follow.

```yaml
---
status: draft            # draft | approved  — gate checks this
approved_by:             # set when status flips to approved
tokens:
  colors:                # required, non-empty map
    primary: "#..."
    surface: "#..."
    text: "#..."
  typography:            # required
    families: { sans: "...", mono: "..." }
    scale: [12, 14, 16, 20, 24]
  spacing: [4, 8, 12, 16, 24, 32]   # required, non-empty
  radii: [4, 8, 12]
components:              # required, >= 1 entry
  - Button
  - Input
  - Card
---
## Component specs
<prose per component: variants, states, accessibility notes>
```

### Linter contract (`lint-design-system.mjs`)

Deterministic, no network. Exit 0 only if ALL hold:
- File parses as YAML-frontmatter + markdown.
- `tokens.colors` is a non-empty map.
- `tokens.typography.families` and `tokens.typography.scale` are present and non-empty.
- `tokens.spacing` is a non-empty array.
- `components` is an array with at least one entry.
- Each listed component has a matching `## ` section in the prose body.

On failure: exit non-zero and print one line per missing/empty field. The gate's part 2 is
"linter exits 0."

> The linter checks **completeness**, not taste. Approval (part 3) is the human judgment step.

## How the skill gets built (implementation methodology)

Governed by `superpowers:writing-skills` — TDD for skills. After the spec is approved:

1. **Spec** — this document (written, self-reviewed, user-reviewed).
2. **Plan** — `superpowers:writing-plans` produces a bite-sized implementation plan.
3. **RED** — baseline pressure-test: run a subagent through the pipeline WITHOUT the skill and
   watch it skip or rush the design system under time pressure; record exact rationalizations.
4. **GREEN** — write `SKILL.md` + `design-system.schema.md` + `lint-design-system.mjs` that close
   those specific rationalizations; re-run the scenario and confirm the gate holds.
5. **REFACTOR** — find new loopholes, add explicit counters, build the rationalization table and
   red-flags list, re-test until bulletproof.
6. **Verify & integrate** — run the linter on a real sample, dry-run the full pipeline, commit.

## Out of scope (YAGNI)

- No new planning or building engine — only orchestration of existing skills.
- No design-system *generation* intelligence beyond producing the artifact; taste/quality is a
  human approval step, not an automated one.
- No multi-project / portfolio orchestration; one project per run.

## Open questions for spec review

- Final skill name (`tandem-build` is a placeholder).
- Linter language: Node `.mjs` (assumed) vs Python, depending on what the target environment
  reliably has.
- Whether greenfield scaffolding should reuse `gsd-new-project` or a lighter inline scaffold.
