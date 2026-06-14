"""Display utilities — matplotlib figures for image visualisation."""

import cv2
import matplotlib.pyplot as plt
import numpy as np


def show_histogram(img: np.ndarray, title: str = "") -> plt.Figure:
    """Return a matplotlib Figure with the pixel intensity distribution.

    Parameters
    ----------
    img : np.ndarray
        Grayscale image (2D array).
    title : str
        Optional title for the plot.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(img.ravel(), bins=256, range=(0, 256), color="gray", alpha=0.7)
    ax.set_xlabel("Intensidad de pixel")
    ax.set_ylabel("Frecuencia")
    ax.set_xlim(0, 255)
    if title:
        ax.set_title(title)
    fig.tight_layout()
    return fig


def show_digitalization_grid(img: np.ndarray) -> plt.Figure:
    """Return a matplotlib Figure with a pixel grid + numeric cell values.

    Each cell displays its pixel value.  Text colour is chosen automatically
    to contrast with the cell background (white on dark, black on light).
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    h, w = img.shape[:2]

    # Display the image
    ax.imshow(img, cmap="gray", interpolation="nearest")

    # Grid lines at pixel boundaries
    ax.set_xticks(np.arange(-0.5, w, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, h, 1), minor=True)
    ax.grid(True, which="minor", color="gray", linewidth=0.5)
    ax.tick_params(which="minor", length=0)

    # Overlay numeric values
    edge = isinstance(img.ravel()[0], (np.floating, float))
    for i in range(h):
        for j in range(w):
            val = img[i, j]
            text = f"{val:.1f}" if edge else str(val)
            colour = "white" if val < 128 else "black"
            ax.text(j, i, text, ha="center", va="center",
                    color=colour, fontsize=7)

    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    return fig


def show_matrix_text(img: np.ndarray, label: str = "Matriz") -> str:
    """Return a string representation of the pixel matrix, like the original notebook.

    Example output
    --------------
    F1: 120 121 119 118
    F2: 118 122 120 117
    ...
    """
    lines = [f"📊 {label}"]
    for i, fila in enumerate(img):
        # If float (raw edge result), show with 1 decimal; otherwise as integer
        if np.issubdtype(img.dtype, np.floating):
            vals = " ".join(f"{float(v):6.1f}" for v in fila)
        else:
            vals = " ".join(f"{int(v):3d}" for v in fila)
        lines.append(f"F{i+1}: {vals}")
    return "\n".join(lines)


def show_filter_comparison(
    original: np.ndarray,
    filtered: np.ndarray,
    title: str = "",
) -> plt.Figure:
    """Return a matplotlib Figure comparing *original* vs *filtered*.

    The figure contains a 2×2 grid:
      - top-left:   original image
      - top-right:  filtered image
      - bottom-left:  original histogram
      - bottom-right: filtered histogram
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # --- images ---
    axes[0, 0].imshow(original, cmap="gray", interpolation="nearest")
    axes[0, 0].set_title("Original")
    axes[0, 0].axis("off")

    axes[0, 1].imshow(filtered, cmap="gray", interpolation="nearest")
    axes[0, 1].set_title("Filtrada")
    axes[0, 1].axis("off")

    # --- histograms ---
    axes[1, 0].hist(original.ravel(), bins=256, range=(0, 256),
                    color="gray", alpha=0.7)
    axes[1, 0].set_title("Histograma — original")
    axes[1, 0].set_xlim(0, 255)

    axes[1, 1].hist(filtered.ravel(), bins=256, range=(0, 256),
                    color="gray", alpha=0.7)
    axes[1, 1].set_title("Histograma — filtrada")
    axes[1, 1].set_xlim(0, 255)

    if title:
        fig.suptitle(title)

    fig.tight_layout()
    return fig


def draw_crop_overlay(
    img: np.ndarray,
    x: int,
    y: int,
    size: int = 15,
) -> np.ndarray:
    """Return a COPY of *img* converted to BGR with a red rectangle overlay.

    The original *img* is never modified (non-destructive).
    """
    # Convert grayscale to BGR
    bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    # Draw red rectangle on the copy
    cv2.rectangle(bgr, (x, y), (x + size, y + size), color=(0, 0, 255), thickness=2)
    return bgr

