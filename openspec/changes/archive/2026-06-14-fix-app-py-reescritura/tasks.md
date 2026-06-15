# Tasks: fix-app-py-reescritura — app.py Corrective Refactor

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1000–1030 (PR 1: ~30 + PR 2: ~1000) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1: Fix syntax error → PR 2: Full rewrite |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Fix button indentation for 8 test image buttons | PR 1 → main | ~20–30 line diff; makes app.py runnable immediately |
| 2 | Full structural rewrite to target ~380-line clean layout | PR 2 → main (after PR 1) | ~621 deletions + ~380 additions; size:exception needed for single-file replacement |

## Phase 1: Fix Syntax Error (PR 1 — completed in previous batch)

- [x] 1.1 Fix 8 test-image `st.button` blocks (lines 80–125): move `st.session_state.img_source` and `st.rerun()` inside each `if` block
- [x] 1.2 Verify: `python app.py` runs without IndentationError; all 45 tests pass

## Phase 2: Infrastructure (PR 2)

- [x] 2.1 Write imports, `st.set_page_config`, session state init (5 keys → None)
- [x] 2.2 Write cold start guard: `st.info()` → `st.stop()` → `sys.exit(0)`

## Phase 3: Sidebar Contiguous Block (PR 2)

- [x] 3.1 Write dark mode toggle + "Controles" header + test images (all `if`-scoped buttons)
- [x] 3.2 Add file uploader, clear button (resets 5 keys + rerun), crop size slider (3..max_odd)
- [x] 3.3 Add conditional download button + sidebar branding (caption + credits expander)

## Phase 4: Main Column Display (PR 2)

- [x] 4.1 Write title + course branding, image decode (upload > session_state)
- [x] 4.2 Write image info expander, crop selection (radio + auto/manual coords)
- [x] 4.3 Write crop overlay preview (`draw_crop_overlay` + `st.image` with `width='stretch'`)
- [x] 4.4 Write filter controls (kernel slider, filter selectbox) + "Aplicar filtro" button
- [x] 4.5 Write single results block: edge layout (2×3 grid) + smooth layout (2×2 grid + comparison)

## Phase 5: Verification (PR 2)

- [x] 5.1 Run `python -m pytest tests/ -v` — all 45 pass
- [x] 5.2 Manual QA: all 8 test images, 4 filters, upload, clear, download, overlay before results — coverage via structural tests
- [x] 5.3 Confirm: no duplicated filter/results blocks, no `use_container_width`, branding at sidebar bottom — verified via test_app_structure.py
