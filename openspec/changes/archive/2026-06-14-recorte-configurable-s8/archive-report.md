# Archive Report: recorte-configurable-s8

## Change Summary

| Field | Value |
|-------|-------|
| **Change** | recorte-configurable-s8 |
| **Description** | Replace hardcoded `CROP_SIZE = 15` with a configurable `st.number_input` in S8 with reset button, stale result clearing, and dynamic `max_odd` bound |
| **Mode** | openspec |
| **Commit** | `a9119f2` |
| **Date archived** | 2026-06-14 |
| **Tasks** | 6/6 complete |
| **Tests** | 67 passed, 0 failed |
| **Artifact store** | `openspec/changes/archive/2026-06-14-recorte-configurable-s8/` |

## What Was Implemented

### Phase 1 (RED) — Test update
- Renamed `test_crop_size_constant_defined` → `test_crop_size_tracking_key_in_init` in `tests/test_app_structure.py`
- Updated assertion: checks `_crop_size_at_result` is in the S2 session state init loop instead of checking for `CROP_SIZE = 15`

### Phase 2 (GREEN) — Crop size config
- **S2 init**: Removed `CROP_SIZE = 15` constant. Added `_crop_size_at_result` to session state init loop (6 keys total)
- **Post-S6**: Added `min_dim = min(h, w)` and `max_odd = max(3, min_dim if min_dim % 2 == 1 else min_dim - 1)` after image dimensions are known
- **S8**: Complete rewrite — `st.number_input` (key="crop_size_input", step=2, min=3, max=max_odd, default=15) with reset button "📐 Predeterminado 15×15" in side-by-side columns, stale guard (clears result/raw/filter_applied on crop size change, NO `st.rerun()`), dynamic header showing `{current_crop}×{current_crop}`, reactive X/Y bounds in manual mode
- **S9 apply**: Added `st.session_state._crop_size_at_result = st.session_state.crop_size_input` after storing result

### Phase 3 (REFACTOR) — Verification
- Confirmed no stale `CROP_SIZE` references remain in `app.py`
- All 67 tests pass

## Files Changed

| File | Action | Lines |
|------|--------|-------|
| `app.py` | Modified | +53/-19 |
| `tests/test_app_structure.py` | Modified | +12/-8 |
| `openspec/specs/crop-size-config.md` | Rewritten | +147/-99 |
| `openspec/specs/app-structure.md` | Updated | +59/-19 |
| `openspec/changes/recorte-configurable-s8/proposal.md` | Created | 69 lines |
| `openspec/changes/recorte-configurable-s8/design.md` | Created | 199 lines |
| `openspec/changes/recorte-configurable-s8/tasks.md` | Created | 34 lines |

## Test Results

**67 passed, 0 failed** (14 warnings — matplotlib PyparsingDeprecationWarning only)

All existing core tests (validation, cropping, mean/median/laplacian/sobel) continue to pass. Structural test updated to reflect dynamic crop size approach.

### CRITICAL Fix Applied: Label Mismatch

**Issue**: Test `test_crop_size_constant_defined` asserted `CROP_SIZE = 15` existed as a module-level constant, but the implementation replaced the constant with a runtime widget-driven approach. The test name and assertion were misaligned with the actual architecture.

**Fix**: Renamed to `test_crop_size_tracking_key_in_init` and updated assertion to check `_crop_size_at_result` appears in the S2 session state init loop — matching the actual design where `crop_size_input` is widget-bound (Streamlit auto-initializes) and `_crop_size_at_result` is explicitly tracked.

## Spec Delta Summary

### `openspec/specs/crop-size-config.md` — Complete rewrite

**Before**: Sidebar slider approach (slider range 3..max_odd, step 2, default 15) with reactive X/Y bounds for manual coordinates.

**After**: S8 `st.number_input` approach with:
- CRC-01: S8 number_input for crop size (key="crop_size_input", min=3, max=max_odd, step=2, default=15)
- CRC-02: max_odd dynamic computation (post-S6, floor of 3)
- CRC-03: Reset button (restores 15, calls `st.rerun()`)
- CRC-04: Stale result clearing (no `st.rerun()`, preserves result on same size)
- CRC-05: Crop size validation in core (ValueError if size > min(h,w))
- CRC-06: Center auto mode uses dynamic crop size
- CRC-07: Manual mode with reactive X/Y bounds
- CRC-08: Filter operates on selected crop size

Requirements relabeled from generic headings to `CRC-NN` identifiers.

### `openspec/specs/app-structure.md` — Targeted additions

- **APP-06** (new): S8 crop size widget group — number_input + reset button in columns, dynamic header
- **APP-07** (new): Stale clearing (S8) and S9 tracking (`_crop_size_at_result`)
- **APP-03**: Added reset button scenario (effects inside button block)
- **APP-04**: Added `_crop_size_at_result` to cold start init key list (6 keys)
- **S8 description**: Updated from "Radio, coords, overlay" → "Radio, coords, overlay, number_input, reset, stale guard"
- **S3 description**: Removed "size" from sidebar controls
- Requirements relabeled from `### Requirement:` → `### APP-NN:` format

## Archive Contents

- `proposal.md` ✅
- `design.md` ✅
- `tasks.md` ✅ (6/6 tasks complete)
- `archive-report.md` ✅ (this file)

## Source of Truth Updated

The following main specs reflect the new behavior:
- `openspec/specs/crop-size-config.md`
- `openspec/specs/app-structure.md`

## Deferred Work

None. All success criteria from the proposal were met:
- [x] number_input visible in S8 with odd-only range, default 15
- [x] max_odd clamps to min(H,W) odd, minimum 3
- [x] Reset button restores 15 and triggers `st.rerun()`
- [x] Stale result cleared on crop_size change (no main-flow rerun)
- [x] All tests pass (with updated crop_size test)
- [x] No sidebar elements added

## SDD Cycle Complete

The change has been fully planned, implemented, verified, and archived.
