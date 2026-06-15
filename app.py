"""Streamlit web app — Image Filtering Pipeline.

Run with:
    streamlit run app.py
"""

import streamlit as st
import cv2
import numpy as np
from io import BytesIO
import sys

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
    show_matrix_text,
    draw_crop_overlay,
)

# ---------------------------------------------------------------------------
# S1: st.set_page_config — MUST be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Filtrado de Imágenes")

# ---------------------------------------------------------------------------
# S2: Session state init — 5 keys, all → None
# ---------------------------------------------------------------------------
for key in ("img_gray", "img_source", "result", "raw", "filter_applied"):
    if key not in st.session_state:
        st.session_state[key] = None

# Pre-compute max_odd from session_state for the sidebar crop-size slider.
# On cold start the guard (S6) stops before the slider; on warm reruns the
# image is already in session_state so we get the real dimensions.
if st.session_state.img_gray is not None:
    _h, _w = st.session_state.img_gray.shape[:2]
    _min_dim = min(_h, _w)
    _max_odd = _min_dim if _min_dim % 2 == 1 else _min_dim - 1
    _max_odd = max(3, _max_odd)
else:
    _max_odd = 15  # placeholder — cold start guard stops before slider use

# ---------------------------------------------------------------------------
# S3: SIDEBAR — contiguous block (all st.sidebar calls in one place)
# ---------------------------------------------------------------------------

# Dark mode toggle
dark_mode = st.sidebar.toggle("🌙 Modo oscuro", value=False)
if dark_mode:
    st.markdown(
        """<style>
        .stApp { background-color: #1e1e1e; color: #e0e0e0; }
        .stMarkdown, .stText, .stCaption, .stSubheader { color: #e0e0e0; }
        </style>""",
        unsafe_allow_html=True,
    )

st.sidebar.markdown("### 🎛️ Controles")

# --- Test images (8 buttons, 2×2 × 2) ---
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
    if st.button("🩻 Rayos X"):
        st.session_state.img_gray = generar_imagen_prueba("rayos_x")
        st.session_state.img_source = "prueba_rayos_x"
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
    if st.button("📄 Documento"):
        st.session_state.img_gray = generar_imagen_prueba("documento")
        st.session_state.img_source = "prueba_documento"
        st.rerun()

col3, col4 = st.sidebar.columns(2)
with col3:
    if st.button("🔍 Inspección"):
        st.session_state.img_gray = generar_imagen_prueba("inspeccion")
        st.session_state.img_source = "prueba_inspeccion"
        st.rerun()
with col4:
    if st.button("🛰️ Satelital"):
        st.session_state.img_gray = generar_imagen_prueba("satelital")
        st.session_state.img_source = "prueba_satelital"
        st.rerun()

# --- File upload ---
uploaded = st.sidebar.file_uploader(
    "O suba una imagen...",
    type=["jpg", "jpeg"],
    help="Solo imágenes JPG/JPEG en blanco y negro.",
)

# --- Clear button (resets all 5 keys) ---
if st.sidebar.button("🔄 Limpiar imagen", type="secondary"):
    for key in ("img_gray", "img_source", "result", "raw", "filter_applied"):
        st.session_state[key] = None
    st.rerun()

# --- Crop size slider (uses max_odd computed from session_state above) ---
crop_size = st.sidebar.slider(
    "Tamaño de recorte",
    min_value=3,
    max_value=_max_odd,
    value=min(15, _max_odd),
    step=2,
    help="Tamaño del recorte cuadrado (solo impares). "
         "El máximo es el impar más grande ≤ min(alto, ancho).",
)

# --- Download button (conditional on result) ---
if st.session_state.result is not None:
    _, result_bytes = cv2.imencode(".png", st.session_state.result)
    buf = BytesIO(result_bytes.tobytes())
    filter_name = st.session_state.filter_applied or "desconocido"
    st.sidebar.download_button(
        label="📥 Descargar imagen procesada",
        data=buf,
        file_name=f"{st.session_state.img_source or 'None'}_filtrado_{filter_name.lower()}.png",
        mime="image/png",
    )

# --- Sidebar branding — always visible ---
st.sidebar.markdown("---")
st.sidebar.caption("MA475 • UPC • 2026-S6")
with st.sidebar.expander("ℹ️ Créditos del proyecto", expanded=False):
    st.markdown("**Curso:** MA475 - Matemática Computacional")
    st.markdown("**Institución:** UPC - Universidad Peruana de Ciencias Aplicadas")
    st.markdown("**Integrantes:**")
    st.markdown("- Chavez Giraldo, Andrei Gabriel")
    st.markdown("- Romero Veliz, Matthias Alonso")
    st.markdown("- Escalante Rojas, Rogger Junior")
    st.markdown("- Zea Diaz, Jesús Enrique")
    st.markdown("- Rodriguez Espinoza, Daniel Kevin")
    st.markdown("**Profesor:** Jesús Manuel Acosta Neyra")
    st.markdown("**Período:** 2026 (Semana 6 / primera revisión)")

