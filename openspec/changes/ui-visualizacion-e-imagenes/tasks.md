# Tasks: UI — Visualización completa e imágenes de prueba reales

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~210 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

## Phase 1: Foundation — Tests first (TDD RED)

- [x] 1.1 Create `tests/test_display.py` — write failing tests for `draw_crop_overlay`: shape is H×W×3 BGR, dtype=uint8, red pixels at rectangle border, original array NOT modified
- [x] 1.2 Add `TestGenerarImagenPruebaNuevas` to `tests/test_core.py` — write failing tests for 4 new types: shape=(200,200), dtype=uint8, determinism, structural checks (rayos_x intensity range, documento dark pixels, inspeccion dark line, satelital quadrant means), existing types unchanged

## Phase 2: Core implementation (GREEN)

- [x] 2.1 Add `draw_crop_overlay(img, x, y, size=15) -> np.ndarray` to `filtrado/display.py` — gray→BGR copy via `cv2.cvtColor`, draw red `cv2.rectangle((0,0,255), thickness=2)`, return copy (never mutate original)
- [x] 2.2 Add 4 new `elif` branches to `generar_imagen_prueba()` in `filtrado/core.py`: `rayos_x` (gradient+bright circle+noise, seed=42), `documento` (light background+dark rects, seed=84), `inspeccion` (uniform+dark line, seed=...), `satelital` (4 quadrants+gaussian noise, seed=126)

## Phase 3: UI integration (app.py)

- [x] 3.1 Import `draw_crop_overlay` from `filtrado.display` in `app.py`
- [x] 3.2 Add 4 new sidebar buttons (rayos_x, documento, inspeccion, satelital) alongside existing test image buttons
- [x] 3.3 Insert overlay rendering block between crop selection widgets and filter controls: compute `(crop_x, crop_y)` from live widget values (same formulas as crop functions), call `draw_crop_overlay(gray, crop_x, crop_y)`, display with `st.image()`
- [x] 3.4 Ensure overlay updates reactively on crop mode switch and coordinate changes (Streamlit rerun handles this naturally — no extra state needed)

## Phase 4: Verification

- [x] 4.1 Run `python -m pytest tests/ -v` — confirm all new + 30 existing tests pass
- [ ] 4.2 Launch `streamlit run app.py` — verify full image + overlay visible before filter controls, rectangle matches crop for both center and manual modes, all 4 new test images render in sidebar and produce correct overlays
