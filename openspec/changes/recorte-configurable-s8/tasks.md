# Tasks: Recorte Configurable en S8

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 40–60 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

## Phase 1 (RED): Update structural test

- [x] **1.1** Rename `test_crop_size_constant_defined` → `test_crop_size_tracking_key_in_init` in `tests/test_app_structure.py`. Assert that `"_crop_size_at_result"` appears in the S2 init key tuple. Remove old assertions for `CROP_SIZE = 15`.

## Phase 2 (GREEN): Implement crop size config

All changes in `app.py`.

- [x] **2.1** Remove `CROP_SIZE = 15` line. Add `"_crop_size_at_result"` to the session state init tuple in S2.
- [x] **2.2** After `h, w = gray.shape[:2]` (post-S6), add `min_dim = min(h, w)` and `max_odd = max(3, min_dim if min_dim % 2 == 1 else min_dim - 1)`.
- [x] **2.3** Rewrite S8: get `current_crop = st.session_state.get("crop_size_input", 15)`; add stale guard (clear result/raw/filter_applied if `_crop_size_at_result != current_crop`, NO rerun); update header to `"### ✂️ Recorte {current_crop}×{current_crop}"`; add two-column layout with `st.number_input` (key="crop_size_input", step=2, min=3, max=max_odd, value=current_crop) + reset button; replace all `CROP_SIZE` references → `current_crop`.
- [x] **2.4** In S9 apply handler, after storing result/raw/filter_applied, add `st.session_state._crop_size_at_result = st.session_state.crop_size_input`.

## Phase 3 (REFACTOR): Verify cleanup

- [x] **3.1** Verify no stale `CROP_SIZE` references remain in `app.py`. Run `python -m pytest tests/ -v` — all tests pass, including the updated structural test.
