# Proposal: Recorte Configurable en S8

## Intent

Add an adjustable crop size control integrated in the S8 crop section (main column) with a reset button, replacing the hardcoded `CROP_SIZE = 15`. The previous sidebar-slider approach caused layout and state issues; this version embeds the control where the crop lives.

## Scope

### In Scope
- Replace `CROP_SIZE = 15` with `st.number_input` in S8 (key="crop_size_input", step=2, min=3, max=max_odd, default=15)
- Re-add `max_odd` computation after image dimensions (post-S6 cold start guard)
- Add "📐 Predeterminado 15×15" reset button beside number_input → `st.rerun()`
- Add stale result clearing: when crop_size changes and result exists, clear result/raw/filter_applied — NO `st.rerun()`
- Add `_crop_size_at_result` tracking in S9 apply handler
- Update `test_crop_size_constant_defined` for dynamic approach

### Out of Scope
- No changes to `filtrado/core.py`, `filtrado/display.py`, or `test_core.py`/`test_display.py`
- No sidebar elements added or modified
- No `st.rerun()` outside button callbacks

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `crop-size-config`: Crop size control moves from sidebar slider → S8 `st.number_input` with reset button and stale clearing protocol
- `app-structure`: S8 surface expanded with number_input + reset button; session state extended (`crop_size_input`, `_crop_size_at_result`)

## Approach

1. **S2 init**: Remove `CROP_SIZE = 15`. Add `_crop_size_at_result` to session state init loop.
2. **Post-S6**: Compute `max_odd = max(3, min_dim if min_dim % 2 == 1 else min_dim - 1)`.
3. **S8**: Add `st.number_input(..., key="crop_size_input")` and reset button beside it. Stale guard: if result exists and `_crop_size_at_result != current_crop`, clear result/raw/filter_applied.
4. **S9 apply**: After storing result, set `st.session_state._crop_size_at_result = st.session_state.crop_size_input`.
5. **All CROP_SIZE references** → `st.session_state.crop_size_input`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app.py` | Modified | S2 init, post-S6 max_odd, S8 widget+reset+stale guard, S9 tracking |
| `tests/test_app_structure.py` | Modified | Update `test_crop_size_constant_defined` |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Manual mode X/Y max out of sync | Low | Compute from `crop_size_input` inline |
| Widget state conflict on rerun | Low | Explicit `key="crop_size_input"` |
| Stale clearing loses user work silently | Low | Same existing clear pattern — user changes crop, expects new result |

## Rollback Plan

Revert `app.py` to restore `CROP_SIZE = 15`. Revert test. Core/display unchanged — single-file revert.

## Dependencies

None.

## Success Criteria

- [ ] number_input visible in S8 with odd-only range, default 15
- [ ] max_odd clamps to min(H,W) odd, minimum 3
- [ ] Reset button restores 15 and triggers `st.rerun()`
- [ ] Stale result cleared on crop_size change (no main-flow rerun)
- [ ] All tests pass (with updated crop_size test)
- [ ] No sidebar elements added
