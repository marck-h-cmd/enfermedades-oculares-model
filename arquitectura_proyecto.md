# Arquitectura del Sistema: OcularDiagnose (Advanced Clinical Suite)

Este documento detalla la arquitectura de software y el flujo de datos del proyecto **OcularDiagnose**, diseñado para la detección, diagnóstico y análisis estadístico robusto de patologías oculares a partir de imágenes de fondo de ojo.

---

## 1. Diagrama de Arquitectura General

El sistema está diseñado bajo una arquitectura desacoplada de microservicios e interfaces de usuario, comunicadas a través de protocolos REST y llamadas a APIs de inferencia.

```mermaid
graph TD
    %% Estilos de Nodos
    style UI fill:#e0f2fe,stroke:#0284c7,stroke-width:2px;
    style API fill:#fef3c7,stroke:#d97706,stroke-width:2px;
    style ML fill:#dcfce7,stroke:#16a34a,stroke-width:2px;
    style DB fill:#f3e8ff,stroke:#7e22ce,stroke-width:2px;

    subgraph Capa de Presentación (Frontend)
        UI_React["React / Next.js Web App (Puerto 3000)"]
        UI_Streamlit["Streamlit ML Dashboard (Puerto 8501)"]
    end

    subgraph Capa de Aplicación (Backend)
        API_FastAPI["FastAPI Server (Uvicorn - Puerto 8000)"]
        Auth_JWT["Módulo de Autenticación (JWT)"]
        Chat_Groq["Orquestador de Chat (Llama3 via Groq)"]
    end

    subgraph Capa de Inteligencia Artificial e Inferencia
        TF_Models["Modelos Base (TensorFlow / Keras) <br> - MobileNetV2 <br> - ResNet50V2 <br> - EfficientNetV2-B0"]
        Ensemble_Engine["Consenso de Modelos (Ensemble) <br> - Promedio Ponderado de Probabilidades"]
        Hybrid_RF["Clasificador Híbrido <br> - MobileNetV2 (Extractor) + Random Forest"]
        XAI_Engine["Preprocesamiento y Explicabilidad <br> - CLAHE Contrast Adaptation <br> - Mapas de Calor Grad-CAM"]
    end

    subgraph Biblioteca de Validación Estadística
        Stats_Core["stats_validation.py <br> - Shapiro-Wilk <br> - Wilcoxon & t-Student <br> - Holm-Bonferroni <br> - Friedman & Nemenyi"]
        Stats_Robust["robust_stats_validation.py <br> - Kolmogorov-Smirnov <br> - Alpha-trimming <br> - Pitman-Morgan <br> - Lagrange Multiplier (LMBP) <br> - E-C2ST (Sequential E-values)"]
    end

    subgraph Capa de Almacenamiento (Base de Datos / Archivos)
        JSON_CV["cv_metrics_results.json <br> (Métricas por Folds de Cross-Validation)"]
        H5_Models["Modelos Pesos (.h5) <br> - best_ocular_model.h5 <br> - best_rf_classifier.pkl"]
        Report_PDF["Generador de Reportes PDF"]
    end

    %% Conexiones
    UI_React -->|HTTP Requests / Auth| API_FastAPI
    UI_Streamlit -->|Lectura/Escritura| JSON_CV
    UI_Streamlit -->|Guardado de pesos| H5_Models
    
    API_FastAPI --> Auth_JWT
    API_FastAPI --> Chat_Groq
    API_FastAPI -->|Carga de Pesos| H5_Models
    API_FastAPI -->|Inferencia / Explicabilidad| XAI_Engine
    API_FastAPI -->|Llamadas Estadísticas| Stats_Core
    API_FastAPI -->|Llamadas Robustas| Stats_Robust
    
    XAI_Engine --> TF_Models
    XAI_Engine --> Hybrid_RF
    Stats_Core -->|Carga de Datos| JSON_CV
    
    API_FastAPI -->|Generación de Fichas| Report_PDF
```

---

## 2. Descripción de Componentes por Capas

