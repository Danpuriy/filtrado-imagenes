"""Streamlit web app — Image Filtering Pipeline.

Run with:
    streamlit run app.py
"""

import streamlit as st
import cv2
import numpy as np

from filtrado.core import (
    validate_image,
    crop_center,
    crop_manual,
    mean_filter,
    median_filter,
    laplacian_filter,
    sobel_filter,
)
from filtrado.display import (
    show_digitalization_grid,
    show_filter_comparison,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Filtrado de Imágenes")

st.title("Filtrado de Imágenes")
st.markdown(
    "Cargue una imagen **JPG en blanco y negro** para aplicar filtros "
    "de procesamiento digital. El pipeline valida, recorta y filtra "
    "la imagen mostrando la matriz de píxeles y su digitalización."
)

# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------
uploaded = st.file_uploader(
    "Seleccione una imagen...",
    type=["jpg", "jpeg"],
    help="Solo imágenes JPG/JPEG en blanco y negro.",
)

if uploaded is None:
    st.info("Sube una imagen JPG para comenzar.")
    st.stop()

# Decode bytes → OpenCV array
bytes_data = uploaded.getvalue()
img_array = np.frombuffer(bytes_data, np.uint8)
img_color = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

if img_color is None:
    st.error("No se pudo decodificar la imagen. El archivo podría estar corrupto.")
    st.stop()

# ---------------------------------------------------------------------------
# Validate
# ---------------------------------------------------------------------------
is_valid, msg = validate_image(img_color)
if not is_valid:
    st.error(f"Imagen inválida: {msg}")
    st.stop()

st.success("Imagen válida — blanco y negro aceptado.")

# Convert validated image to grayscale for processing
gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------
# Crop selection
# ---------------------------------------------------------------------------
st.markdown("### Recorte")

crop_option = st.radio(
    "Seleccione modo de recorte:",
    ["Imagen completa", "Recorte 15×15 (centro)", "Recorte 15×15 (manual)"],
    horizontal=True,
)

if crop_option == "Imagen completa":
    cropped = gray
elif crop_option == "Recorte 15×15 (centro)":
    cropped = crop_center(gray)
else:
    col1, col2 = st.columns(2)
    max_x = max(0, gray.shape[1] - 15)
    max_y = max(0, gray.shape[0] - 15)
    with col1:
        x = st.number_input("X (columna)", min_value=0, max_value=max_x, value=0)
    with col2:
        y = st.number_input("Y (fila)", min_value=0, max_value=max_y, value=0)
    try:
        cropped = crop_manual(gray, int(x), int(y))
    except ValueError as e:
        st.error(str(e))
        st.stop()

st.caption(f"Dimensión final: {cropped.shape[1]}×{cropped.shape[0]} píxeles")

# ---------------------------------------------------------------------------
# Filter selection
# ---------------------------------------------------------------------------
st.markdown("### Filtro")

filter_option = st.selectbox(
    "Seleccione un filtro:",
    ["Media", "Mediana", "Laplaciano", "Sobel"],
)

is_edge = filter_option in ("Laplaciano", "Sobel")

# ---------------------------------------------------------------------------
# Process
# ---------------------------------------------------------------------------
if st.button("Aplicar filtro", type="primary"):
    # -------- Original display (same for all filter types) --------
    st.markdown("---")
    st.subheader("Imagen original")
    orig_col1, orig_col2 = st.columns(2)
    with orig_col1:
        st.image(cropped, caption="Original", clamp=True, use_container_width=True)
    with orig_col2:
        fig_orig_dig = show_digitalization_grid(cropped)
        st.pyplot(fig_orig_dig)
        st.caption("Digitalización — matriz de píxeles")

    # -------- Apply the selected filter --------
    if filter_option == "Media":
        result = mean_filter(cropped)
        raw = None
    elif filter_option == "Mediana":
        result = median_filter(cropped)
        raw = None
    elif filter_option == "Laplaciano":
        raw, result = laplacian_filter(cropped)
    else:  # Sobel
        raw, result = sobel_filter(cropped)

    # -------- Results display --------
    if is_edge:
        # -- Edge filters (Laplacian / Sobel): show matrices first --
        st.subheader("Matrices del filtrado")
        mat_col1, mat_col2 = st.columns(2)
        with mat_col1:
            fig_raw = show_digitalization_grid(raw)
            st.pyplot(fig_raw)
            st.caption("Matriz resultante del filtrado (raw — float64)")
        with mat_col2:
            fig_norm = show_digitalization_grid(result)
            st.pyplot(fig_norm)
            st.caption("Matriz re-escalada (0–255 — uint8)")

        st.subheader("Imagen resultante")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.image(result, caption=f"Filtro {filter_option}",
                     clamp=True, use_container_width=True)
        with res_col2:
            fig_res_dig = show_digitalization_grid(result)
            st.pyplot(fig_res_dig)
            st.caption("Digitalización de la imagen resultante")
    else:
        # -- Smoothing filters (Mean / Median) --
        st.subheader("Imagen resultante")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.image(result, caption=f"Filtro {filter_option}",
                     clamp=True, use_container_width=True)
        with res_col2:
            fig_res_dig = show_digitalization_grid(result)
            st.pyplot(fig_res_dig)
            st.caption("Digitalización — matriz obtenida tras el filtro")

    # -------- Comparison (always shown) --------
    st.subheader("Comparación")
    fig_comp = show_filter_comparison(
        cropped, result, title=f"Original vs {filter_option}"
    )
    st.pyplot(fig_comp)
