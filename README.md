# 🎨 Filtrado de Imágenes

Procesamiento digital de imágenes con filtros Media, Mediana, Laplaciano y Sobel.

## 🚀 Deploy automático

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/new)

## 📦 Instalación local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

## 📱 Compartir en presentación

```bash
streamlit run app.py &
ngrok http 8501
```

## 📁 Estructura

- `app.py` — aplicación Streamlit
- `filtrado/core.py` — funciones de procesamiento
- `filtrado/display.py` — visualización de matrices
- `tests/` — 30 tests pytest
- `notebooks/` — backup para Colab
