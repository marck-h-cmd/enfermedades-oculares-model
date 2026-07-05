# Modelo de Detección de Enfermedades Oculares

Este proyecto es una aplicación desarrollada en **Python** que utiliza **Streamlit** para la interfaz de usuario y **TensorFlow/Keras** para modelos de Deep Learning enfocados en la detección o clasificación de diversas enfermedades oculares a partir de imágenes médicas.

## Características Principales

*   **Interfaz de Usuario (Streamlit):** Una aplicación interactiva que permite a los usuarios cargar imágenes oculares y recibir predicciones sobre posibles patologías.
*   **Modelos de Deep Learning:** Implementación y entrenamiento de modelos como MobileNetV2, EfficientNetB0 y ResNet50V2, así como un modelo ensamblado (Ensemble) para mejorar la precisión y confianza.
*   **Procesamiento de Imágenes (CLAHE):** Se incluye preprocesamiento avanzado utilizando CLAHE (Contrast Limited Adaptive Histogram Equalization) para mejorar el contraste de las imágenes médicas antes de ser analizadas por la red neuronal.
*   **Visualización y Análisis:** Análisis estadístico integrado y métricas de desempeño usando Plotly, Seaborn y Matplotlib.

## Estructura del Proyecto

*   `app.py`: Archivo principal que ejecuta la aplicación web con Streamlit.
*   `clahe.py`: Funciones o aplicación orientada al preprocesamiento de imágenes utilizando CLAHE.
*   `train_model.py`: Script para el entrenamiento individual de los modelos base.
*   `train_ensemble.py`: Script para el entrenamiento y combinación de modelos mediante un enfoque de ensamble (Ensemble).
*   `translation.py`: Posiblemente un módulo de traducción para la interfaz o aumentación de datos orientada a la posición (translation).
*   `requirements.txt`: Lista de dependencias del proyecto.

## Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/marck-h-cmd/enfermedades-oculares-model.git
    cd enfermedades-oculares-model
    ```

2.  **Crear y activar un entorno virtual (recomendado):**
    ```bash
    # En Windows:
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

## Ejecución

Para iniciar la aplicación principal, asegúrate de tener tu entorno activado y ejecuta:

```bash
streamlit run app.py
```

## Contacto / Autor
- Marck (marck-h-cmd) - [mahermenegildopa@unitru.edu.pe]
