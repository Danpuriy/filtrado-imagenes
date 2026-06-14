import numpy as np
import pytest
from filtrado.display import draw_crop_overlay

def test_draw_crop_overlay_basic():
    """Verify that draw_crop_overlay returns a BGR image of correct shape and dtype,

    and does not mutate the original image.
    """
    img = np.zeros((100, 120), dtype=np.uint8)
    img_copy = img.copy()

    x, y, size = 20, 30, 15
    output = draw_crop_overlay(img, x, y, size=size)

    # Correct shape (H x W x 3) and dtype
    assert output.shape == (100, 120, 3)
    assert output.dtype == np.uint8

    # Original image is NOT modified
    assert np.array_equal(img, img_copy)

    # Some pixels on the rectangle border must be red (0, 0, 255)
    # OpenCV's cv2.rectangle(img, (x, y), (x+size, y+size), color=(0,0,255), thickness=2)
    # top line: y, column from x to x+size
    # bottom line: y+size, column from x to x+size
    # left line: x, row from y to y+size
    # right line: x+size, row from y to y+size
    assert np.array_equal(output[y, x], [0, 0, 255])
    assert np.array_equal(output[y + size, x + size], [0, 0, 255])
    assert np.array_equal(output[y, x + size], [0, 0, 255])
    assert np.array_equal(output[y + size, x], [0, 0, 255])

    # A pixel far away should remain unchanged (grayscale converted to BGR, so all channels equal)
    assert output[0, 0, 0] == img[0, 0]
    assert output[0, 0, 1] == img[0, 0]
    assert output[0, 0, 2] == img[0, 0]

def test_draw_crop_overlay_different_coords():
    """Verify draw_crop_overlay with different dimensions, coordinates, and size."""
    img = np.ones((80, 80), dtype=np.uint8) * 100
    x, y, size = 5, 12, 30
    output = draw_crop_overlay(img, x, y, size=size)

    assert output.shape == (80, 80, 3)
    # Check corners of the rectangle
    assert np.array_equal(output[y, x], [0, 0, 255])
    assert np.array_equal(output[y + size, x + size], [0, 0, 255])
    assert np.array_equal(output[y, x + size], [0, 0, 255])
    assert np.array_equal(output[y + size, x], [0, 0, 255])
    
    # Far away pixel is converted to BGR correctly (value remains 100)
    assert np.array_equal(output[0, 0], [100, 100, 100])


def test_draw_crop_overlay_dynamic_size():
    """Verify draw_crop_overlay uses dynamic size parameter (not hardcoded 15)."""
    img = np.ones((100, 100), dtype=np.uint8) * 100
    
    # Test with size=21 (different from default 15)
    x, y, size = 10, 15, 21
    output = draw_crop_overlay(img, x, y, size=size)
    
    assert output.shape == (100, 100, 3)
    # Check corners of the rectangle at the dynamic size
    assert np.array_equal(output[y, x], [0, 0, 255])
    assert np.array_equal(output[y + size, x + size], [0, 0, 255])
    assert np.array_equal(output[y, x + size], [0, 0, 255])
    assert np.array_equal(output[y + size, x], [0, 0, 255])
    
    # Verify the rectangle is exactly size x size
    # With thickness=2, check a point well inside the rectangle (should be grayscale, not red)
    # Interior starts at y+2, x+2 due to border thickness
    assert not np.array_equal(output[y + 2, x + 2], [0, 0, 255])
    # Verify interior has the correct grayscale value converted to BGR
    assert np.array_equal(output[y + 2, x + 2], [100, 100, 100])

def test_draw_crop_overlay_size_3():
    """Verify draw_crop_overlay works with minimum size=3."""
    img = np.ones((20, 20), dtype=np.uint8) * 50
    x, y, size = 2, 2, 3
    output = draw_crop_overlay(img, x, y, size=size)
    
    assert output.shape == (20, 20, 3)
    assert np.array_equal(output[y, x], [0, 0, 255])
    assert np.array_equal(output[y + size, x + size], [0, 0, 255])