# ---------------------------------------------------------------------------
# S4: Title + course branding
# ---------------------------------------------------------------------------
st.title("🎨 Filtrado de Imágenes")
st.markdown("**MA475 • UPC • 2026-S6**")
st.markdown(
    "Cargue una imagen **JPG en blanco y negro** o use una imagen de prueba "
    "para aplicar filtros de procesamiento digital."
)

# ---------------------------------------------------------------------------
# S5: Image decode — upload overrides session_state
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

# ---------------------------------------------------------------------------
# S6: Cold start guard — st.stop() + sys.exit(0)
# ---------------------------------------------------------------------------
if gray is None:
    st.info("👈 Usá una imagen de prueba en la barra lateral o subí un JPG.")
    st.stop()
    sys.exit(0)  # non-Streamlit fallback

# ---------------------------------------------------------------------------
# Image dimensions (after guard: gray is guaranteed not None)
# ---------------------------------------------------------------------------
h, w = gray.shape[:2]

# ---------------------------------------------------------------------------
# S7: Image info expander
# ---------------------------------------------------------------------------
with st.expander("📋 Información de la imagen", expanded=False):
    cols_info = st.columns(4)
    with cols_info[0]:
        st.metric("Dimensiones", f"{w}×{h}")
    with cols_info[1]:
        st.metric("Valor mínimo", int(gray.min()))
    with cols_info[2]:
        st.metric("Valor máximo", int(gray.max()))
    with cols_info[3]:
        st.metric("Valor medio", f"{gray.mean():.1f}")

# ---------------------------------------------------------------------------
# S8: Crop selection + overlay preview — BEFORE filter results
# ---------------------------------------------------------------------------
st.markdown(f"### ✂️ Recorte {crop_size}×{crop_size}")

crop_option = st.radio(
    "Seleccione modo de recorte:",
    ["Centro automático", "Manual (ingresar coordenadas)"],
    horizontal=True,
)

if crop_option == "Centro automático":
    cropped = crop_center(gray, size=crop_size)
else:
    max_x = max(0, w - crop_size)
    max_y = max(0, h - crop_size)
    coord_col1, coord_col2 = st.columns(2)
    with coord_col1:
        x = st.number_input("X (columna)", min_value=0, max_value=max_x, value=0)
    with coord_col2:
        y = st.number_input("Y (fila)", min_value=0, max_value=max_y, value=0)
    try:
        cropped = crop_manual(gray, int(x), int(y), size=crop_size)
    except ValueError as e:
        st.error(str(e))
        st.stop()

st.caption(f"Recorte de {cropped.shape[1]}×{cropped.shape[0]} píxeles listo")

# Crop overlay preview — draws red rectangle on a COPY (non-destructive)
st.markdown("### 🖼️ Vista previa del recorte")
if crop_option == "Centro automático":
    cy, cx = (h - 1) // 2, (w - 1) // 2
    half = crop_size // 2
    crop_x = cx - half
    crop_y = cy - half
else:
    crop_x = int(x)
    crop_y = int(y)

overlay_bgr = draw_crop_overlay(gray, crop_x, crop_y, size=crop_size)
st.image(
    overlay_bgr,
    caption=f"Imagen completa con recorte (rectángulo rojo = zona {crop_size}×{crop_size})",
    clamp=True,
    width="stretch",
)

# ---------------------------------------------------------------------------
# S9: Filter controls + apply + results (SINGLE copy — NO duplication)
# ---------------------------------------------------------------------------
st.markdown("### 🔧 Filtro")

col_kernel, col_filter = st.columns([1, 2])
with col_kernel:
    kernel_size = st.slider(
        "Tamaño del kernel",
        min_value=3,
        max_value=15,
        value=3,
        step=2,
        help="Tamaño de la ventana del filtro (solo impares). "
             "Valores más grandes = efecto más fuerte.",
    )
with col_filter:
    filter_option = st.selectbox(
        "Seleccione un filtro:",
        ["Media", "Mediana", "Laplaciano", "Sobel"],
    )

is_edge = filter_option in ("Laplaciano", "Sobel")

# --- Apply button — stores everything in session_state ---
if st.button("🚀 Aplicar filtro", type="primary"):
    if filter_option == "Media":
        result_img = mean_filter(cropped, kernel_size=kernel_size)
        raw_img = None
    elif filter_option == "Mediana":
        result_img = median_filter(cropped, kernel_size=kernel_size)
        raw_img = None
    elif filter_option == "Laplaciano":
        raw_img, result_img = laplacian_filter(cropped, kernel_size=kernel_size)
    else:
        raw_img, result_img = sobel_filter(cropped, kernel_size=kernel_size)

    st.session_state.result = result_img
    st.session_state.raw = raw_img
    st.session_state.filter_applied = filter_option
    st.rerun()

