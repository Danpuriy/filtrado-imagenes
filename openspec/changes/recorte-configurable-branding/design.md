# Design: Configurable Crop Size with Course Branding

## Technical Approach

This change introduces a user-configurable crop size (odd 3–min(H,W)) with reactive validation and adds MA475 UPC 2026-S6 course branding throughout the UI. The approach follows the existing patterns in `app.py` — widget-driven reactive updates with values passed to pure functions in `filtrado/core.py` and `filtrado/display.py`.

Key changes:
1. **Crop size slider** in sidebar computes `max_odd = largest odd ≤ min(H,W)` inline; passes `crop_size` to `crop_center()`, `crop_manual()`, `draw_crop_overlay()`
2. **Reactive X/Y bounds**: `max_x = w - crop_size`, `max_y = h - crop_size` recalculated on every rerun
3. **Core validation**: `crop_manual()` adds defensive check raising `ValueError` if `size > min(h,w)`
4. **Branding**: Header line under title, sidebar footer caption, and collapsed expander with full credits

## Architecture Decisions

| Decision | Options | Trade-off | Chosen |
|----------|---------|-----------|--------|
| Crop size state | Session state vs read from widget directly | Session state persists; slider value already in widget | Read from widget directly (no extra state) |
| Branding placement | Header only / sidebar only / all three | All three cover different visibility needs | All three |
| Validation layer | UI only vs core only vs both | UI gives immediate feedback; core is safety net | Both (defense in depth) |
| Slider max computation | Inline vs helper function | Reusable for X/Y bounds | Inline in `app.py` (used once per render) |

## Data Flow

```
Image loaded → gray (H×W)
       │
       ├──→ max_odd = largest_odd(min(H,W)) clamped ≥ 3
       │
       ├──→ Slider "Tamaño de recorte" → crop_size
       │            │
       │            ├──→ max_x = W - crop_size
       │            ├──→ max_y = H - crop_size
       │            ├──→ crop_center(gray, crop_size) OR crop_manual(gray, x, y, crop_size)
       │            ├──→ draw_crop_overlay(gray, crop_x, crop_y, crop_size)
       │            └──→ cropped → filter → results
       │
       └──→ Branding: header + sidebar footer + expander
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app.py` | Modify | Add crop size slider, dynamic X/Y bounds, pass `crop_size` to crop/overlay functions, add branding (header, sidebar footer, expander) |
| `filtrado/core.py` | Modify | Add defensive validation in `crop_manual()` raising `ValueError` if `size > min(h,w)` |
| `filtrado/display.py` | No change | `draw_crop_overlay()` already accepts `size` parameter — just pass dynamic value |

## Interfaces / Contracts

```python
# filtrado/display.py — existing, unchanged signature
def draw_crop_overlay(img: np.ndarray, x: int, y: int, size: int = 15) -> np.ndarray:
    """Return BGR copy with red rectangle at (x,y) to (x+size, y+size)."""

# filtrado/core.py — existing, already accepts size
def crop_center(img: np.ndarray, size: int = 15) -> np.ndarray:
    ...

def crop_manual(img: np.ndarray, x: int, y: int, size: int = 15) -> np.ndarray:
    # NEW: raises ValueError if size > min(h, w)
    ...
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|--------------|----------|
| Unit - core.py | `crop_manual` raises `ValueError` for oversized crop | `pytest.mark.parametrize` size > min_dim |
| Unit - core.py | `crop_center`/`crop_manual` work for various sizes | Parametrize size=3, 15, 31 |
| Unit - display.py | `draw_crop_overlay` output shape H×W×3, red border pixels | NumPy assertions on returned array |
| Unit - app.py | Slider max computation, X/Y bounds helper | Pure function tests (extracted logic) |
| Manual - UI | Full flow: slider → overlay → crop → filter | Visual verification in Streamlit |

## Migration / Rollout

No migration required. Default crop size remains 15, so existing behavior is preserved. All 30+ existing tests pass without modification.

## Open Questions

- [ ] None — all decisions resolved per proposal and specs