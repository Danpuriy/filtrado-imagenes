# Crop Overlay Specification

## Purpose

Show the full grayscale image with a red rectangle overlay marking where the 15×15 crop is taken. The overlay must appear before filter application and update reactively when crop mode or coordinates change.

## Requirements

### Requirement: Full-image display before filter

The system MUST render the full grayscale image using `st.image()` immediately after image decode, positioned between the crop selection widgets and the filter controls. The full image MUST be visible regardless of whether a filter has been applied.

#### Scenario: Full image shown on image load

- GIVEN a user has uploaded a JPG or selected a test image
- WHEN the image is decoded and validated
- THEN the full grayscale image is displayed above the crop selection widgets
- AND the image is visible before any filter button is clicked

### Requirement: Reactive red rectangle overlay

The system MUST convert the grayscale image to BGR with `cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)` and draw a red rectangle at the current crop coordinates using `cv2.rectangle(img, (x, y), (x+15, y+15), color=(0,0,255), thickness=2)`. The overlay MUST recompute on every Streamlit rerun from live widget values.

#### Scenario: Center mode overlay

- GIVEN crop mode is set to "Centro automático"
- WHEN the full image is displayed
- THEN a red rectangle is drawn at the center crop coordinates computed by `crop_center()`
- AND the rectangle dimensions are exactly 15×15 pixels

#### Scenario: Manual mode overlay updates reactively

- GIVEN crop mode is set to "Manual (ingresar coordenadas)"
- WHEN the user changes the X or Y coordinate widgets
- THEN the red rectangle overlay moves to match the new (x, y) coordinates
- AND the rectangle dimensions remain exactly 15×15 pixels

#### Scenario: Overlay updates on mode switch

- GIVEN the full image with overlay is displayed in "Centro automático" mode
- WHEN the user switches to "Manual (ingresar coordenadas)"
- THEN the overlay redraws at the manual coordinate position (default x=0, y=0)

### Requirement: Non-destructive overlay

The overlay MUST NOT modify the image data stored in `st.session_state.img_gray` or the `cropped` array used for filtering. The rectangle is drawn on a COPY of the BGR-converted image solely for display.

#### Scenario: Filter operates on unmodified crop

- GIVEN the full image is displayed with a red rectangle overlay
- WHEN the user clicks "Aplicar filtro"
- THEN the filter operates on the original 15×15 crop (not the overlaid image)
- AND the result matches the expected filter output for that crop region

### Requirement: UI placement

The full image with overlay MUST be positioned in the UI flow between the crop selection widgets and the filter controls, outside the results block.

#### Scenario: Layout order

- GIVEN an image is loaded
- WHEN the page renders
- THEN the element order is: image info → crop selection → full image with overlay → filter controls → apply button → results

## Validation Criteria

- [ ] Full image with red rectangle visible before filter application
- [ ] Rectangle position matches center crop coordinates in auto mode
- [ ] Rectangle follows manual X/Y coordinate changes
- [ ] Rectangle updates on mode switch without page reload
- [ ] Filter output is identical with and without overlay active
- [ ] All existing 30+ tests continue to pass
