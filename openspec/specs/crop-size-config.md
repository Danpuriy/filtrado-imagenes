# Crop Size Config Specification

## Purpose

Allow the user to configure the square crop size via a sidebar slider. The size must be odd, bounded by 3 and min(image height, image width), with reactive validation and boundary updates for manual coordinate inputs.

## Requirements

### Requirement: Sidebar slider for crop size

The system MUST provide a sidebar slider labeled "Tamaño de recorte" with range 3 to max_odd (inclusive), step 2 (odd only), default 15. Where max_odd = min(image_height, image_width) if odd, else min(image_height, image_width) - 1.

#### Scenario: Slider appears with correct range and default

- GIVEN an image is loaded with dimensions 200×150
- WHEN the sidebar renders
- THEN a slider "Tamaño de recorte" appears with min=3, max=149, step=2, default=15

#### Scenario: Slider max clamps to odd ≤ min(H,W)

- GIVEN an image is loaded with dimensions 50×50
- WHEN the slider max is computed
- THEN max = 49 (largest odd ≤ 50)

#### Scenario: Slider max clamps to 3 for tiny images

- GIVEN an image is loaded with dimensions 2×100
- WHEN the slider max is computed
- THEN max = 3 (clamped to minimum valid odd size)

### Requirement: Crop size validation in core

The system MUST validate in `crop_manual(gray, x, y, size)` that `size ≤ min(h, w)`. If validation fails, a ValueError MUST be raised with a descriptive message.

#### Scenario: crop_manual rejects oversized crop

- GIVEN a 100×80 grayscale image
- WHEN crop_manual is called with size=90
- THEN ValueError is raised ("crop size 90 exceeds image min dimension 80")

#### Scenario: crop_manual accepts valid size at boundary

- GIVEN a 100×80 grayscale image
- WHEN crop_manual is called with size=79
- THEN no error is raised and crop is extracted

### Requirement: Center auto mode uses dynamic crop size

The system MUST pass the selected `crop_size` to `crop_center(gray, size=crop_size)` when mode is "Centro automático". The center coordinates MUST be computed for the given size.

#### Scenario: Center crop uses selected size

- GIVEN crop mode is "Centro automático" and crop_size=21
- WHEN the overlay and crop are computed
- THEN crop_center is called with size=21
- AND the extracted crop is 21×21 pixels

### Requirement: Manual mode uses dynamic crop size with reactive X/Y bounds

The system MUST pass the selected `crop_size` to `crop_manual(gray, x, y, size=crop_size)` when mode is "Manual". The maximum X coordinate MUST be `w - crop_size`, maximum Y MUST be `h - crop_size`. These bounds MUST update reactively when the crop size slider changes.

#### Scenario: Manual X max updates on crop size change

- GIVEN image width=200, crop_size=15
- WHEN user changes crop_size to 21
- THEN X input max updates from 185 to 179

#### Scenario: Manual Y max updates on crop size change

- GIVEN image height=150, crop_size=15
- WHEN user changes crop_size to 31
- THEN Y input max updates from 135 to 119

#### Scenario: Manual crop uses selected size

- GIVEN crop mode is "Manual", crop_size=21, x=10, y=20
- WHEN the crop is computed
- THEN crop_manual is called with size=21
- AND the extracted crop is 21×21 pixels at (10,20)

### Requirement: Filter operates on selected crop size

The system MUST apply the frequency filter to the cropped region using the user-selected `crop_size`. The FFT and all filter operations MUST use the dynamically sized crop.

#### Scenario: Filter output dimensions match crop size

- GIVEN crop_size=21, any filter selected
- WHEN "Aplicar filtro" is clicked
- THEN the filtered result is 21×21 pixels

## Validation Criteria

- [ ] Slider appears with odd-only range, default 15
- [ ] Slider max = largest odd ≤ min(H,W)
- [ ] Center mode extracts crop of selected size
- [ ] Manual mode X/Y max values update reactively on size change
- [ ] Manual mode extracts crop of selected size at given coordinates
- [ ] crop_manual raises ValueError if size > min(h,w)
- [ ] Filter operates on selected crop size
- [ ] All existing tests pass (default 15 unchanged)