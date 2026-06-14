# Design: UI — Visualización completa e imágenes de prueba reales

## Technical Approach

Three independent changes in a single change: (1) overlay rendering function in `display.py`, (2) four new test-image types in `core.py`, (3) UI restructure in `app.py` that inserts the overlay between crop selection and filter controls. All non-destructive — existing tests pass unchanged.

## Architecture Decisions

| Decision | Options | Trade-off | Chosen |
|---|---|---|---|
| **Overlay placement** | `app.py` inline vs `display.py` function | Inline is simpler but untestable; a pure function in `display.py` follows existing patterns and can be unit-tested | `display.py` — add `cv2` import alongside existing `numpy`/`matplotlib` |
| **Coordinate source** | Session state vs recompute from live widgets | Session state adds stale-value risk; recomputing from current widget values on every rerun is reactive and correct | Compute `(crop_x, crop_y)` from widget values, same formulas as `crop_center`/`crop_manual` |
| **Test-image determinism** | Global RNG vs per-type seeded RNG | Global couples types; per-type `np.random.default_rng(seed)` keeps them independent and idempotent | Per-type deterministic seeds — `rayos_x=42`, `documento=84`, `satelital=126` |
| **Original image in results** | Remove vs keep | The overlay shows *where* the crop is; the results original shows full-image *comparison* with filtered output — different purposes | Keep both; overlay is pre-apply, results original is post-apply comparison |

## Data Flow

```
Test img button / Upload
        │
        ▼
   gray (np.uint8, full size)
        │
        ├──→ Image info expander
        │
        ├──→ Crop widgets → crop_x, crop_y, cropped (15×15)
        │                      │
        │                      ▼
        │              draw_crop_overlay(gray, crop_x, crop_y)
        │                      │
        │                      ▼
        │              st.image(overlay_bgr)  ← NEW
        │
        ├──→ Kernel/filter widgets
        │
        └──→ Apply → cropped ──→ filter() ──→ Results section
```

## File Changes

| File | Action | Description |
|---|---|---|
| `filtrado/display.py` | Modify | Add `draw_crop_overlay(gray, x, y, size=15)` — gray→BGR copy + `cv2.rectangle()` red border |
| `filtrado/core.py` | Modify | Add 4 `elif` branches to `generar_imagen_prueba()`: `rayos_x`, `documento`, `inspeccion`, `satelital` |
| `app.py` | Modify | Restructure UI order; insert overlay rendering block; add 4 new sidebar test-image buttons |
| `tests/test_core.py` | Modify | Add `TestGenerarImagenPruebaNuevas` — shape, dtype, determinism, structural properties for each new type |

## Interfaces / Contracts

```python
# filtrado/display.py — new function
def draw_crop_overlay(
    img: np.ndarray,        # grayscale (H×W uint8)
    x: int,                 # crop top-left column
    y: int,                 # crop top-left row
    size: int = 15,         # crop size
) -> np.ndarray:            # BGR image (H×W×3 uint8) with red rectangle
    """Return a COPY of *img* converted to BGR with a red rectangle overlay.
    The original *img* is never modified (non-destructive).
    """

# filtrado/core.py — new generar_imagen_prueba cases
# All return 200×200 np.uint8, deterministic
# rayos_x:    gradient 30-80 + bright circle ~180 + salt-pepper 2%
# documento:  background ~220 + dark rectangles 0-30
# inspeccion: uniform ~128 + dark diagonal line ~30
# satelital:  4 quadrants (40/100/160/220) + gaussian noise σ~5
```

## Testing Strategy

| Layer | What to Test | Approach |
|---|---|---|
| Unit — `display.py` | `draw_crop_overlay` output shape (H×W×3), dtype, red pixels at rectangle border, original unchanged | Pure numpy assertions |
| Unit — `core.py` | Each new type: shape=(200,200), dtype=uint8, determinism | `assert arr.shape == (200,200)` + `np.array_equal(a, b)` |
| Unit — `core.py` | Structural properties: gradient range (rayos_x), dark pixels (documento/intensidad), quadrant means (satelital) | `np.mean`, `np.min`, `np.max` bounds |
| Unit — `core.py` | Existing types unchanged | Compare output with known values from before change |
| Manual — UI | Full image with overlay visible pre-apply, rectangle tracks crop mode/coordinates | Visual inspection in Streamlit |
| Manual — UI | New test images render in sidebar and produce correct overlays | Visual inspection |

## Migration / Rollout

No migration required. Atomic change — all three pieces land together, no feature flags.

## Open Questions

- None — specs (`crop-overlay.md`, `test-images-real-world.md`) fully resolve the design.
