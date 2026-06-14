# Crop Overlay Specification

## Purpose

Show the full grayscale image with a red rectangle overlay marking where the crop is taken. The overlay must appear before filter application and update reactively when crop mode, coordinates, or crop size change.

## ADDED Requirements

### Requirement: Dynamic rectangle size from crop size parameter

The system MUST use the dynamic `crop_size` parameter (not hardcoded 15) when drawing the rectangle. The rectangle MUST be drawn from (x, y) to (x + crop_size, y + crop_size) using `cv2.rectangle(img, (x, y), (x + crop_size, y + crop_size), color=(0,0,255), thickness=2)`.

#### Scenario: Overlay rectangle matches selected crop size

- GIVEN crop_size=21, mode="Centro automático"
- WHEN the full image is displayed
- THEN the red rectangle dimensions are exactly 21×21 pixels

#### Scenario: Overlay rectangle updates when crop size changes

- GIVEN crop_size=15, overlay shows 15×15 rectangle
- WHEN user changes crop_size to 31
- THEN the overlay rectangle updates to 31×31 pixels on next rerun

## MODIFIED Requirements

### Requirement: Reactive red rectangle overlay

The system MUST convert the grayscale image to BGR with `cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)` and draw a red rectangle at the current crop coordinates using `cv2.rectangle(img, (x, y), (x + crop_size, y + crop_size), color=(0,0,255), thickness=2)`. The overlay MUST recompute on every Streamlit rerun from live widget values including crop_size.
(Previously: rectangle used hardcoded 15×15 dimensions)

#### Scenario: Center mode overlay

- GIVEN crop mode is set to "Centro automático"
- WHEN the full image is displayed
- THEN a red rectangle is drawn at the center crop coordinates computed by `crop_center()` with the current `crop_size`
- AND the rectangle dimensions are exactly crop_size×crop_size pixels

#### Scenario: Manual mode overlay updates reactively

- GIVEN crop mode is set to "Manual (ingresar coordenadas)"
- WHEN the user changes the X or Y coordinate widgets
- THEN the red rectangle overlay moves to match the new (x, y) coordinates
- AND the rectangle dimensions remain exactly crop_size×crop_size pixels

#### Scenario: Overlay updates on mode switch

- GIVEN the full image with overlay is displayed in "Centro automático" mode
- WHEN the user switches to "Manual (ingresar coordenadas)"
- THEN the overlay redraws at the manual coordinate position (default x=0, y=0)
- AND the rectangle dimensions match the current crop_size

#### Scenario: Overlay updates on crop size change

- GIVEN the full image with overlay is displayed at crop_size=15
- WHEN the user changes the crop size slider to 21
- THEN the overlay redraws with 21×21 rectangle at the same (x, y) coordinates

### Requirement: Non-destructive overlay

The overlay MUST NOT modify the image data stored in `st.session_state.img_gray` or the `cropped` array used for filtering. The rectangle is drawn on a COPY of the BGR-converted image solely for display.
(Previously: referenced 15×15 crop; now references dynamically sized crop)

#### Scenario: Filter operates on unmodified crop

- GIVEN the full image is displayed with a red rectangle overlay
- WHEN the user clicks "Aplicar filtro"
- THEN the filter operates on the original crop_size×crop_size crop (not the overlaid image)
- AND the result matches the expected filter output for that crop region

## Validation Criteria

- [ ] Full image with red rectangle visible before filter application
- [ ] Rectangle position matches center crop coordinates in auto mode
- [ ] Rectangle follows manual X/Y coordinate changes
- [ ] Rectangle updates on mode switch without page reload
- [ ] Rectangle dimensions match selected crop_size (not hardcoded 15)
- [ ] Rectangle updates reactively when crop_size slider changes
- [ ] Filter output is identical with and without overlay active
- [ ] All existing 30+ tests continue to pass