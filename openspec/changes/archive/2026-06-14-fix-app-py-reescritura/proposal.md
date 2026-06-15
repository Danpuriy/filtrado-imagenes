# Proposal: fix-app-py-reescritura

## Intent

Fix three blocking bugs (syntax error, duplicated code, disordered flow) in `app.py` that prevent deployment to Streamlit Cloud and break core UX flow, with no functional changes.

## Scope

### In Scope
- Fix sidebar button indentation (`st.rerun()` + `st.session_state.img_source` scoping)
- Eliminate duplicated filter/results section (lines 259–418 & 442–603)
- Reposition crop overlay preview before filter results
- Replace `use_container_width=True` → `width='stretch'`
- Restructure `app.py` from current 621-line broken layout to target layout

### Out of Scope
- No new features, test images, or filter algorithms
- No changes to `filtrado/core.py`, `filtrado/display.py`, or `tests/`
- No spec-level behavior changes — this is pure corrective refactor

## Capabilities

### New Capabilities
None — no new capability introduced.

### Modified Capabilities
None — no spec-level behavior changes. All existing specs (course-branding, crop-overlay, crop-size-config, test-images-real-world) remain valid as-is.

## Approach

Full rewrite of `app.py` to match the target layout. Core logic (filtrado/ package) unchanged — only UI wiring in app.py. Steps:

1. **Skeleton**: Write new layout structure with all sections in correct order
2. **Sidebar sidebar**: Collapse controls (crop size, kernel, filter, apply, upload, test images, download) into sidebar in a single logical block
3. **Main flow**: Title → branding → image load → info → original display → crop selection → overlay → grid/matrix → filter results
4. **Bug fixes applied during rewrite**: correct `st.button` + `st.rerun()` indentation, single filter section, overlay before results
5. **QA**: Run `python -m pytest tests/ -v` + manual visual check of all test images and filters

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app.py` | Modified | Full rewrite — fix bugs, eliminate duplication, reorder flow |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Regressions in filter output | Low | Core in `filtrado/` unchanged; run 45 tests |
| Test image session state broken | Low | Same `st.session_state` contract; manual QA each button |
| Crop overlay misplaced | Medium | Verify `draw_crop_overlay()` called at correct position |

## Rollback Plan

`git checkout -- app.py` and verify with `git diff --stat` — single-file change, immediate revert.

## Dependencies

- Existing 45-passing test suite as regression guard
- Existing `filtrado/` package unchanged

## Success Criteria

- [ ] `python -m pytest tests/ -v` — all 45 tests pass
- [ ] `python app.py` starts without `IndentationError`
- [ ] No duplicated code blocks in `app.py`
- [ ] Crop overlay preview renders before filter results section
- [ ] All 4 filter types (media, mediana, laplaciano, sobel) produce correct results
- [ ] All 8 test image buttons work (4 original + 4 real-world)
- [ ] `use_container_width` does not appear anywhere in `app.py`