# --- Results display (SINGLE block, from session_state) ---
if st.session_state.result is not None:
    is_edge = st.session_state.filter_applied in ("Laplaciano", "Sobel")
    result_img = st.session_state.result
    raw_img = st.session_state.raw
    filter_name = st.session_state.filter_applied

    st.markdown("---")

    # -------- Original image + digitalization + matrix (always) --------
    st.subheader("🖼️ Imagen original y recorte digitalizado")
    orig_col1, orig_col2 = st.columns(2)
    with orig_col1:
        st.image(gray, caption="Imagen Original (completa)", clamp=True, width="stretch")
    with orig_col2:
        st.image(cropped, caption=f"Recorte {cropped.shape[1]}×{cropped.shape[0]}", clamp=True, width="stretch")

    st.markdown("---")
    dig_col1, dig_col2 = st.columns(2)
    with dig_col1:
        fig_orig_dig = show_digitalization_grid(cropped)
        st.pyplot(fig_orig_dig)
        st.caption("Digitalización del recorte — matriz de píxeles")
    with dig_col2:
        st.markdown("**Matriz numérica del recorte:**")
        st.code(show_matrix_text(cropped, "Recorte"), language="text")

    # -------- Per filter: exact PDF layout --------
    if is_edge:
        # Laplaciano / Sobel — Figura 4 del PDF: 2×3 grid
        st.subheader(f"📊 Filtro {filter_name} — matriz resultante y re-escalado")
        edge_col1, edge_col2, edge_col3 = st.columns(3)
        with edge_col1:
            fig_dig = show_digitalization_grid(cropped)
            st.pyplot(fig_dig)
            st.caption("Digitalización Inicial")
        with edge_col2:
            fig_raw = show_digitalization_grid(raw_img)
            st.pyplot(fig_raw)
            st.caption("Matriz Resultante del Filtrado")
        with edge_col3:
            fig_norm = show_digitalization_grid(result_img)
            st.pyplot(fig_norm)
            st.caption("Matriz Re-escalada (0–255)")

        # Second row: text matrices + result image
        edge2_col1, edge2_col2, edge2_col3 = st.columns(3)
        with edge2_col1:
            st.markdown("**Matriz numérica inicial:**")
            st.code(show_matrix_text(cropped, "Inicial"), language="text")
        with edge2_col2:
            st.markdown("**Matriz numérica resultante (re-escalada):**")
            st.code(show_matrix_text(result_img, f"Re-escalada — {filter_name}"), language="text")
        with edge2_col3:
            st.image(result_img, caption=f"Imagen Resultante — {filter_name}", clamp=True, width="stretch")

        # Third row: result digitalization
        st.markdown("---")
        st.subheader("📈 Digitalización Resultante")
        res_dig_col1, res_dig_col2 = st.columns(2)
        with res_dig_col1:
            fig_res_dig = show_digitalization_grid(result_img)
            st.pyplot(fig_res_dig)
            st.caption("Digitalización Resultante")
        with res_dig_col2:
            st.markdown("**Matriz numérica resultante:**")
            st.code(show_matrix_text(result_img, f"Resultante — {filter_name}"), language="text")

    else:
        # Media / Mediana — Figura 3 del PDF: 2×2 grid + comparación
        st.subheader(f"📊 Filtro {filter_name} — imagen resultante")
        sm_col1, sm_col2 = st.columns(2)
        with sm_col1:
            st.image(result_img, caption=f"Imagen Resultante — {filter_name}", clamp=True, width="stretch")
        with sm_col2:
            fig_res_dig = show_digitalization_grid(result_img)
            st.pyplot(fig_res_dig)
            st.caption("Digitalización Resultante")

        # Matrices textuales: inicial vs resultante
        st.markdown("---")
        st.subheader("📄 Matrices numéricas")
        mat_col1, mat_col2 = st.columns(2)
        with mat_col1:
            st.markdown("**Matriz numérica inicial:**")
            st.code(show_matrix_text(cropped, "Inicial"), language="text")
        with mat_col2:
            st.markdown("**Matriz numérica resultante:**")
            st.code(show_matrix_text(result_img, f"Resultante — {filter_name}"), language="text")

        # Comparación visual: 2×2 grid (Imagen + Digitalización)
        st.markdown("---")
        st.subheader("📈 Comparación visual — Inicial vs Resultante")
        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            st.image(cropped, caption="Imagen Inicial", clamp=True, width="stretch")
            fig_comp_init = show_digitalization_grid(cropped)
            st.pyplot(fig_comp_init)
            st.caption("Digitalización Inicial")
        with comp_col2:
            st.image(result_img, caption=f"Imagen Resultante — {filter_name}", clamp=True, width="stretch")
            fig_comp_res = show_digitalization_grid(result_img)
            st.pyplot(fig_comp_res)
            st.caption("Digitalización Resultante")
