"""Tests for filtrado.core — validation, cropping, and all 4 filters."""

import numpy as np
import pytest

from filtrado.core import (
    validate_image,
    crop_center,
    crop_manual,
    mean_filter,
    median_filter,
    laplacian_filter,
    sobel_filter,
    generar_imagen_prueba,
)


# ---------------------------------------------------------------------------
# validate_image
# ---------------------------------------------------------------------------

class TestValidateImage:
    def test_bw_single_channel_accepted(self, sample_bw):
        """A 2-D grayscale image MUST pass validation."""
        ok, msg = validate_image(sample_bw)
        assert ok, f"Expected valid, got: {msg}"
        assert msg == ""

    def test_color_rejected(self, sample_color):
        """A 3-channel image with differing channels MUST be rejected."""
        ok, msg = validate_image(sample_color)
        assert not ok
        assert "color" in msg.lower() or "colour" in msg.lower()

    def test_equal_channels_accepted(self):
        """A 3-channel image where R==G==B is effectively B&W — MUST pass."""
        channel = np.random.randint(0, 256, (30, 30), dtype=np.uint8)
        img = np.stack([channel, channel, channel], axis=-1)
        ok, msg = validate_image(img)
        assert ok, f"Expected valid, got: {msg}"

    def test_undersized_rejected(self):
        """Images smaller than 15×15 MUST be rejected."""
        img = np.random.randint(0, 256, (10, 14), dtype=np.uint8)
        ok, msg = validate_image(img)
        assert not ok
        assert "small" in msg.lower()

    def test_2d_undersized_rejected(self):
        """2-D single-channel images smaller than 15×15 MUST be rejected."""
        img = np.random.randint(0, 256, (5, 5), dtype=np.uint8)
        ok, msg = validate_image(img)
        assert not ok
        assert "small" in msg.lower()

    def test_bw_accepted_at_exact_minimum(self):
        """A 15×15 image is the minimum allowed — MUST pass."""
        img = np.zeros((15, 15), dtype=np.uint8)
        ok, msg = validate_image(img)
        assert ok, f"Expected valid, got: {msg}"

    def test_corrupted_none_rejected(self):
        """Simulate a corrupted image by passing a tiny invalid buffer."""
        with pytest.raises(Exception):
            # This should fail at cv2 level or be caught elsewhere
            validate_image(np.array([], dtype=np.uint8))


# ---------------------------------------------------------------------------
# Crop
# ---------------------------------------------------------------------------

class TestCrop:
    def test_center_crop_dimensions(self, sample_bw):
        """Center crop MUST return a 15×15 array."""
        cropped = crop_center(sample_bw, size=15)
        assert cropped.shape == (15, 15)

    def test_center_crop_exact_size(self):
        """Cropping a 15×15 image with size=15 MUST return the same array."""
        img = np.random.randint(0, 256, (15, 15), dtype=np.uint8)
        cropped = crop_center(img, size=15)
        assert np.array_equal(img, cropped)

    def test_center_crop_large_odd(self):
        """Center crop on an odd-dimension image works correctly."""
        img = np.random.randint(0, 256, (101, 101), dtype=np.uint8)
        cropped = crop_center(img, size=15)
        assert cropped.shape == (15, 15)

    def test_center_crop_position(self):
        """Known input: 100×100 → crop starts at pixel (42, 42)."""
        # Create an image where we can assert position
        img = np.zeros((100, 100), dtype=np.uint8)
        img[42:57, 42:57] = 255  # fill the target crop region
        cropped = crop_center(img, size=15)
        assert cropped.shape == (15, 15)
        # All pixels in the cropped region should be 255
        assert np.all(cropped == 255)

    def test_manual_crop_valid(self, sample_bw):
        """Manual crop at (10, 20) MUST return the correct slice."""
        cropped = crop_manual(sample_bw, x=10, y=20, size=15)
        assert cropped.shape == (15, 15)
        assert np.array_equal(cropped, sample_bw[20:35, 10:25])

    def test_manual_crop_oob_raises(self, sample_bw):
        """Out-of-bounds coordinates MUST raise ValueError."""
        with pytest.raises(ValueError, match="exceed|out of bounds|OOB"):
            crop_manual(sample_bw, x=90, y=50, size=15)

    def test_manual_crop_edge_valid(self, sample_bw):
        """Coordinates at the very edge (width-15, height-15) MUST work."""
        h, w = sample_bw.shape[:2]
        cropped = crop_manual(sample_bw, x=w - 15, y=h - 15, size=15)
        assert cropped.shape == (15, 15)


