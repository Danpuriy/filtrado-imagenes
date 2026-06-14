# Tasks: Configurable Crop Size with Course Branding

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~150 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Configurable crop size + branding | PR 1 | All changes fit in single PR under 400 lines |

## Phase 1: Tests First (TDD RED)

- [x] 1.1 Test: `crop_manual` raises ValueError when size > min(h,w) in test_core.py
- [x] 1.2 Test: `crop_center`/`crop_manual` work for various sizes (3, 15, 31) in test_core.py
- [x] 1.3 Test: `draw_crop_overlay` output shape H×W×3, red border pixels for dynamic size in test_display.py
- [x] 1.4 Test: Slider max computation helper (largest_odd ≤ min(H,W)) in test_core.py or new test_app.py

## Phase 2: Core Implementation (GREEN)

- [x] 2.1 Add defensive validation in `crop_manual()` in filtrado/core.py: raise ValueError if size > min(h,w)
- [x] 2.2 No change needed in display.py (already accepts size parameter)

## Phase 3: UI Integration (app.py)

- [x] 3.1 Add crop size slider in sidebar: "Tamaño de recorte", min=3, max=max_odd, step=2, default=15
- [x] 3.2 Compute max_odd = largest odd ≤ min(H,W) (clamped ≥ 3)
- [x] 3.3 Dynamic X/Y bounds: max_x = w - crop_size, max_y = h - crop_size
- [x] 3.4 Pass crop_size to crop_center(), crop_manual(), draw_crop_overlay()
- [x] 3.5 Add header branding: "MA475 • UPC • 2026-S6" under title
- [x] 3.6 Add sidebar footer caption: "MA475 • UPC • 2026-S6"
- [x] 3.7 Add sidebar expander "ℹ️ Créditos del proyecto" with full metadata (course, institution, 5 integrantes, profesor, period)

## Phase 4: Verification

- [x] 4.1 Run pytest tests/ -v — all new + existing tests pass
- [ ] 4.2 Manual: streamlit run app.py — verify slider, overlay, branding, filter on dynamic crop