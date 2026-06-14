"""pytest fixtures — programmatic numpy arrays (no file dependencies)."""

import numpy as np
import pytest


@pytest.fixture
def sample_bw():
    """Return a 100×100 random grayscale image (2-D uint8)."""
    return np.random.randint(0, 256, (100, 100), dtype=np.uint8)


@pytest.fixture
def sample_color():
    """Return a 100×100 colour image where all three channels differ."""
    r = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    g = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    b = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    return np.stack([r, g, b], axis=-1)


@pytest.fixture
def uniform_image():
    """Return a 15×15 image with a constant pixel value of 128."""
    return np.full((15, 15), 128, dtype=np.uint8)


@pytest.fixture
def edge_image():
    """Return a 15×15 image with a vertical edge (left dark, right light).

    Columns 0-7 are 0 (black), columns 8-14 are 255 (white).
    Useful for Sobel gradient detection tests.
    """
    img = np.zeros((15, 15), dtype=np.uint8)
    img[:, 8:] = 255
    return img
