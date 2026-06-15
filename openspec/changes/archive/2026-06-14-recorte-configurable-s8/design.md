# Design: Recorte Configurable en S8

## Technical Approach

Replace the compile-time constant `CROP_SIZE = 15` with a runtime `st.number_input` widget embedded in S8 where the crop is selected. The value flows through `st.session_state.crop_size_input`, consumed by crop/overlay functions. A stale-clearing protocol invalidates filter results when the crop size changes, without a full-app `st.rerun()`. The `max_odd` bound is computed dynamically after image dimensions are known (post-S6 cold start guard), keeping the constraint reactive.

## Architecture Decisions

| Decision | Option | Tradeoff | Choice |
|----------|--------|----------|--------|
| Widget placement | Sidebar vs S8 | Sidebar caused layout/state issues in prior attempt; S8 colocation avoids that | S8 columns |
| State management | Streamlit widget key vs manual session var | Widget key auto-syncs; manual var adds ceremony | `key="crop_size_input"` on number_input |
| Stale clearing | `st.rerun()` vs silent clear | rerun flashes UI; silent clear is smooth and matches existing pattern | Silent clear (no rerun) |
| `_crop_size_at_result` init | In S2 loop vs lazy in code | S2 loop guarantees init before any access | In S2 loop |

## Data Flow

```
Post-S6: h,w → max_odd = max(3, odd(min(h,w)))
               ↓
S8: st.number_input(min=3, max=max_odd, step=2, key="crop_size_input")
               ↓
    st.session_state.crop_size_input (default 15)
               ↓
    Stale guard: if result exists and _crop_size_at_result ≠ current_crop
      → clear result/raw/filter_applied
               ↓
    crop_center/gray, size=current_crop) or crop_manual(..., size=current_crop)
               ↓
    draw_crop_overlay(..., size=current_crop)
               ↓
S9: apply → store result → _crop_size_at_result = crop_size_input
```

## Session State Keys

| Key | Init | Set by | Purpose |
|-----|------|--------|---------|
| `crop_size_input` | Widget default 15 | `st.number_input` key sync | Current crop size |
| `_crop_size_at_result` | `None` | S9 apply handler | Tracks size used for current result |
| `result` | `None` (existing) | S9 apply | Filter output |
| `raw` | `None` (existing) | S9 apply | Raw edge map (Laplacian/Sobel) |
| `filter_applied` | `None` (existing) | S9 apply | Filter name string |

## Widget Keys

| Widget | Key | Type | Purpose |
|--------|-----|------|---------|
| `number_input` | `crop_size_input` | `str` auto-key | Binds widget to session state |
| Reset button | — | `st.button` | Sets `crop_size_input=15` → `st.rerun()` |

## Code Changes

### S2 — Session State Init

Remove `CROP_SIZE = 15`. Add `_crop_size_at_result` to the init loop:

```python
for key in ("img_gray", "img_source", "result", "raw", "filter_applied", "_crop_size_at_result"):
    if key not in st.session_state:
        st.session_state[key] = None
```

### Post-S6 — max_odd Computation

After `h, w = gray.shape[:2]` (line 202), add:

```python
min_dim = min(h, w)
max_odd = max(3, min_dim if min_dim % 2 == 1 else min_dim - 1)
```

### S8 — Complete Rewritten Section

```python
# ---------------------------------------------------------------------------
# S8: Crop selection + overlay preview — BEFORE filter results
# ---------------------------------------------------------------------------
current_crop = st.session_state.get("crop_size_input", 15)

# Stale guard: clear result when crop size changes (NO st.rerun())
if (st.session_state.result is not None
        and st.session_state._crop_size_at_result != current_crop):
    st.session_state.result = None
    st.session_state.raw = None
    st.session_state.filter_applied = None
    st.session_state._crop_size_at_result = None

st.markdown(f"### ✂️ Recorte {current_crop}×{current_crop}")

crop_option = st.radio(
    "Seleccione modo de recorte:",
    ["Centro automático", "Manual (ingresar coordenadas)"],
    horizontal=True,
)

col1, col2 = st.columns(2)
with col1:
    st.number_input(
        "Tamaño de recorte (píxeles)",
        min_value=3,
        max_value=max_odd,
        value=current_crop,
        step=2,
        key="crop_size_input",
    )
with col2:
    if st.button("📐 Predeterminado 15×15"):
        st.session_state.crop_size_input = 15
        st.rerun()

if crop_option == "Centro automático":
    cropped = crop_center(gray, size=current_crop)
else:
    max_x = max(0, w - current_crop)
    max_y = max(0, h - current_crop)
    coord_col1, coord_col2 = st.columns(2)
    with coord_col1:
        x = st.number_input("X (columna)", min_value=0, max_value=max_x, value=0)
    with coord_col2:
        y = st.number_input("Y (fila)", min_value=0, max_value=max_y, value=0)
    try:
        cropped = crop_manual(gray, int(x), int(y), size=current_crop)
    except ValueError as e:
        st.error(str(e))
        st.stop()

st.caption(f"Recorte de {cropped.shape[1]}×{cropped.shape[0]} píxeles listo")

st.markdown("### 🖼️ Vista previa del recorte")
if crop_option == "Centro automático":
    cy, cx = (h - 1) // 2, (w - 1) // 2
    half = current_crop // 2
    crop_x = cx - half
    crop_y = cy - half
else:
    crop_x = int(x)
    crop_y = int(y)

overlay_bgr = draw_crop_overlay(gray, crop_x, crop_y, size=current_crop)
st.image(
    overlay_bgr,
    caption=f"Imagen completa con recorte (rectángulo rojo = zona {current_crop}×{current_crop})",
    clamp=True,
    width="stretch",
)
```

### S9 — Apply Handler Tracking

After `st.session_state.filter_applied = filter_option` (and before `st.rerun()`), add:

```python
st.session_state._crop_size_at_result = st.session_state.crop_size_input
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `app.py` | Modify | S2, post-S6, S8 (full rewrite), S9 (one line) |
| `tests/test_app_structure.py` | Modify | Update `test_crop_size_constant_defined` |

## Test Changes

`test_crop_size_constant_defined` (line 193) must change from asserting `CROP_SIZE = 15` exists, to asserting `crop_size_input` key appears in session state init:

```python
def test_crop_size_input_key_in_init(self):
    """app.py MUST initialize crop_size_input in session state."""
    source = read_app()
    assert "crop_size_input" in source, (
        "crop_size_input widget key not found in app.py"
    )
    # Verify it's inside the session state init loop
    init_section = source[source.index("for key in"):source.index("\n\n")]
    assert "crop_size_input" not in init_section  # No, it's widget-driven
```

Actually — `crop_size_input` is NOT in the S2 init loop because it's a widget-bound key (Streamlit auto-initializes it). The only new init key is `_crop_size_at_result`. So the updated test should check that `_crop_size_at_result` is in the init loop:

```python
def test_crop_size_tracking_key_in_init(self):
    """app.py MUST initialize _crop_size_at_result in session state."""
    source = read_app()
    init_section = source[source.index("for key in"):source.index("\n\n")]
    assert "_crop_size_at_result" in init_section, (
        "_crop_size_at_result must be in session state init"
    )
```

## Migration / Rollback

- **Migration**: No data migration. Widget default (15) matches previous constant semantics.
- **Rollback**: Revert `app.py` — restore `CROP_SIZE = 15`, remove `_crop_size_at_result`, undo S8 changes. Revert test file. Core/display unchanged — single-file revert.

## Open Questions

None.
