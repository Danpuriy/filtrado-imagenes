# Crop Size Config Specification

## Purpose

Allow the user to configure the square crop size via a `st.number_input` in the S8 section (main column). The size must be odd, bounded by 3 and min(image height, image width), with a reset button and stale result clearing when the size changes.

## Requirements

### CRC-01: S8 number_input for crop size

The system MUST provide a `st.number_input` labeled "Tamaño de recorte (píxeles)" in the S8 section with: key="crop_size_input", min=3, max={max_odd}, step=2 (odd-only), default=15.

#### Scenario: Widget appears with correct range and default

- GIVEN an image is loaded with dimensions 200×150
- WHEN the S8 section renders
- THEN a number_input appears with min=3, max=149, step=2, value=15

#### Scenario: Step enforces odd-only values

- GIVEN the user types 16 into the widget
- WHEN the widget processes the input
- THEN the displayed value snaps to 15

### CRC-02: max_odd dynamic computation

The system MUST compute `max_odd = max(3, min_dim if min_dim % 2 == 1 else min_dim - 1)` where `min_dim = min(h, w)`, after image decode (post-S6).

#### Scenario: max_odd clamps to largest odd ≤ min(H,W)

- GIVEN an image 50×50
- WHEN max_odd is computed post-S6
- THEN max_odd = 49

#### Scenario: max_odd has floor of 3

- GIVEN an image 2×100
- WHEN max_odd is computed
- THEN max_odd = 3

### CRC-03: Reset button

The system MUST provide a button "📐 Predeterminado 15×15" beside the number_input. When clicked, it MUST set `st.session_state.crop_size_input = 15` and call `st.rerun()`.

#### Scenario: Reset restores default and reruns

- GIVEN crop_size_input is 31
- WHEN the reset button is clicked
- THEN crop_size_input becomes 15
- AND st.rerun() re-executes the app

### CRC-04: Stale result clearing

When crop_size changes and a result exists, the system MUST clear result, raw, and filter_applied. Clearing MUST NOT include `st.rerun()`.

#### Scenario: Stale result cleared on size change

- GIVEN a result exists with _crop_size_at_result=15
- WHEN crop_size_input changes to 21
- THEN result, raw, filter_applied → None

#### Scenario: Same size preserves result

- GIVEN a result exists with _crop_size_at_result=21
- WHEN crop_size_input stays 21
- THEN result, raw, filter_applied are preserved

### CRC-05: Crop size validation in core

The system MUST validate in `crop_manual(gray, x, y, size)` that `size ≤ min(h, w)`. ValueError otherwise.

#### Scenario: crop_manual rejects oversized crop

- GIVEN a 100×80 image
- WHEN crop_manual(…, size=90)
- THEN ValueError raised

#### Scenario: crop_manual accepts valid size

- GIVEN a 100×80 image
- WHEN crop_manual(…, size=79)
- THEN no error, crop extracted

### CRC-06: Center auto mode uses dynamic crop size

The system MUST pass `st.session_state.crop_size_input` to `crop_center(gray, size=crop_size)`.

#### Scenario: Center crop uses selected size

- GIVEN mode is "Centro automático" and crop_size=21
- WHEN overlay and crop are computed
- THEN crop_center(…, size=21)
- AND crop is 21×21

### CRC-07: Manual mode uses dynamic crop size with reactive X/Y bounds

The system MUST pass crop_size to `crop_manual(gray, x, y, size=crop_size)`. Max X = w − crop_size, max Y = h − crop_size, updating reactively.

#### Scenario: X max updates on crop size change

- GIVEN width=200, crop_size=15
- WHEN crop_size → 21
- THEN X max → 179

#### Scenario: Manual crop uses selected size

- GIVEN mode "Manual", crop_size=21, x=10, y=20
- WHEN crop is computed
- THEN crop_manual(…, size=21)
- AND extracted crop is 21×21 at (10,20)

### CRC-08: Filter operates on selected crop size

The system MUST apply the filter to the cropped region using the user-selected crop_size.

#### Scenario: Filter output matches crop size

- GIVEN crop_size=21, any filter
- WHEN "Aplicar filtro" is clicked
- THEN filtered result is 21×21

## Validation Criteria

- [ ] number_input in S8 with odd range, default 15
- [ ] max_odd = largest odd ≤ min(H,W), floor 3
- [ ] Reset restores 15 with st.rerun()
- [ ] Stale result cleared on size change (no rerun)
- [ ] Same size preserves result
- [ ] Center mode uses dynamic crop_size from session_state
- [ ] Manual mode X/Y max update reactively
- [ ] crop_manual raises ValueError if size > min(h,w)
- [ ] Filter output dimension matches crop_size
- [ ] All existing core tests pass
