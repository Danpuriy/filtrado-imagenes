# Proposal: UI — Visualización completa e imágenes de prueba reales

## Intent

The full image is hidden until after filter application, the 15×15 crop is visually meaningless without showing its position in the original, and the app lacks realistic test images matching the project's "Aplicaciones" section.

## Scope

### In Scope
- Full image with red rectangle overlay marking the 15×15 crop region, shown BEFORE filter application
- Four new test image types: `rayos_x`, `documento`, `inspeccion`, `satelital`
- Full image display moved outside the results block, visible immediately on image load

### Out of Scope
- Changes to filter behavior (still operates on 15×15 crop only)
- Batch/multi-image workflows
- Histogram or additional visualization tools
- Dark mode or styling changes

## Capabilities

### New Capabilities
- `crop-overlay`: Red rectangle overlay on the full grayscale image marking where the 15×15 crop is taken; updates reactively with crop mode/coordinates
- `test-images-real-world`: Four new test image types (`rayos_x`, `documento`, `inspeccion`, `satelital`) added to `generar_imagen_prueba()` simulating real applications

### Modified Capabilities
None — `openspec/specs/` is empty; all capabilities are new.

## Approach

**Change 1+3 (full image + overlay before apply):** After image decode and before the filter button, render `st.image()` with the full grayscale. Convert gray → BGR, draw `cv2.rectangle(..., color=(0,0,255), thickness=2)` at current crop coordinates for the overlay. Recompute on every rerun from live widget values.

**Change 2 (new test images):** Extend `generar_imagen_prueba()` in `filtrado/core.py` with 4 new `tipo` cases. Each returns a 200×200 `np.uint8` using pure numpy operations (gradient backgrounds, noise, geometric patterns). Deterministic, stateless — mirrors existing pattern.

**UI flow:** Image loaded → Image info expander → Full image with crop overlay → Crop selection → Filter controls → Apply button → Results.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app.py` | Modified | Restructure UI: move full image before Apply, add overlay rendering |
| `filtrado/core.py` | Modified | Add 4 test image types to `generar_imagen_prueba()` |
| `tests/test_core.py` | Modified | Add tests for new test image functions |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Crop overlay shows wrong region | Low | Compute from same widget values used for actual crop |
| New test images look unrealistic | Low | Use numpy patterns matched to each domain |
| UI restructure breaks layout | Med | Keep column structure; test manually before commit |

## Rollback Plan

`git checkout HEAD -- app.py filtrado/core.py tests/test_core.py` reverts all changes. Run `python -m pytest tests/ -v` to confirm.

## Dependencies

- OpenCV (`cv2.rectangle`) — already installed
- NumPy — already installed

## Success Criteria

- [ ] Full image with red rectangle overlay visible immediately after image load, before filter
- [ ] Overlay correctly marks the 15×15 crop for both center and manual modes
- [ ] All 4 new test images render without errors in the app
- [ ] All existing 30 tests pass unchanged
- [ ] Filter still operates exclusively on the 15×15 crop (verified visually + test suite)
