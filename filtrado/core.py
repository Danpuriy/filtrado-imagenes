"""Core image filtering operations — pure functions that receive/return np.ndarray."""

import cv2
import numpy as np


def generar_imagen_prueba(tipo: str = "gradiente", size: int = 200) -> np.ndarray:
    """Genera una imagen de prueba en escala de grises para probar la app."""
    if tipo == "gradiente":
        # Gradiente horizontal
        return np.tile(np.linspace(0, 255, size, dtype=np.uint8), (size, 1))
    elif tipo == "cuadros":
        # Patrón de tablero de ajedrez
        img = np.zeros((size, size), dtype=np.uint8)
        bloque = size // 8
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    img[i*bloque:(i+1)*bloque, j*bloque:(j+1)*bloque] = 255
        return img
    elif tipo == "circulos":
        # Círculos concéntricos
        Y, X = np.ogrid[:size, :size]
        center = size // 2
        dist = np.sqrt((X - center)**2 + (Y - center)**2)
        return (np.sin(dist * 0.1) * 127 + 128).astype(np.uint8)
    else:
        # Imagen uniforme gris
        return np.full((size, size), 128, dtype=np.uint8)


def validate_image(img: np.ndarray) -> tuple[bool, str]:
    """Validate image is B&W (single-channel or equal RGB) and ≥ 15×15.

    Returns
    -------
    (is_valid, error_msg)
        is_valid is True when the image passes all checks.
        error_msg describes the rejection reason when is_valid is False.
    """
    # --- size check ---
    if img.shape[0] < 15 or img.shape[1] < 15:
        return (
            False,
            f"Image too small: {img.shape[1]}×{img.shape[0]}. "
            f"Minimum size is 15×15 pixels.",
        )

    # --- B&W check ---
    if img.ndim == 2:
        # Single-channel grayscale — always B&W
        return True, ""

    if img.ndim == 3 and img.shape[2] >= 3:
        # Multi-channel — all channels must be identical
        if (
            np.array_equal(img[:, :, 0], img[:, :, 1])
            and np.array_equal(img[:, :, 0], img[:, :, 2])
        ):
            return True, ""

        return (
            False,
            "Color image detected. Only black-and-white (B&W) images are accepted. "
            "Please upload a grayscale JPG with all channels equal.",
        )

    return False, f"Unsupported image format with ndim={img.ndim}."


def crop_center(img: np.ndarray, size: int = 15) -> np.ndarray:
    """Extract a centered *size* × *size* crop from *img*.

    Handles odd and even dimensions gracefully.  The centre coordinate is
    computed as ``(dim - 1) // 2`` so that the spec's 100 × 100 example
    produces a crop starting at pixel (42, 42).
    """
    h, w = img.shape[:2]
    half = size // 2
    cy, cx = (h - 1) // 2, (w - 1) // 2

    y_start = cy - half
    y_end = y_start + size
    x_start = cx - half
    x_end = x_start + size

    return img[y_start:y_end, x_start:x_end]


def crop_manual(
    img: np.ndarray, x: int, y: int, size: int = 15
) -> np.ndarray:
    """Extract a *size* × *size* crop from *img* starting at pixel (x, y).

    Raises
    ------
    ValueError
        If the requested region extends beyond the image boundaries.
    """
    h, w = img.shape[:2]
    if x + size > w or y + size > h:
        raise ValueError(
            f"Crop region ({size}×{size}) at ({x},{y}) exceeds image "
            f"bounds ({w}×{h})."
        )
    return img[y : y + size, x : x + size]


def mean_filter(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Apply a mean (averaging) filter with configurable kernel size.

    Returns an array of the same shape and dtype as the input.
    """
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    return cv2.blur(img, (k, k))


def median_filter(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
    """Apply a median filter with configurable kernel size.

    Returns an array of the same shape and dtype as the input.
    """
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    return cv2.medianBlur(img, k)


def laplacian_filter(img: np.ndarray, kernel_size: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Apply Laplacian edge detection with configurable kernel size.

    Returns
    -------
    (raw, normalized)
        raw — cv2.Laplacian result as float64 (can contain negative values).
        normalized — rescaled to [0, 255] range as uint8.
    """
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    raw = cv2.Laplacian(img, cv2.CV_64F, ksize=k)
    normalized = cv2.normalize(raw, None, 0, 255, cv2.NORM_MINMAX)
    normalized = normalized.astype(np.uint8)
    return raw, normalized


def sobel_filter(img: np.ndarray, kernel_size: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Apply Sobel edge detection (combined XY magnitude) with configurable kernel size.

    Returns
    -------
    (raw, normalized)
        raw — combined gradient magnitude as float64.
        normalized — rescaled to [0, 255] range as uint8.
    """
    k = kernel_size if kernel_size % 2 == 1 else kernel_size + 1
    grad_x = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=k)
    grad_y = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=k)
    raw = cv2.magnitude(grad_x, grad_y)
    normalized = cv2.normalize(raw, None, 0, 255, cv2.NORM_MINMAX)
    normalized = normalized.astype(np.uint8)
    return raw, normalized
