"""Streamlit web app — Image Filtering Pipeline.

Run with:
    streamlit run app.py
"""

import streamlit as st
import cv2
import numpy as np
from io import BytesIO

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
from filtrado.display import (
    show_digitalization_grid,
    show_filter_comparison,
    show_matrix_text,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Filtrado de Imágenes")

# ---------------------------------------------------------------------------
# Sidebar — dark mode toggle
# ---------------------------------------------------------------------------
dark_mode = st.sidebar.toggle("🌙 Modo oscuro", value=False)
if dark_mode:
    st.markdown("""
    <style>
    .stApp { background-color: #1e1e1e; color: #e0e0e0; }
    .stMarkdown, .stText, .stCaption, .stSubheader { color: #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.markdown("### 🎛️ Controles")

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
st.title("🎨 Filtrado de Imágenes")
st.markdown(
    "Cargue una imagen **JPG en blanco y negro** o use una imagen de prueba "
    "para aplicar filtros de procesamiento digital."
)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------
if "img_gray" not in st.session_state:
    st.session_state.img_gray = None
    st.session_state.img_source = None
    st.session_state.result = None
    st.session_state.raw = None
    st.session_state.filter_applied = None

# ---------------------------------------------------------------------------
# Sample images
# ---------------------------------------------------------------------------
st.sidebar.markdown("### 🖼️ Imágenes de prueba")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("📊 Gradiente"):
        st.session_state.img_gray = generar_imagen_prueba("gradiente")
        st.session_state.img_source = "prueba_gradiente"
        st.rerun()
    if st.button("🎯 Círculos"):
        st.session_state.img_gray = generar_imagen_prueba("circulos")
        st.session_state.img_source = "prueba_circulos"
        st.rerun()
with col2:
    if st.button("🏁 Cuadros"):
        st.session_state.img_gray = generar_imagen_prueba("cuadros")
        st.session_state.img_source = "prueba_cuadros"
        st.rerun()
    if st.button("⬜ Gris"):
        st.session_state.img_gray = generar_imagen_prueba("uniforme")
        st.session_state.img_source = "prueba_gris"
        st.rerun()

# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------
uploaded = st.sidebar.file_uploader(
    "O suba una imagen...",
    type=["jpg", "jpeg"],
    help="Solo imágenes JPG/JPEG en blanco y negro.",
)

if st.sidebar.button("🔄 Limpiar imagen", type="secondary"):
    st.session_state.img_gray = None
    st.session_state.img_source = None
    st.session_state.result = None
    st.session_state.raw = None
    st.session_state.filter_applied = None
    st.rerun()

# ---------------------------------------------------------------------------
# Decode image source
# ---------------------------------------------------------------------------
gray = None
img_source = st.session_state.img_source

if uploaded is not None:
    bytes_data = uploaded.getvalue()
    img_array = np.frombuffer(bytes_data, np.uint8)
    img_color = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if img_color is None:
        st.error("No se pudo decodificar la imagen. El archivo podría estar corrupto.")
        st.stop()

    is_valid, msg = validate_image(img_color)

    if not is_valid:
        if "color" in msg.lower():
            st.warning("⚠️ La imagen es a color. El programa funciona en blanco y negro.")
            convertir = st.checkbox("Convertir a blanco y negro automáticamente", value=True)
            if not convertir:
                st.error("Imagen rechazada. Solo se aceptan imágenes en blanco y negro.")
                st.stop()
            gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
            st.success("✅ Imagen convertida a blanco y negro exitosamente.")
        else:
            st.error(f"Imagen inválida: {msg}")
            st.stop()
    else:
        st.success("✅ Imagen válida — blanco y negro aceptado.")
        gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    st.session_state.img_gray = gray
    st.session_state.img_source = uploaded.name.split(".")[0]

elif st.session_state.img_gray is not None:
    gray = st.session_state.img_gray

else:
    st.info("👈 Usá una imagen de prueba en la barra lateral o subí un JPG.")
    st.stop()

# ---------------------------------------------------------------------------
# Image info panel
# ---------------------------------------------------------------------------
with st.expander("📋 Información de la imagen", expanded=False):
    cols_info = st.columns(4)
    with cols_info[0]:
        st.metric("Dimensiones", f"{gray.shape[1]}×{gray.shape[0]}")
    with cols_info[1]:
        st.metric("Valor mínimo", int(gray.min()))
    with cols_info[2]:
        st.metric("Valor máximo", int(gray.max()))
    with cols_info[3]:
        st.metric("Valor medio", f"{gray.mean():.1f}")

# ---------------------------------------------------------------------------
# Crop selection
# ---------------------------------------------------------------------------
st.markdown("### ✂️ Recorte")

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
# Kernel size & Filter selection
# ---------------------------------------------------------------------------
st.markdown("### 🔧 Filtro")

col_kernel, col_filter = st.columns([1, 2])
with col_kernel:
    kernel_size = st.slider(
        "Tamaño del kernel",
        min_value=3, max_value=15, value=3, step=2,
        help="Tamaño de la ventana del filtro (solo impares). "
             "Valores más grandes = efecto más fuerte.",
    )
with col_filter:
    filter_option = st.selectbox(
        "Seleccione un filtro:",
        ["Media", "Mediana", "Laplaciano", "Sobel"],
    )

is_edge = filter_option in ("Laplaciano", "Sobel")

# ---------------------------------------------------------------------------
# Apply button — stores everything in session_state
# ---------------------------------------------------------------------------
if st.button("🚀 Aplicar filtro", type="primary"):
    result_img = None
    raw_img = None

    if filter_option == "Media":
        result_img = mean_filter(cropped, kernel_size=kernel_size)
    elif filter_option == "Mediana":
        result_img = median_filter(cropped, kernel_size=kernel_size)
    elif filter_option == "Laplaciano":
        raw_img, result_img = laplacian_filter(cropped, kernel_size=kernel_size)
    else:
        raw_img, result_img = sobel_filter(cropped, kernel_size=kernel_size)

    st.session_state.result = result_img
    st.session_state.raw = raw_img
    st.session_state.filter_applied = filter_option
    st.rerun()

# ---------------------------------------------------------------------------
# Results display (from session_state — persists across reruns)
# ---------------------------------------------------------------------------
if st.session_state.result is not None:
    is_edge = st.session_state.filter_applied in ("Laplaciano", "Sobel")
    result_img = st.session_state.result
    raw_img = st.session_state.raw
    filter_name = st.session_state.filter_applied

    st.markdown("---")

    # -------- 1. Original display + digitalization + text matrix --------
    st.subheader("🖼️ Muestra 1 — Imagen original")
    orig_col1, orig_col2 = st.columns(2)
    with orig_col1:
        st.image(cropped, caption="Original", clamp=True, use_container_width=True)
    with orig_col2:
        fig_orig_dig = show_digitalization_grid(cropped)
        st.pyplot(fig_orig_dig)
        st.caption("Digitalización — matriz de píxeles")

    with st.expander("📄 Matriz numérica de la imagen original", expanded=False):
        st.code(show_matrix_text(cropped, "Original"), language="text")

    # -------- 2. Filter-specific displays --------
    if is_edge:
        # Raw matrix
        st.subheader(f"📊 Muestra 2 — Matriz resultante del filtrado ({filter_name})")
        mat_col1, mat_col2 = st.columns(2)
        with mat_col1:
            fig_raw = show_digitalization_grid(raw_img)
            st.pyplot(fig_raw)
            st.caption(f"Matriz cruda ({filter_name}) — valores float64")
        with mat_col2:
            fig_norm = show_digitalization_grid(result_img)
            st.pyplot(fig_norm)
            st.caption("Matriz re-escalada (0–255 — uint8)")

        with st.expander("📄 Matriz numérica del resultado (re-escalada)", expanded=False):
            st.code(show_matrix_text(result_img, f"Re-escalada — {filter_name}"), language="text")

        # Result image
        st.subheader("🖼️ Muestra 3 — Imagen resultante del filtrado")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.image(result_img,
                     caption=f"Filtro {filter_name} (kernel {kernel_size}×{kernel_size})",
                     clamp=True, use_container_width=True)
        with res_col2:
            fig_res_dig = show_digitalization_grid(result_img)
            st.pyplot(fig_res_dig)
            st.caption("Digitalización de la imagen resultante")
    else:
        # Smoothing filters
        st.subheader(f"🖼️ Muestra 2 — Imagen resultante ({filter_name})")
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.image(result_img,
                     caption=f"Filtro {filter_name} (kernel {kernel_size}×{kernel_size})",
                     clamp=True, use_container_width=True)
        with res_col2:
            fig_res_dig = show_digitalization_grid(result_img)
            st.pyplot(fig_res_dig)
            st.caption("Digitalización — matriz obtenida tras el filtro")

        with st.expander("📄 Matriz numérica del resultado", expanded=False):
            st.code(show_matrix_text(result_img, f"Resultado — {filter_name}"), language="text")

    # -------- 3. Comparison (Original vs Result) --------
    st.subheader("📈 Comparación — Original vs Filtrada")
    fig_comp = show_filter_comparison(
        cropped, result_img, title=f"Original vs {filter_name}"
    )
    st.pyplot(fig_comp)

    # -------- 4. Sidebar download --------
    _, result_bytes = cv2.imencode(".png", result_img)
    buf = BytesIO(result_bytes.tobytes())

    st.sidebar.markdown("### 💾 Descargar")
    st.sidebar.download_button(
        label="📥 Descargar imagen procesada",
        data=buf,
        file_name=f"{img_source}_filtrado_{filter_name.lower()}.png",
        mime="image/png",
    )
