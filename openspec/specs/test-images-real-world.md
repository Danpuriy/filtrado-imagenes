# Test Images — Real-World Specification

## Purpose

Add four new deterministic test image types to `generar_imagen_prueba()` that simulate real-world applications: medical X-ray, document scanning, industrial inspection, and satellite imagery. All existing test images MUST remain unchanged.

## Requirements

### Requirement: New image types added to `generar_imagen_prueba()`

The function `generar_imagen_prueba(tipo, size=200)` in `filtrado/core.py` MUST accept four new `tipo` values: `"rayos_x"`, `"documento"`, `"inspeccion"`, and `"satelital"`. Each MUST return a 200×200 `np.uint8` array. The existing keys (`gradiente`, `cuadros`, `circulos`, `uniforme`) MUST continue to work unchanged.

#### Scenario: Existing images unchanged

- GIVEN `generar_imagen_prueba("gradiente")` is called
- WHEN the function runs
- THEN it returns the same gradient pattern as before the change

### Requirement: `rayos_x` — Medical X-Ray simulation

The `"rayos_x"` type MUST produce a soft gradient background with pixel values in the ~30–80 range (lung-like tissue), a bright circular object of ~180 intensity, and salt-and-pepper noise at 2% probability.

#### Scenario: X-ray image structure

- GIVEN `generar_imagen_prueba("rayos_x")` is called
- THEN the returned array is 200×200 with dtype `np.uint8`
- AND the background pixels are in the range 30–80
- AND a roughly circular region near center has intensity ~180
- AND at least 1% of pixels differ from their neighbors (salt-and-pepper noise present)
- AND the function is deterministic (same output for same input parameters)

### Requirement: `documento` — Document scan simulation

The `"documento"` type MUST produce a light background of approximately 220 intensity with small dark rectangles (~0–30) scattered across the image to simulate text characters.

#### Scenario: Document image structure

- GIVEN `generar_imagen_prueba("documento")` is called
- THEN the returned array is 200×200 with dtype `np.uint8`
- AND the background pixels are ~220 ± 10
- AND there are multiple small rectangular dark regions (< 30 intensity) representing text
- AND the function is deterministic

### Requirement: `inspeccion` — Industrial crack inspection

The `"inspeccion"` type MUST produce a uniform mid-gray surface of ~128 intensity with a thin dark line (~30 intensity) simulating a crack.

#### Scenario: Inspection image structure

- GIVEN `generar_imagen_prueba("inspeccion")` is called
- THEN the returned array is 200×200 with dtype `np.uint8`
- AND the surface pixels are ~128 ± 2
- AND there is a contiguous thin dark line (~30) of width 1–3 pixels
- AND the function is deterministic

### Requirement: `satelital` — Satellite imagery simulation

The `"satelital"` type MUST produce four quadrants of different gray levels (40, 100, 160, 220) with additive gaussian noise.

#### Scenario: Satellite image structure

- GIVEN `generar_imagen_prueba("satelital")` is called
- THEN the returned array is 200×200 with dtype `np.uint8`
- AND the four quadrants have distinct base gray levels (40, 100, 160, 220)
- AND noise is present but the quadrant means differ by at least 50 between adjacent quadrants
- AND the function is deterministic for a fixed random seed

## Validation Criteria

- [ ] All 4 new types produce 200×200 `np.uint8` arrays without errors
- [ ] Each type produces visually distinct patterns matching their domain description
- [ ] Existing types (`gradiente`, `cuadros`, `circulos`, `uniforme`) produce identical output to before the change
- [ ] New test images appear in the Streamlit sidebar and render without errors
- [ ] All existing tests pass without modification