# ---------------------------------------------------------------------------
# Mean & Median filters
# ---------------------------------------------------------------------------

class TestMeanMedian:
    def test_mean_preserves_shape(self, sample_bw):
        result = mean_filter(sample_bw)
        assert result.shape == sample_bw.shape

    def test_mean_uniform_unchanged(self, uniform_image):
        result = mean_filter(uniform_image)
        # A uniform input stays uniform after averaging
        assert np.allclose(result, uniform_image, atol=1)

    def test_median_preserves_shape(self, sample_bw):
        result = median_filter(sample_bw)
        assert result.shape == sample_bw.shape

    def test_median_uniform_unchanged(self, uniform_image):
        result = median_filter(uniform_image)
        assert np.allclose(result, uniform_image, atol=1)

    def test_median_removes_salt_pepper(self):
        """Median filter MUST eliminate isolated extreme pixels."""
        img = np.full((15, 15), 128, dtype=np.uint8)
        img[7, 7] = 0     # salt
        img[3, 10] = 255  # pepper
        result = median_filter(img)
        # The noise pixels should be replaced by surrounding median
        assert abs(int(result[7, 7]) - 128) <= 2
        assert abs(int(result[3, 10]) - 128) <= 2

    def test_mean_smooths_extreme(self):
        """Mean filter MUST attenuate isolated extreme values."""
        img = np.full((15, 15), 128, dtype=np.uint8)
        img[7, 7] = 255
        result = mean_filter(img)
        assert result[7, 7] < 255


# ---------------------------------------------------------------------------
# Laplacian & Sobel filters
# ---------------------------------------------------------------------------

class TestLaplacian:
    def test_uniform_near_zero(self, uniform_image):
        """Uniform input → raw Laplacian MUST be near zero."""
        raw, norm = laplacian_filter(uniform_image)
        assert np.allclose(raw, 0, atol=1)

    def test_normalized_range(self, sample_bw):
        """Normalized output MUST be uint8 in [0, 255]."""
        raw, norm = laplacian_filter(sample_bw)
        assert norm.dtype == np.uint8
        assert norm.min() >= 0
        assert norm.max() <= 255

    def test_preserves_shape(self, sample_bw):
        raw, norm = laplacian_filter(sample_bw)
        assert raw.shape == sample_bw.shape
        assert norm.shape == sample_bw.shape

    def test_raw_is_float64(self, sample_bw):
        raw, _ = laplacian_filter(sample_bw)
        assert raw.dtype == np.float64

    def test_edge_high_values(self, edge_image):
        """Edges MUST produce higher absolute raw values than flat regions."""
        raw, norm = laplacian_filter(edge_image)
        # Values along the edge should be non-zero
        assert np.max(np.abs(raw)) > 10


class TestSobel:
    def test_uniform_near_zero(self, uniform_image):
        raw, norm = sobel_filter(uniform_image)
        assert np.allclose(raw, 0, atol=1)

    def test_normalized_range(self, sample_bw):
        raw, norm = sobel_filter(sample_bw)
        assert norm.dtype == np.uint8
        assert norm.min() >= 0
        assert norm.max() <= 255

    def test_preserves_shape(self, sample_bw):
        raw, norm = sobel_filter(sample_bw)
        assert raw.shape == sample_bw.shape
        assert norm.shape == sample_bw.shape

    def test_raw_is_float64(self, sample_bw):
        raw, _ = sobel_filter(sample_bw)
        assert raw.dtype == np.float64

    def test_vertical_edge_detected(self, edge_image):
        """A vertical edge MUST produce higher magnitude at the edge column."""
        raw, norm = sobel_filter(edge_image)
        # The edge column (col 8) should have higher values than flat cols
        edge_col = raw[:, 8]
        flat_col_left = raw[:, 4]
        assert np.mean(edge_col) > np.mean(flat_col_left)