### A. Capa de Presentación (Frontend)
1. **OcularDiagnose Web App (Next.js / React):**
   * **Propósito:** Panel de control clínico principal para oftalmólogos y médicos.
   * **Módulos Clave:**
     * *Diagnóstico:* Carga de retinografías en tiempo real, sliders dinámicos de comparación visual (Imagen Original vs. Preprocesamiento CLAHE) y mapa de calor Grad-CAM.
     * *Significancia Estadística:* Visualización detallada de la tabla de diferencias críticas de Nemenyi, Friedman, y la grilla de diagnóstico de robustez de 3 niveles de severidad (Alerta, Informativo, Estable).
     * *Chat Clínico:* Interfaz de mensajería con un asistente de IA entrenado para resolver dudas sobre diagnósticos oculares.
     * *Fichas Clínicas:* Descarga de PDF detallando el caso del paciente.
2. **Streamlit ML Dashboard:**
   * **Propósito:** Entorno analítico para desarrolladores e ingenieros de Machine Learning.
   * **Módulos Clave:**
     * Entrenamiento por folds (Cross-Validation).
     * Tuning de hiperparámetros.
     * Evaluación detallada de curvas ROC/AUC, Brier Scores e histogramas de brillo.

### B. Capa de Aplicación (Backend - FastAPI)
* **Arquitectura:** RESTful asíncrona.
* **Controladores Principales (`backend/`):**
  * `auth.py`: Control de acceso mediante hash de contraseñas y emisión de tokens JWT portadores.
  * `predict.py`: Canal de inferencia principal. Carga los pesos, aplica el preprocesamiento CLAHE, calcula Grad-CAM con gradientes de TensorFlow y expone el endpoint `/api/predict`.
  * `stats.py`: Calcula y organiza la metadata estadística uniendo el cross-validation con la librería estadística para consumo del frontend.
  * `chat.py`: Conecta la API de Groq Cloud (usando modelos de la familia Llama-3) inyectando un *system prompt* clínico para asegurar respuestas médicas rigurosas y seguras.
  * `reports.py`: Genera de forma automatizada los documentos en PDF usando ReportLab.

### C. Capa de Inteligencia Artificial (Inferencia)
El sistema utiliza una estrategia de consenso probabilístico:
* **Extractor de Características:** MobileNetV2 convierte imágenes de $224\times224\times3$ en vectores de características altamente abstractos de 1,280 dimensiones.
* **Random Forest (CNN-RF Classifier):** Utiliza los vectores anteriores para evaluar las decisiones a través de un bosque aleatorio de 100 estimadores lógicos, reduciendo el sobreajuste en conjuntos de datos pequeños.
* **Ensemble (Fusión):** Combina el poder predictivo promediando las salidas de MobileNetV2, ResNet50V2 y EfficientNetV2 para estabilizar las predicciones marginales.

### D. Librería Estadística (Validación e Inferencia)
Juzga si los modelos han aprendido patrones sistemáticos o si los resultados son producto de fluctuaciones aleatorias en las muestras:
1. **`stats_validation.py`:**
   * Ejecuta la comparación global y post-hoc (Friedman y Nemenyi).
   * Evalúa la normalidad de diferencias (Shapiro-Wilk) para seleccionar de manera inteligente entre pruebas paramétricas (t-Student pareada) y no paramétricas (Wilcoxon).
   * Corrige el riesgo de falsos positivos en comparaciones múltiples mediante el algoritmo secuencial de Holm-Bonferroni.
2. **`robust_stats_validation.py`:**
   * Biblioteca matemática que valida la robustez clínica de los modelos.
   * Modela la variabilidad de inicialización ($\alpha$-trimming), la robustez ante la luz y contraste (Multiplicadores de Lagrange), y los cambios de distribución por ruido del entorno físico (E-C2ST).

---

## 3. Flujo de Datos Principal (Inferencia)

El siguiente flujo detalla el camino de una imagen desde que el usuario la sube hasta que se genera el diagnóstico estadísticamente validado:

```
[Usuario sube retinografía]
          │
          ▼
[React Web App] ──(Envía POST con imagen + Token JWT)──► [FastAPI /api/predict]
                                                               │
                                                               ▼
                                                     [Preprocesamiento CLAHE]
                                                               │
                                                               ▼
                                                     [Inferencia del Modelo]
                                                  ┌────────────┴────────────┐
                                                  ▼                         ▼
                                             [Probabilidad]          [Grad-CAM Gradients]
                                                  │                         │
                                                  ▼                         ▼
                                           [Normalización]          [Generación Heatmap]
                                                  │                         │
                                                  └────────────┬────────────┘
                                                               │
                                                               ▼
[React visualiza predicción + Grad-CAM] ◄──(Devuelve JSON)───[Respuesta API]
```
