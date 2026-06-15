# Design: app.py Rewrite — Corrective Refactor

## Technical Approach

Full rewrite of `app.py` from 621 lines to ~350–400 lines fixing three bugs:

1. **Syntax error**: 8 test image buttons have `img_source` assignment at parent indent level with a dangling `st.rerun()` at wrong indent → `IndentationError`
2. **Duplicated code**: Filter selection + results appear twice (lines 259–418 and 442–603) with crop overlay wedged between them
3. **Disordered flow**: Crop overlay preview renders AFTER first results block instead of before

Core `filtrado/` package and all 45 tests UNCHANGED. Only Streamlit UI wiring in `app.py` changes.

## Architecture Decisions

### Decision: Sidebar as contiguous block (Section 3)

| Option | Tradeoff | Decision |
|--------|----------|----------|
| All sidebar calls in one block at file top | Branding renders even after `st.stop()`; widget order explicit | ✅ **Adopted** |
| Interleave sidebar calls throughout file | Keeps controls near their logical main-column section | ❌ Rejected — branding risk |

### Decision: Filter controls in main column, not sidebar

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Apply button + filter select in main column | Reads `cropped` local var from crop section naturally | ✅ **Adopted** |
| Apply button in sidebar | Requires storing `cropped` in session_state (new key) or recomputing it inside handler | ❌ Rejected — violates "same contract" rule |

### Decision: Download button in sidebar section

| Option | Tradeoff | Decision |
|--------|----------|----------|
| `st.sidebar.download_button` in Section 3, conditional on `result` | All sidebar elements in one place; correct visual order (download before branding) | ✅ **Adopted** |
| Inside results block (current pattern) | Download appears AFTER branding in sidebar order | ❌ Rejected — wrong visual order |

### Decision: No `st.stop()` after results section

| Option | Tradeoff | Decision |
|--------|----------|----------|
| Skip results silently when `result is None` | Cold start guard already handles no-image case; branding always shows | ✅ **Adopted** |
| `else: st.stop()` (current bug) | Prevents sidebar branding from rendering | ❌ Rejected |

## Section Layout

```
┌──────────────────────────────────────────────────┐
│ SECTION 1:  st.set_page_config(layout="wide")    │
├──────────────────────────────────────────────────┤
│ SECTION 2:  Session state init (5 keys → None)   │
├──────────────────────────────────────────────────┤
│ SECTION 3:  SIDEBAR (contiguous block)           │
│  ├─ Dark mode toggle                             │
│  ├─ "Controles" header                           │
│  ├─ Test images (8 buttons, 2×2 cols)            │
│  ├─ File upload                                   │
│  ├─ Clear button (resets all state)              │
│  ├─ Crop size slider (3..max_odd, step 2, dflt15)│
│  ├─ Download btn (st.sidebar, conditional result) │
│  └─ Branding: caption + credits expander (ALWAYS) │
├──────────────────────────────────────────────────┤
│ SECTION 4:  Title + "MA475 • UPC • 2026-S6"      │
├──────────────────────────────────────────────────┤
│ SECTION 5:  Image decode (upload / session_state) │
├──────────────────────────────────────────────────┤
│ SECTION 6:  Cold start guard (st.stop + sys.exit) │
├──────────────────────────────────────────────────┤
│ SECTION 7:  Image info expander (metrics)        │
├──────────────────────────────────────────────────┤
│ SECTION 8:  Crop selection + overlay preview     │
│  ├─ st.radio: auto / manual coords               │
│  ├─ Crop extraction (crop_center / crop_manual)   │
│  ├─ st.caption with crop dimensions               │
│  └─ OVERLAY: draw_crop_overlay → st.image       │
├──────────────────────────────────────────────────┤
│ SECTION 9:  Filter controls + apply + results    │
│  ├─ Kernel slider (3..15, step 2, dflt 3)        │
│  ├─ Filter selectbox (4 options)                  │
│  ├─ Apply button → store result + rerun          │
│  └─ if result: display (SINGLE copy)             │
│      ├─ Original + crop side-by-side              │
│      ├─ Digitalization grid + matrix text         │
│      ├─ Edge: 2×3 grid (3 cols × 2 rows)         │
│      ├─ Smooth: 2×2 grid + comparison             │
│      └─ (download already handled in Section 3)   │
└──────────────────────────────────────────────────┘
```

## Session State Contract

| Key | Type | Set by | Read by | Reset by |
|-----|------|--------|---------|----------|
| `img_gray` | `ndarray\|None` | Test image buttons, decode section | All main sections, apply button | Clear, new upload |
| `img_source` | `str\|None` | Test image buttons, decode | Download filename | Clear |
| `result` | `ndarray\|None` | Apply button | Results section, download section | Clear |
| `raw` | `ndarray\|None` | Apply button (edge filters) | Results (edge layout) | Clear |
| `filter_applied` | `str\|None` | Apply button | Results section | Clear |

All init: `if key not in st.session_state: st.session_state[key] = None`. No new keys added. Clear button sets ALL 5 keys to None + `st.rerun()`.

## Button Scoping Pattern

```python
# CORRECT — ALL side effects inside the `if` block, no orphan statements
if st.button("📊 Gradiente"):
    st.session_state.img_gray = generar_imagen_prueba("gradiente")
    st.session_state.img_source = "prueba_gradiente"
    st.rerun()
```

Applies identically to all 8 test image buttons and the "Aplicar filtro" button.

## Error / Edge Case Handling

| Scenario | Behavior |
|----------|----------|
| Cold start (no image, no upload) | `st.info()` → `st.stop()` → `sys.exit(0)` |
| Upload decode fails | `st.error("No se pudo decodificar...")` → `st.stop()` |
| Color image, user declines convert | `st.error("Imagen rechazada...")` → `st.stop()` |
| Manual crop out of bounds | `crop_manual` → `ValueError` → `st.error()` → `st.stop()` |
| `img_source` is None (edge case) | Download filename: `None_filtrado_media.png` — acceptable, branding always shows |
| Crop size exceeds bounds | Slider max clamps to `max_odd = max(3, min_dim if odd else min_dim-1)` |

## Key Implementation Notes

1. **max_odd** computed right after cold start guard: `max_odd = max(3, min_dim if min_dim % 2 else min_dim - 1)`. Slider in Section 3 uses `value=min(15, max_odd)`.

2. **Overlay coords** must match crop function logic: center mode uses `(h-1)//2, (w-1)//2` minus `crop_size//2`. Manual mode reads `x, y` from widget values. Passed to `draw_crop_overlay()` which makes a COPY — non-destructive per spec.

3. **Download buffer** generated fresh inside the conditional block in Section 3: `cv2.imencode(".png", result_img)` → `BytesIO`. `st.session_state.img_source` and `st.session_state.filter_applied` provide filename components.

4. **Edge vs Smooth layout**: Laplacian/Sobel show raw matrix + normalized + 2×3 grid. Media/Mediana show 2×2 grid + comparison. Both are SINGLE copies, no duplication.

5. **No `use_container_width`**: All `st.image()` calls use `clamp=True, width='stretch'`. Zero occurrences of `use_container_width`.

6. **Dark mode**: Toggle in sidebar applies CSS via `st.markdown(unsafe_allow_html=True)` in the main column — works because the sidebar toggle is processed first.