# ---------------------------------------------------------------------------
# Nuevas imágenes de prueba
# ---------------------------------------------------------------------------

class TestGenerarImagenPruebaNuevas:
    def test_rayos_x_properties(self):
        img1 = generar_imagen_prueba("rayos_x")
        img2 = generar_imagen_prueba("rayos_x")
        assert img1.shape == (200, 200)
        assert img1.dtype == np.uint8
        # Determinism
        assert np.array_equal(img1, img2)
        
        # Rays X structure: soft gradient background (Tissue) ~30-80, bright circle ~180, salt-pepper noise
        # Since we have noise (0 and 255), we can check values
        # Let's check there's a circular/bright region of intensity ~180
        assert np.any((img1 >= 170) & (img1 <= 190))
        # Let's check there's tissue/background pixels in 30-80
        assert np.any((img1 >= 30) & (img1 <= 80))
        # Salt-and-pepper noise check (at least 1% should differ from neighbors or be 0/255)
        # Let's just verify some pixels are 0 or 255
        assert np.any(img1 == 0)
        assert np.any(img1 == 255)

    def test_documento_properties(self):
        img1 = generar_imagen_prueba("documento")
        img2 = generar_imagen_prueba("documento")
        assert img1.shape == (200, 200)
        assert img1.dtype == np.uint8
        # Determinism
        assert np.array_equal(img1, img2)
        
        # Light background ~220 +/- 10
        # Dark rectangles ~0-30
        # We assert most of the image is light, but some is very dark
        light_pixels = np.sum((img1 >= 210) & (img1 <= 230))
        dark_pixels = np.sum(img1 <= 30)
        assert light_pixels > 15000  # most of 40000 pixels
        assert dark_pixels > 500     # representing text

    def test_inspeccion_properties(self):
        img1 = generar_imagen_prueba("inspeccion")
        img2 = generar_imagen_prueba("inspeccion")
        assert img1.shape == (200, 200)
        assert img1.dtype == np.uint8
        # Determinism
        assert np.array_equal(img1, img2)
        
        # Surface is ~128 +/- 2
        # Dark diagonal line is ~30
        flat_pixels = np.sum((img1 >= 126) & (img1 <= 130))
        line_pixels = np.sum((img1 >= 20) & (img1 <= 40))
        assert flat_pixels > 35000
        assert line_pixels > 50

    def test_satelital_properties(self):
        img1 = generar_imagen_prueba("satelital")
        img2 = generar_imagen_prueba("satelital")
        assert img1.shape == (200, 200)
        assert img1.dtype == np.uint8
        # Determinism
        assert np.array_equal(img1, img2)
        
        # 4 quadrants: base levels 40, 100, 160, 220 + gaussian noise
        # Check mean of each quadrant is distinct
        q1 = img1[0:100, 0:100]
        q2 = img1[0:100, 100:200]
        q3 = img1[100:200, 0:100]
        q4 = img1[100:200, 100:200]
        
        means = [np.mean(q) for q in (q1, q2, q3, q4)]
        # Sort means and verify they correspond to around 40, 100, 160, 220
        means.sort()
        assert abs(means[0] - 40) < 10
        assert abs(means[1] - 100) < 10
        assert abs(means[2] - 160) < 10
        assert abs(means[3] - 220) < 10

    def test_existing_types_unchanged(self):
        # Existing types (gradiente, cuadros, circulos) shouldn't be altered
        img_grad = generar_imagen_prueba("gradiente")
        assert img_grad.shape == (200, 200)
        # Check horizontal gradient properties
        assert np.array_equal(img_grad[0], np.linspace(0, 255, 200, dtype=np.uint8))
        
        img_cuadros = generar_imagen_prueba("cuadros")
        assert img_cuadros.shape == (200, 200)
        assert img_cuadros[0, 0] == 255
        assert img_cuadros[0, 25] == 0

