# Proposal: Configurable Crop Size with Course Branding

## Intent
Make crop size user-configurable (odd 3–min(H,W)) with validation; add visible MA475 UPC 2026-S6 attribution.

## Scope

### In Scope
- Sidebar slider for crop size (default 15, step 2, odd only, max = min(H,W))
- Validation in UI and core: crop size ≤ min(image dimensions)
- Center auto & manual modes use dynamic size
- Overlay rectangle updates reactively
- Manual X/Y max values recalculated on size change
- Filter operates on selected crop size
- Header: "MA475 • UPC • 2026-S6" under title
- Sidebar footer with course line
- Expander "ℹ️ Créditos del proyecto" with 5 members, professor, period

### Out of Scope
- Even crop sizes, non-square crops, session persistence, branding in exports, i18n

## Capabilities

### New Capabilities
- `crop-size-config`: Configurable square crop size with odd-number validation & boundary checks

### Modified Capabilities
- `crop-overlay`: Rectangle dimensions now dynamic; X/Y max values reactive to crop size

## Approach

**1. Configurable Crop Size**
- `app.py`: Add slider `st.slider("Tamaño de recorte", 3, max_odd, 15, step=2)` where `max_odd = min(H,W) // 2 * 2 + 1`. Pass `crop_size` to `crop_center()`, `crop_manual()`, `draw_crop_overlay()`. Recalc `max_x = w - crop_size`, `max_y = h - crop_size` for manual inputs.
- `core.py`: `crop_center/crop_manual` already accept `size`; add defensive check in `crop_manual` for `size > min(h,w)`.
- `display.py`: `draw_crop_overlay` already accepts `size` — pass dynamic value.

**2. Course Branding**
- `app.py`: Add header line after title; sidebar footer caption; sidebar expander with full credits.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `app.py` | Modified | Crop slider, dynamic X/Y max, pass size to crop/overlay, branding |
| `filtrado/display.py` | Modified | Ensure `draw_crop_overlay` uses dynamic size |
| `filtrado/core.py` | Modified | Defensive size validation in `crop_manual` |
| `openspec/specs/crop-overlay.md` | Delta spec | Update overlay for dynamic size |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Slider max fails for tiny images | Low | Clamp to 3 if min_dim < 3 |
| Tests assume 15×15 | Medium | Default unchanged; tests pass size explicitly |
| Off-by-one for even sizes | Low | Slider odd-only constraint |

## Rollback Plan
Revert `app.py` (slider + branding), `core.py` (validation), delete delta spec. Default 15×15 restored.

## Dependencies
None (Streamlit/NumPy/OpenCV only)

## Success Criteria
- [ ] Slider appears with odd-only range, default 15
- [ ] Center & manual modes use selected size
- [ ] X/Y max values update reactively on size change
- [ ] Overlay rectangle matches selected size
- [ ] Filter applies to selected crop size
- [ ] Header, sidebar footer, expander with all credits visible
- [ ] All 30+ existing tests pass
- [ ] Core validation rejects oversized crops