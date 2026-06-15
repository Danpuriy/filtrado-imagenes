# App Structure Specification

## Purpose

Structural and correctness requirements for `app.py`: section ordering, no duplication, button scoping, cold start safety, sidebar/main separation.

## Requirements

### Requirement: Mandatory section order

`app.py` sections MUST appear in this order:

| # | Section | Note |
|---|---------|------|
| 1 | `st.set_page_config` | First Streamlit call |
| 2 | Session state init | Before any widget/conditional |
| 3 | Sidebar controls | Test images, upload, clear, size, kernel, filter, apply, download |
| 4 | Title + branding | Main column |
| 5 | Image decode | Upload or session_state restore |
| 6 | Cold start guard | `st.stop()` + `sys.exit(0)` |
| 7 | Image info panel | Expandable metrics |
| 8 | Crop selection + overlay preview | Radio, coords, overlay |
| 9 | Filter results | One block, `st.session_state.result` |
| 10 | Sidebar branding | Course caption + credits, last |

#### Scenario: Page config first

- GIVEN `app.py` executes
- WHEN Streamlit processes the file
- THEN `st.set_page_config()` precedes any `st.session_state` or `st.sidebar`

#### Scenario: Overlay before results

- GIVEN `st.session_state.result` is not None
- WHEN results section renders
- THEN `draw_crop_overlay()` executes before filter output

#### Scenario: Branding at end

- GIVEN sidebar renders
- WHEN scrolled to bottom
- THEN last elements are the caption and credits expander

### Requirement: No code duplication

Filter selection, apply button, and results display MUST each appear exactly once.

#### Scenario: Single filter selectbox

- GIVEN `app.py` loaded
- WHEN searching for `st.selectbox` with `["Media", "Mediana", "Laplaciano", "Sobel"]`
- THEN exactly one such widget exists

#### Scenario: Single apply button

- GIVEN `app.py` loaded
- WHEN searching for `"Aplicar filtro"`
- THEN exactly one `st.button` with that label appears

#### Scenario: Single results block

- GIVEN `app.py` loaded
- WHEN results section renders
- THEN exactly one block checks `st.session_state.result is not None`

### Requirement: st.button + st.rerun() scoping

Every `st.button()` condition MUST contain ALL side effects — session_state writes and `st.rerun()` — inside the `if` block. No related statement MAY appear at parent indentation.

#### Scenario: Effects inside button block

- GIVEN any test image button renders
- WHEN user clicks it
- THEN `st.session_state.img_gray`, `st.session_state.img_source`, and `st.rerun()` are inside the `if` block
- AND no unconditional `st.rerun()` or `img_source` assignment at parent indentation

#### Scenario: No stray post-apply assignments

- GIVEN `"Aplicar filtro"` button block
- WHEN the `if` ends
- THEN no `st.session_state.result` assignment exists outside the block at same indentation

### Requirement: Cold start safety

Session state MUST be initialized before any access via `if key not in` guards. When no image is available, `st.stop()` MUST halt Streamlit and `sys.exit(0)` MUST follow as non-Streamlit guard.

#### Scenario: Keys initialized before use

- GIVEN `app.py` starts
- WHEN execution reaches any widget
- THEN `img_gray`, `img_source`, `result`, `raw`, `filter_applied` have `None` defaults via `if key not in` checks

#### Scenario: Cold stop with dual guard

- GIVEN no image and no upload
- WHEN execution reaches image decode
- THEN `st.info()` shows instruction
- AND `st.stop()` halts Streamlit
- AND `sys.exit(0)` follows as fallback

### Requirement: Sidebar vs main column separation

All user controls MUST use `st.sidebar.*`. All display output MUST use bare `st.*`.

#### Scenario: Controls in sidebar

- GIVEN any control renders
- THEN it uses `st.sidebar.*`

#### Scenario: Display in main column

- GIVEN display output (images, matrices, info) renders
- THEN it uses bare `st.*`

## Validation Criteria

- [ ] `app.py` starts with no `IndentationError` / `SyntaxError`
- [ ] All `st.button` effects inside their `if` blocks
- [ ] No duplicated filter/results sections
- [ ] Overlay preview before filter results
- [ ] `st.set_page_config` is first Streamlit call
- [ ] Controls in sidebar, display in main column
- [ ] All 45 tests pass
- [ ] `use_container_width` absent from `app.py`
