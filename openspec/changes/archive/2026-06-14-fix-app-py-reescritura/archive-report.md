# Archive Report: fix-app-py-reescritura

**Archived**: 2026-06-14
**Previous location**: `openspec/changes/fix-app-py-reescritura/`
**Archive location**: `openspec/changes/archive/2026-06-14-fix-app-py-reescritura/`

## Summary

Corrective refactor of `app.py` — fixed three blocking bugs (syntax error in test image button indentation, duplicated filter/results section, disordered crop overlay position) with no functional changes. Full rewrite from 613 lines to 431 lines.

## What Was Done

| Category | Details |
|----------|---------|
| **Bugs fixed** | 1. Indentation error in 8 test image `st.button` blocks (stray `st.rerun()` at parent indent) 2. Duplicated filter selection + results block (lines 259–418 & 442–603) 3. Crop overlay preview rendering after first results block instead of before |
| **Code structure** | Rewrote from 621-line broken layout to ~431-line clean layout in 10 defined sections |
| **Layout applied** | Section 1: `st.set_page_config` → Section 2: Session state init → Section 3: Sidebar (contiguous) → Section 4: Title + branding → Section 5: Image decode → Section 6: Cold start guard → Section 7: Image info → Section 8: Crop + overlay → Section 9: Filter results → Section 10: Sidebar branding |
| **`use_container_width` removed** | Replaced all occurrences with `width='stretch'` |
| **Button scoping fixed** | All `st.button()` side effects (session_state writes + `st.rerun()`) now inside the `if` block |

## Files Modified

| File | Change | Lines Before | Lines After |
|------|--------|-------------|-------------|
| `app.py` | Full rewrite | 613 | 431 |

## Files Added

| File | Purpose |
|------|---------|
| `tests/test_app_structure.py` | 22 structural tests verifying section order, no duplication, button scoping, cold start safety |

## Test Results

| Suite | Count | Result |
|-------|-------|--------|
| All tests (unit + structural) | 67 | ✅ All pass |
| Spec scenarios compliant | 37/37 | ✅ All compliant |
| Test images | 8 | ✅ All 8 buttons work (4 original + 4 real-world) |
| Filter types | 4 (media, mediana, laplaciano, sobel) | ✅ All produce correct results |
| `use_container_width` | — | ✅ Zero occurrences in `app.py` |

## Spec Impact

No spec-level changes. The following existing specs remain valid as-is:
- `openspec/specs/app-structure.md`
- `openspec/specs/course-branding.md`
- `openspec/specs/crop-overlay.md`
- `openspec/specs/crop-size-config.md`
- `openspec/specs/test-images-real-world.md`

No delta specs were produced — the change was purely a structural refactor of `app.py` UI wiring.

## Archive Contents

| Artifact | Status |
|----------|--------|
| `proposal.md` | ✅ |
| `design.md` | ✅ |
| `tasks.md` | ✅ (14/14 tasks complete) |
| `archive-report.md` | ✅ (this file) |

## Engram Traceability

| Field | Value |
|-------|-------|
| Observation ID | `obs-ccb975191ae81fcd` (ID: 108) |
| Topic Key | `sdd/fix-app-py-reescritura/archive-report` |
| Type | architecture |

## Remaining Risks / Caveats

- **None expected.** All 67 tests pass, all 37 spec scenarios compliant, core `filtrado/` package untouched.
- The change is a single-file rewrite with immediate rollback via `git checkout -- app.py`.
