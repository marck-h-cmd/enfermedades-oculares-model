import streamlit as st
import tensorflow as tf
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import cv2
import os
import time
from datetime import datetime
import warnings
import base64
import json
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from sklearn.metrics import matthews_corrcoef, confusion_matrix, classification_report
from scipy.stats import chi2
from scipy import stats
import itertools
from pathlib import Path

warnings.filterwarnings('ignore')

# Configuración de página
st.set_page_config(
    page_title="🏥 Comparación de 3 Arquitecturas CNN + Estadísticas",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class AplicacionTresArquitecturas:
    """Aplicación para comparar 3 arquitecturas CNN con análisis estadístico avanzado"""
    
    def __init__(self):
        # Tu código existente de __init__ aquí...
        self.informacion_clases = {
            'Central Serous Chorioretinopathy [Color Fundus]': {
                'nombre': 'Corioretinopatía Serosa Central',
                'descripcion': 'Acumulación de líquido bajo la retina',
                'gravedad': 'Moderada',
                'color': '#FFA07A',
                'tratamiento': 'Observación, láser focal en casos persistentes',
                'pronostico': 'Bueno, resolución espontánea en 80% casos'
            },
            'Diabetic Retinopathy': {
                'nombre': 'Retinopatía Diabética', 
                'descripcion': 'Daño vascular por diabetes',
                'gravedad': 'Alta',
                'color': '#FF6B6B',
                'tratamiento': 'Control glucémico, inyecciones intravítreas, láser',
                'pronostico': 'Manejo temprano previene ceguera'
            },
            'Disc Edema': {
                'nombre': 'Edema del Disco Óptico',
                'descripcion': 'Hinchazón por presión intracraneal',
                'gravedad': 'Alta',
                'color': '#FF4444',
                'tratamiento': 'Urgente: reducir presión intracraneal',
                'pronostico': 'Depende de causa subyacente'
            },
            'Glaucoma': {
                'nombre': 'Glaucoma',
                'descripcion': 'Daño del nervio óptico',
                'gravedad': 'Alta',
                'color': '#DC143C',
                'tratamiento': 'Gotas hipotensoras, láser, cirugía',
                'pronostico': 'Progresión lenta con tratamiento'
            },
            'Healthy': {
                'nombre': 'Ojo Sano',
                'descripcion': 'Sin patologías detectadas',
                'gravedad': 'Normal',
                'color': '#32CD32',
                'tratamiento': 'Exámenes preventivos anuales',
                'pronostico': 'Excelente'
            },
            'Macular Scar': {
                'nombre': 'Cicatriz Macular',
                'descripcion': 'Tejido cicatricial en mácula',
                'gravedad': 'Moderada',
                'color': '#DAA520',
                'tratamiento': 'Rehabilitación visual, ayudas ópticas',
                'pronostico': 'Estable, visión central afectada'
            },
            'Myopia': {
                'nombre': 'Miopía',
                'descripcion': 'Error refractivo',
                'gravedad': 'Leve',
                'color': '#87CEEB',
                'tratamiento': 'Lentes correctivos, cirugía refractiva',
                'pronostico': 'Excelente con corrección'
            },
            'Pterygium': {
                'nombre': 'Pterigión',
                'descripcion': 'Crecimiento anormal en córnea',
                'gravedad': 'Leve',
                'color': '#DDA0DD',
                'tratamiento': 'Observación, cirugía si afecta visión',
                'pronostico': 'Bueno, puede recurrir post-cirugía'
            },
            'Retinal Detachment': {
                'nombre': 'Desprendimiento de Retina',
                'descripcion': 'Emergencia: separación retinal',
                'gravedad': 'Crítica',
                'color': '#B22222',
                'tratamiento': 'URGENTE: cirugía inmediata',
                'pronostico': 'Bueno si se trata en <24-48h'
            },
            'Retinitis Pigmentosa': {
                'nombre': 'Retinitis Pigmentosa',
                'descripcion': 'Degeneración progresiva',
                'gravedad': 'Alta',
                'color': '#8B0000',
                'tratamiento': 'Suplementos, implantes retinales',
                'pronostico': 'Progresivo, investigación activa'
            }
        }
        
        # Tu código existente de architecture_info...
        self.informacion_arquitecturas = {
            'CNN_Original': {
                'nombre_completo': 'CNN MobileNetV2 Original',
                'descripcion': 'Tu modelo inicial entrenado (70.44% accuracy)',
                'color': '#E91E63',
                'icon': '🧠',
                'ventajas': ['Tu modelo base', 'Conocido', 'Optimizado móvil'],
                'caracteristicas': {
                    'Tipo': 'Depthwise Separable Convolutions',
                    'Parámetros': '~3.5M',
                    'Ventaja principal': 'Eficiencia computacional',
                    'Año': '2018'
                }
            },
            'EfficientNetB0': {
                'nombre_completo': 'EfficientNet-B0',
                'descripcion': 'Arquitectura con compound scaling balanceado',
                'color': '#2196F3',
                'icon': '⚡',
                'ventajas': ['Compound scaling', 'Balance accuracy/params', 'Estado del arte'],
                'caracteristicas': {
                    'Tipo': 'Compound Scaling CNN',
                    'Parámetros': '~5.3M',
                    'Ventaja principal': 'Balance óptimo accuracy/eficiencia',
                    'Año': '2019'
                }
            },
            'ResNet50V2': {
                'nombre_completo': 'ResNet-50 V2',
                'descripcion': 'Red residual profunda con conexiones skip',
                'color': '#FF9800',
                'icon': '🔗',
                'ventajas': ['Conexiones residuales', 'Red profunda', 'Estable'],
                'caracteristicas': {
                    'Tipo': 'Residual Network',
                    'Parámetros': '~25.6M',
                    'Ventaja principal': 'Capacidad de representación profunda',
                    'Año': '2016'
                }
            }
        }
        
        self.modelos = None
        self.nombres_clases = None
        self.nombres_clases_individuales = None
        self.analisis_actual = None
        self.resultados_estadisticos = None  # Para almacenar resultados estadísticos
    
    @st.cache_resource
    def cargar_modelos(_self):
        """Carga las 3 arquitecturas para comparar"""
        try:
            modelos = {}
            
            # Mapeo de archivos a arquitecturas
            archivos_modelos = {
                'CNN_Original': 'eye_disease_model.h5',
                'EfficientNetB0': 'ensemble_efficientnet_model.h5', 
                'ResNet50V2': 'ensemble_resnet_model.h5'
            }
            
            for nombre_arq, nombre_archivo in archivos_modelos.items():
                if os.path.exists(nombre_archivo):
                    modelos[nombre_arq] = tf.keras.models.load_model(nombre_archivo)
                    st.success(f"✅ {nombre_arq} cargado correctamente")
                else:
                    st.warning(f"⚠️ No se encontró {nombre_archivo}")
            
            # Cargar nombres de clases
            nombres_clases_conjunto = {}
            if os.path.exists('ensemble_class_indices.npy'):
                indices_clases = np.load('ensemble_class_indices.npy', allow_pickle=True).item()
                nombres_clases_conjunto = {v: k for k, v in indices_clases.items()}
            
            nombres_clases_individuales = {}
            if os.path.exists('class_indices.npy'):
                indices_clases = np.load('class_indices.npy', allow_pickle=True).item()
                nombres_clases_individuales = {v: k for k, v in indices_clases.items()}
            
            # Nombres por defecto si no hay archivos
            if not nombres_clases_conjunto:
                nombres_clases_conjunto = {i: f"Clase_{i}" for i in range(10)}
            if not nombres_clases_individuales:
                nombres_clases_individuales = {i: f"Clase_{i}" for i in range(10)}
            
            return modelos, nombres_clases_conjunto, nombres_clases_individuales
            
        except Exception as e:
            st.error(f"Error cargando modelos: {str(e)}")
            return {}, {}, {}
    
    def preprocesar_imagen(self, imagen):
        """Preprocesa imagen para predicción"""
        try:
            if imagen.mode != 'RGB':
                imagen = imagen.convert('RGB')
            
            imagen = imagen.resize((224, 224))
            array_img = np.array(imagen)
            array_img = array_img.astype('float32') / 255.0
            array_img = np.expand_dims(array_img, axis=0)
            
            return array_img
            
        except Exception as e:
            st.error(f"Error procesando imagen: {str(e)}")
            return None

    def preprocesar_imagen_desde_ruta(self, ruta_imagen):
        """Preprocesa imagen desde ruta para evaluación estadística"""
        try:
            imagen = Image.open(ruta_imagen)
            return self.preprocesar_imagen(imagen)
        except Exception as e:
            st.error(f"Error procesando imagen {ruta_imagen}: {str(e)}")
            return None
    
    def predecir_con_cronometraje(self, modelo, array_img, nombre_arq):
        """Realiza predicción midiendo tiempo y métricas"""
        try:
            # Medir tiempo de predicción
            tiempo_inicio = time.time()
            predicciones = modelo.predict(array_img, verbose=0)
            tiempo_fin = time.time()
            
            tiempo_prediccion = tiempo_fin - tiempo_inicio
            
            indice_clase_predicha = np.argmax(predicciones[0])
            confianza = float(predicciones[0][indice_clase_predicha])
            
            # Usar nombres de clases correctos
            if nombre_arq == 'CNN_Original':
                clase_predicha = self.nombres_clases_individuales[indice_clase_predicha]
            else:
                clase_predicha = self.nombres_clases[indice_clase_predicha]
            
            return {
                'arquitectura': nombre_arq,
                'clase_predicha': clase_predicha,
                'indice_clase_predicha': indice_clase_predicha,
                'confianza': confianza,
                'todas_probabilidades': predicciones[0],
                'tiempo_prediccion': tiempo_prediccion,
                'tamaño_modelo': self.obtener_tamaño_modelo(modelo),
                'conteo_parametros': modelo.count_params()
            }
            
        except Exception as e:
            st.error(f"Error en predicción {nombre_arq}: {str(e)}")
            return None
    
    def obtener_tamaño_modelo(self, modelo):
        """Calcula el tamaño del modelo en MB"""
        try:
            conteo_parametros = modelo.count_params()
            tamaño_mb = (conteo_parametros * 4) / (1024 * 1024)
            return tamaño_mb
        except:
            return 0
    
    # ========== NUEVAS FUNCIONES ESTADÍSTICAS ==========
    
    def calcular_correlacion_matthews(self, y_verdadero, y_predicho):
        """Calcula el Coeficiente de Correlación de Matthews"""
        try:
            mcc = matthews_corrcoef(y_verdadero, y_predicho)
            return mcc
        except Exception as e:
            st.error(f"Error calculando MCC: {str(e)}")
            return 0.0
    
    def prueba_mcnemar(self, y_verdadero, y_pred1, y_pred2):
        """Realiza la prueba de McNemar entre dos modelos"""
        try:
            # Crear tabla de contingencia 2x2
            # Casos donde modelo1 correcto, modelo2 incorrecto
            correcto_1_incorrecto_2 = np.sum((y_pred1 == y_verdadero) & (y_pred2 != y_verdadero))
            # Casos donde modelo1 incorrecto, modelo2 correcto  
            incorrecto_1_correcto_2 = np.sum((y_pred1 != y_verdadero) & (y_pred2 == y_verdadero))
            
            # Tabla de contingencia
            tabla_contingencia = np.array([
                [correcto_1_incorrecto_2, incorrecto_1_correcto_2],
                [incorrecto_1_correcto_2, correcto_1_incorrecto_2]
            ])
            
            # Calcular estadístico de McNemar con corrección de continuidad
            n = correcto_1_incorrecto_2 + incorrecto_1_correcto_2
            
            if n == 0:
                return {
                    'estadistico': 0.0,
                    'valor_p': 1.0,
                    'significativo': False,
                    'tabla_contingencia': tabla_contingencia,
                    'interpretacion': 'No hay diferencias entre modelos'
                }
            
            # McNemar con corrección de continuidad de Yates
            estadistico_mcnemar = (abs(correcto_1_incorrecto_2 - incorrecto_1_correcto_2) - 1)**2 / n
            valor_p = 1 - chi2.cdf(estadistico_mcnemar, df=1)
            
            # Interpretación
            significativo = valor_p < 0.05
            
            if significativo:
                if correcto_1_incorrecto_2 > incorrecto_1_correcto_2:
                    interpretacion = "Modelo 1 significativamente mejor que Modelo 2"
                else:
                    interpretacion = "Modelo 2 significativamente mejor que Modelo 1"
            else:
                interpretacion = "No hay diferencia significativa entre modelos"
            
            return {
                'estadistico': estadistico_mcnemar,
                'valor_p': valor_p,
                'significativo': significativo,
                'tabla_contingencia': tabla_contingencia,
                'interpretacion': interpretacion,
                'n_desacuerdos': n
            }
            
        except Exception as e:
            st.error(f"Error en prueba McNemar: {str(e)}")
            return None
    
    def calcular_intervalo_confianza_mcc(self, y_verdadero, y_predicho, confianza=0.95):
        """Calcula intervalo de confianza bootstrap para MCC"""
        try:
            n_bootstrap = 1000
            mccs_bootstrap = []
            
            n_muestras = len(y_verdadero)
            
            for _ in range(n_bootstrap):
                # Bootstrap resampling
                indices = np.random.choice(n_muestras, n_muestras, replace=True)
                y_verdadero_bootstrap = y_verdadero[indices]
                y_predicho_bootstrap = y_predicho[indices]
                
                try:
                    mcc_bootstrap = matthews_corrcoef(y_verdadero_bootstrap, y_predicho_bootstrap)
                    mccs_bootstrap.append(mcc_bootstrap)
                except:
                    continue
            
            if len(mccs_bootstrap) == 0:
                return None, None
            
            alpha = 1 - confianza
            percentil_inferior = (alpha/2) * 100
            percentil_superior = (1 - alpha/2) * 100
            
            ci_inferior = np.percentile(mccs_bootstrap, percentil_inferior)
            ci_superior = np.percentile(mccs_bootstrap, percentil_superior)
            
            return ci_inferior, ci_superior
            
        except Exception as e:
            st.error(f"Error calculando IC para MCC: {str(e)}")
            return None, None
    
    def escanear_carpeta_dataset(self, ruta_dataset):
        """Escanea carpeta de dataset y crea lista de imágenes con etiquetas"""
        try:
            ruta_dataset = Path(ruta_dataset)
            extensiones_imagen = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
            
            datos_imagenes = []
            carpetas_clases = [d for d in ruta_dataset.iterdir() if d.is_dir()]
            
            if not carpetas_clases:
                st.error("No se encontraron carpetas de clases en el dataset")
                return None
            
            # Mapear nombres de carpetas a índices
            nombre_clase_a_indice = {}
            
            st.info(f"📁 Clases encontradas: {len(carpetas_clases)}")
            
            for indice_clase, carpeta_clase in enumerate(sorted(carpetas_clases)):
                nombre_clase = carpeta_clase.name
                nombre_clase_a_indice[nombre_clase] = indice_clase
                
                st.write(f"• **Clase {indice_clase}**: {nombre_clase}")
                
                # Buscar imágenes en la carpeta
                imagenes_en_clase = []
                for ext in extensiones_imagen:
                    imagenes_en_clase.extend(carpeta_clase.glob(f'*{ext}'))
                    imagenes_en_clase.extend(carpeta_clase.glob(f'*{ext.upper()}'))
                
                for ruta_img in imagenes_en_clase:
                    datos_imagenes.append({
                        'ruta_imagen': str(ruta_img),
                        'etiqueta_verdadera': indice_clase,
                        'nombre_clase': nombre_clase
                    })
            
            st.success(f"✅ Total de imágenes encontradas: {len(datos_imagenes)}")
            
            return datos_imagenes, nombre_clase_a_indice
            
        except Exception as e:
            st.error(f"Error escaneando dataset: {str(e)}")
            return None, None

    def evaluar_modelos_en_dataset(self, entrada_dataset):
        """Evalúa todos los modelos en un dataset (carpeta o CSV)"""
        try:
            # Determinar si es carpeta o archivo CSV
            if isinstance(entrada_dataset, str) and entrada_dataset.endswith('.csv'):
                # Leer CSV
                df_prueba = pd.read_csv(entrada_dataset)
                
                if 'ruta_imagen' not in df_prueba.columns or 'etiqueta_verdadera' not in df_prueba.columns:
                    st.error("El archivo CSV debe contener columnas 'ruta_imagen' y 'etiqueta_verdadera'")
                    return None
                
                datos_imagenes = df_prueba.to_dict('records')
                
            else:
                # Escanear carpeta de dataset
                datos_imagenes, mapeo_clases = self.escanear_carpeta_dataset(entrada_dataset)
                if datos_imagenes is None:
                    return None
            
            resultados = {
                'etiquetas_verdaderas': [],
                'predicciones': {arq: [] for arq in self.modelos.keys()},
                'confianzas': {arq: [] for arq in self.modelos.keys()},
                'tiempos_prediccion': {arq: [] for arq in self.modelos.keys()}
            }
            
            total_imagenes = len(datos_imagenes)
            barra_progreso = st.progress(0)
            texto_estado = st.empty()
            
            # Procesar imágenes en lotes para eficiencia
            for idx, datos_img in enumerate(datos_imagenes):
                texto_estado.text(f"Evaluando imagen {idx+1}/{total_imagenes}: {Path(datos_img['ruta_imagen']).name}")
                
                # Preprocesar imagen
                array_img = self.preprocesar_imagen_desde_ruta(datos_img['ruta_imagen'])
                if array_img is None:
                    continue
                
                # Etiqueta verdadera
                etiqueta_verdadera = datos_img['etiqueta_verdadera']
                resultados['etiquetas_verdaderas'].append(etiqueta_verdadera)
                
                # Predecir con cada modelo
                for nombre_arq, modelo in self.modelos.items():
                    resultado_pred = self.predecir_con_cronometraje(modelo, array_img, nombre_arq)
                    
                    if resultado_pred:
                        resultados['predicciones'][nombre_arq].append(resultado_pred['indice_clase_predicha'])
                        resultados['confianzas'][nombre_arq].append(resultado_pred['confianza'])
                        resultados['tiempos_prediccion'][nombre_arq].append(resultado_pred['tiempo_prediccion'])
                    else:
                        resultados['predicciones'][nombre_arq].append(-1)  # Error
                        resultados['confianzas'][nombre_arq].append(0.0)
                        resultados['tiempos_prediccion'][nombre_arq].append(0.0)
                
                # Actualizar progreso
                barra_progreso.progress((idx + 1) / total_imagenes)
                
                # Mostrar progreso cada 50 imágenes
                if (idx + 1) % 50 == 0:
                    st.write(f"✅ Procesadas {idx + 1}/{total_imagenes} imágenes")
            
            barra_progreso.empty()
            texto_estado.empty()
            
            # Convertir a arrays numpy
            resultados['etiquetas_verdaderas'] = np.array(resultados['etiquetas_verdaderas'])
            for arq in self.modelos.keys():
                resultados['predicciones'][arq] = np.array(resultados['predicciones'][arq])
                resultados['confianzas'][arq] = np.array(resultados['confianzas'][arq])
                resultados['tiempos_prediccion'][arq] = np.array(resultados['tiempos_prediccion'][arq])
            
            return resultados
            
        except Exception as e:
            st.error(f"Error evaluando modelos: {str(e)}")
            return None
    
    def realizar_analisis_estadistico(self, resultados_evaluacion):
        """Realiza análisis estadístico completo"""
        try:
            y_verdadero = resultados_evaluacion['etiquetas_verdaderas']
            arquitecturas = list(self.modelos.keys())
            
            resultados_estadisticos = {
                'puntuaciones_mcc': {},
                'intervalos_confianza_mcc': {},
                'puntuaciones_accuracy': {},
                'resultados_mcnemar': {},
                'matrices_confusion': {},
                'reportes_clasificacion': {}
            }
            
            # Calcular MCC y accuracy para cada modelo
            for arq in arquitecturas:
                y_pred = resultados_evaluacion['predicciones'][arq]
                
                # MCC
                mcc = self.calcular_correlacion_matthews(y_verdadero, y_pred)
                resultados_estadisticos['puntuaciones_mcc'][arq] = mcc
                
                # Intervalo de confianza para MCC
                ci_inferior, ci_superior = self.calcular_intervalo_confianza_mcc(y_verdadero, y_pred)
                resultados_estadisticos['intervalos_confianza_mcc'][arq] = (ci_inferior, ci_superior)
                
                # Accuracy
                accuracy = np.mean(y_verdadero == y_pred)
                resultados_estadisticos['puntuaciones_accuracy'][arq] = accuracy
                
                # Matriz de confusión
                cm = confusion_matrix(y_verdadero, y_pred)
                resultados_estadisticos['matrices_confusion'][arq] = cm
                
                # Reporte de clasificación
                try:
                    reporte_clases = classification_report(y_verdadero, y_pred, output_dict=True)
                    resultados_estadisticos['reportes_clasificacion'][arq] = reporte_clases
                except:
                    resultados_estadisticos['reportes_clasificacion'][arq] = {}
            
            # Pruebas de McNemar entre pares de modelos
            for arq1, arq2 in itertools.combinations(arquitecturas, 2):
                y_pred1 = resultados_evaluacion['predicciones'][arq1]
                y_pred2 = resultados_evaluacion['predicciones'][arq2]
                
                resultado_mcnemar = self.prueba_mcnemar(y_verdadero, y_pred1, y_pred2)
                resultados_estadisticos['resultados_mcnemar'][f"{arq1}_vs_{arq2}"] = resultado_mcnemar
            
            return resultados_estadisticos
            
        except Exception as e:
            st.error(f"Error en análisis estadístico: {str(e)}")
            return None
    
    def mostrar_seccion_analisis_estadistico(self):
        """Sección completa de análisis estadístico"""
        st.markdown("---")
        st.header("📊 ANÁLISIS ESTADÍSTICO INFERENCIAL")
        st.markdown("""
        **Evaluación rigurosa con pruebas estadísticas:**
        - 🎯 **Coeficiente de Matthews (MCC)**: Métrica balanceada que considera todos los casos de la matriz de confusión
        - 🔬 **Prueba de McNemar**: Comparación estadística entre pares de modelos
        - 📈 **Intervalos de Confianza**: Bootstrap CI para robustez estadística
        """)
        
        # Dataset de evaluación
        st.subheader("📂 Dataset de Evaluación")
        
        # Input de ruta de carpeta
        carpeta_dataset = st.text_input(
            "🗂️ Ruta de la carpeta de pruebas:",
            value="Pruebas",  # Valor por defecto
            help="Ejemplo: Pruebas, ./Pruebas, /path/to/Pruebas"
        )
        
        # Mostrar estructura esperada
        with st.expander("📋 Estructura de carpetas esperada"):
            st.code("""
    📂 Pruebas/
    ├── 📁 Central_Serous_Chorioretinopathy/
    │   ├── 🖼️ test001.jpg
    │   ├── 🖼️ test002.jpg
    │   └── ...
    ├── 📁 Diabetic_Retinopathy/
    │   ├── 🖼️ test003.jpg
    │   ├── 🖼️ test004.jpg
    │   └── ...
    ├── 📁 Glaucoma/
    │   ├── 🖼️ test005.jpg
    │   └── ...
    └── 📁 Healthy/
        ├── 🖼️ test006.jpg
        └── ...

    ✅ Cada carpeta = una clase
    ✅ Nombres de carpetas = nombres de clases
    ✅ Formatos soportados: .jpg, .jpeg, .png, .bmp, .tiff
            """)
        
        # Verificar si la carpeta existe
        if carpeta_dataset:
            ruta_dataset = Path(carpeta_dataset)
            if ruta_dataset.exists() and ruta_dataset.is_dir():
                st.success(f"✅ Carpeta encontrada: {ruta_dataset.absolute()}")
                
                # Vista previa del dataset
                if st.button("👀 Vista Previa del Dataset", key="vista_previa_dataset"):
                    with st.spinner("🔍 Escaneando dataset..."):
                        datos_vista_previa, mapeo_clases = self.escanear_carpeta_dataset(ruta_dataset)
                        
                        if datos_vista_previa:
                            st.markdown("#### 📊 Resumen del Dataset:")
                            
                            # Crear DataFrame para mostrar distribución
                            df_vista_previa = pd.DataFrame(datos_vista_previa)
                            conteos_clases = df_vista_previa['nombre_clase'].value_counts()
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**📈 Distribución por Clase:**")
                                for nombre_clase, conteo in conteos_clases.items():
                                    st.markdown(f"• **{nombre_clase}**: {conteo} imágenes")
                            
                            with col2:
                                # Gráfico de distribución
                                fig_dist = go.Figure(data=[
                                    go.Bar(x=conteos_clases.index, y=conteos_clases.values)
                                ])
                                fig_dist.update_layout(
                                    title="📊 Distribución de Imágenes por Clase",
                                    xaxis_title="Clases",
                                    yaxis_title="Número de Imágenes",
                                    height=400
                                )
                                st.plotly_chart(fig_dist, use_container_width=True)
                            
                            st.dataframe(df_vista_previa.head(10), use_container_width=True)
                
                # Botón de evaluación
                if st.button("🚀 INICIAR EVALUACIÓN ESTADÍSTICA", type="primary", use_container_width=True, key="eval_carpeta"):
                    st.info("🔄 Evaluando modelos en dataset completo... Esto puede tomar varios minutos.")
                    
                    # Evaluar modelos
                    resultados_evaluacion = self.evaluar_modelos_en_dataset(str(ruta_dataset))
                    
                    if resultados_evaluacion is not None:
                        st.success("✅ Evaluación completada! Realizando análisis estadístico...")
                        
                        # Análisis estadístico
                        resultados_estadisticos = self.realizar_analisis_estadistico(resultados_evaluacion)
                        
                        if resultados_estadisticos is not None:
                            # Guardar en session state
                            st.session_state.resultados_estadisticos = resultados_estadisticos
                            st.session_state.resultados_evaluacion = resultados_evaluacion
                            
                            # Mostrar resultados
                            self.mostrar_resultados_estadisticos(resultados_estadisticos, resultados_evaluacion)
            
            else:
                st.error(f"❌ No se encontró la carpeta: {carpeta_dataset}")
                st.markdown("**💡 Sugerencias:**")
                st.markdown("• Verifica que la ruta sea correcta")
                st.markdown("• Usa rutas relativas como `Pruebas` o `./Pruebas`")
                st.markdown("• O rutas absolutas como `/ruta/completa/Pruebas`")
        
        # Mostrar resultados si ya están calculados
        if hasattr(st.session_state, 'resultados_estadisticos') and st.session_state.resultados_estadisticos:
            st.markdown("---")
            st.info("📊 Mostrando resultados de análisis estadístico previo")
            self.mostrar_resultados_estadisticos(
                st.session_state.resultados_estadisticos, 
                st.session_state.resultados_evaluacion
            )
    
    def mostrar_resultados_estadisticos(self, resultados_estadisticos, resultados_evaluacion):
        """Muestra resultados del análisis estadístico"""
        
        # Crear timestamp único para evitar keys duplicados
        import time
        timestamp = str(int(time.time() * 1000))  # timestamp en milisegundos
        
        # === SECCIÓN 1: COEFICIENTE DE MATTHEWS ===
        st.subheader("🎯 Coeficiente de Correlación de Matthews (MCC)")
        
        st.markdown("""
        **MCC** es una métrica balanceada que funciona bien incluso con clases desbalanceadas.
        - **Rango**: -1 (completamente incorrecto) a +1 (predicción perfecta)
        - **0**: Predicción aleatoria
        - **>0.5**: Excelente rendimiento
        """)
        
        # Tabla de MCC con intervalos de confianza
        datos_mcc = []
        for arq in self.modelos.keys():
            puntuacion_mcc = resultados_estadisticos['puntuaciones_mcc'][arq]
            ci_inferior, ci_superior = resultados_estadisticos['intervalos_confianza_mcc'][arq]
            accuracy = resultados_estadisticos['puntuaciones_accuracy'][arq]
            
            datos_mcc.append({
                'Arquitectura': arq.replace('_', ' '),
                'MCC': f"{puntuacion_mcc:.4f}",
                'IC 95% Inferior': f"{ci_inferior:.4f}" if ci_inferior else "N/A",
                'IC 95% Superior': f"{ci_superior:.4f}" if ci_superior else "N/A",
                'Accuracy': f"{accuracy:.4f}",
                'Interpretación': self.interpretar_mcc(puntuacion_mcc)
            })
        
        df_mcc = pd.DataFrame(datos_mcc)
        st.dataframe(df_mcc, use_container_width=True)
        
        # Gráfico de MCC con intervalos de confianza
        fig_mcc = go.Figure()
        
        arquitecturas = list(self.modelos.keys())
        puntuaciones_mcc = [resultados_estadisticos['puntuaciones_mcc'][arq] for arq in arquitecturas]
        ci_inferiores = [resultados_estadisticos['intervalos_confianza_mcc'][arq][0] for arq in arquitecturas]
        ci_superiores = [resultados_estadisticos['intervalos_confianza_mcc'][arq][1] for arq in arquitecturas]
        
        # Barras con intervalos de confianza
        fig_mcc.add_trace(go.Bar(
            x=[arq.replace('_', ' ') for arq in arquitecturas],
            y=puntuaciones_mcc,
            error_y=dict(
                type='data',
                symmetric=False,
                array=[ci_superior - mcc for ci_superior, mcc in zip(ci_superiores, puntuaciones_mcc)],
                arrayminus=[mcc - ci_inferior for ci_inferior, mcc in zip(ci_inferiores, puntuaciones_mcc)]
            ),
            marker_color=[self.informacion_arquitecturas[arq]['color'] for arq in arquitecturas],
            text=[f"{mcc:.3f}" for mcc in puntuaciones_mcc],
            textposition='auto'
        ))
        
        fig_mcc.update_layout(
            title="🎯 Coeficiente de Matthews con Intervalos de Confianza (95%)",
            yaxis_title="MCC Score",
            yaxis=dict(range=[-1, 1]),
            height=500
        )
        
        # Líneas de referencia
        fig_mcc.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Predicción Aleatoria")
        fig_mcc.add_hline(y=0.5, line_dash="dash", line_color="green", annotation_text="Excelente Rendimiento")
        
        st.plotly_chart(fig_mcc, use_container_width=True, key=f"grafico_mcc_principal_{timestamp}")
        
        # === SECCIÓN 2: PRUEBAS DE MCNEMAR ===
        st.subheader("🔬 Pruebas de McNemar - Comparación entre Modelos")
        
        st.markdown("""
        **Prueba de McNemar** compara estadísticamente el rendimiento entre pares de modelos:
        - **H₀**: No hay diferencia entre los modelos
        - **H₁**: Hay diferencia significativa
        - **α = 0.05**: Nivel de significancia
        """)
        
        datos_mcnemar = []
        for comparacion, resultado in resultados_estadisticos['resultados_mcnemar'].items():
            if resultado:
                arq1, arq2 = comparacion.split('_vs_')
                
                datos_mcnemar.append({
                    'Comparación': f"{arq1.replace('_', ' ')} vs {arq2.replace('_', ' ')}",
                    'Estadístico McNemar': f"{resultado['estadistico']:.4f}",
                    'p-valor': f"{resultado['valor_p']:.6f}",
                    'Significativo (α=0.05)': "✅ Sí" if resultado['significativo'] else "❌ No",
                    'Interpretación': resultado['interpretacion'],
                    'N° Desacuerdos': resultado['n_desacuerdos']
                })
        
        df_mcnemar = pd.DataFrame(datos_mcnemar)
        st.dataframe(df_mcnemar, use_container_width=True)
        
        # Heatmap de p-valores
        self.graficar_mapa_calor_mcnemar(resultados_estadisticos['resultados_mcnemar'], timestamp)
        
        # === SECCIÓN 3: MATRICES DE CONFUSIÓN ===
        st.subheader("🎭 Matrices de Confusión por Arquitectura")
        
        cols = st.columns(len(self.modelos))
        
        for i, (arq, cm) in enumerate(resultados_estadisticos['matrices_confusion'].items()):
            with cols[i]:
                fig_cm = self.graficar_matriz_confusion(cm, arq)
                st.plotly_chart(fig_cm, use_container_width=True, key=f"matriz_confusion_{arq}_{timestamp}")
        
        # === SECCIÓN 4: ANÁLISIS DE SIGNIFICANCIA ===
        st.subheader("📈 Análisis de Significancia Estadística")
        
        # Resumen de significancia
        comparaciones_significativas = [
            comp for comp, resultado in resultados_estadisticos['resultados_mcnemar'].items() 
            if resultado and resultado['significativo']
        ]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                label="🔬 Comparaciones Significativas",
                value=len(comparaciones_significativas),
                delta=f"de {len(resultados_estadisticos['resultados_mcnemar'])} totales"
            )
        
        with col2:
            mejor_mcc_arq = max(resultados_estadisticos['puntuaciones_mcc'], key=resultados_estadisticos['puntuaciones_mcc'].get)
            mejor_puntuacion_mcc = resultados_estadisticos['puntuaciones_mcc'][mejor_mcc_arq]
            
            st.metric(
                label="🏆 Mejor MCC",
                value=f"{mejor_puntuacion_mcc:.4f}",
                delta=f"{mejor_mcc_arq.replace('_', ' ')}"
            )
        
        # Recomendaciones estadísticas
        st.subheader("💡 Recomendaciones Estadísticas")
        
        if len(comparaciones_significativas) == 0:
            st.warning("""
            ⚠️ **No se encontraron diferencias estadísticamente significativas** entre los modelos.
            
            **Implicaciones:**
            - Los modelos tienen rendimiento similar estadísticamente
            - Otros criterios (velocidad, tamaño) pueden ser decisivos
            - Se recomienda aumentar el tamaño del dataset de prueba
            """)
        else:
            st.success(f"""
            ✅ **Se encontraron {len(comparaciones_significativas)} diferencias significativas**
            
            **Modelos con diferencias estadísticamente probadas:**
            """)
            
            for comp in comparaciones_significativas:
                resultado = resultados_estadisticos['resultados_mcnemar'][comp]
                st.markdown(f"• **{comp.replace('_', ' ')}**: {resultado['interpretacion']}")
        
        # === SECCIÓN 5: EXPORTAR RESULTADOS ESTADÍSTICOS ===
        st.subheader("📤 Exportar Resultados Estadísticos")
        
        if st.button("📊 Generar Reporte Estadístico Completo", use_container_width=True, key=f"btn_generar_reporte_estadistico_{timestamp}"):
            self.generar_reporte_estadistico(resultados_estadisticos, resultados_evaluacion)
    
    def interpretar_mcc(self, puntuacion_mcc):
        """Interpreta el score MCC"""
        if puntuacion_mcc >= 0.8:
            return "🟢 Excelente"
        elif puntuacion_mcc >= 0.6:
            return "🔵 Muy bueno"
        elif puntuacion_mcc >= 0.4:
            return "🟡 Bueno"
        elif puntuacion_mcc >= 0.2:
            return "🟠 Regular"
        elif puntuacion_mcc >= 0:
            return "🔴 Bajo"
        else:
            return "🔴 Muy bajo"
    
    def graficar_mapa_calor_mcnemar(self, resultados_mcnemar, timestamp=None):
        """Crea heatmap de p-valores de McNemar"""
        try:
            if timestamp is None:
                import time
                timestamp = str(int(time.time() * 1000))
                
            arquitecturas = list(self.modelos.keys())
            n_arqs = len(arquitecturas)
            
            # Matriz de p-valores
            matriz_valores_p = np.ones((n_arqs, n_arqs))
            matriz_significancia = np.zeros((n_arqs, n_arqs))
            
            for i, arq1 in enumerate(arquitecturas):
                for j, arq2 in enumerate(arquitecturas):
                    if i != j:
                        clave_comp = f"{arq1}_vs_{arq2}"
                        if clave_comp in resultados_mcnemar:
                            resultado = resultados_mcnemar[clave_comp]
                            matriz_valores_p[i, j] = resultado['valor_p']
                            matriz_significancia[i, j] = 1 if resultado['significativo'] else 0
                        else:
                            # Buscar comparación inversa
                            clave_comp_inv = f"{arq2}_vs_{arq1}"
                            if clave_comp_inv in resultados_mcnemar:
                                resultado = resultados_mcnemar[clave_comp_inv]
                                matriz_valores_p[i, j] = resultado['valor_p']
                                matriz_significancia[i, j] = 1 if resultado['significativo'] else 0
            
            # Crear heatmap
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=matriz_valores_p,
                x=[arq.replace('_', ' ') for arq in arquitecturas],
                y=[arq.replace('_', ' ') for arq in arquitecturas],
                colorscale='RdYlBu_r',
                text=[[f"p={matriz_valores_p[i,j]:.4f}" for j in range(n_arqs)] for i in range(n_arqs)],
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            # Añadir línea de significancia
            fig_heatmap.add_shape(
                type="line",
                x0=-0.5, y0=-0.5, x1=n_arqs-0.5, y1=n_arqs-0.5,
                line=dict(color="red", width=2, dash="dash")
            )
            
            fig_heatmap.update_layout(
                title="🔬 Heatmap de p-valores (Pruebas de McNemar)<br>Valores < 0.05 indican diferencia significativa",
                height=400
            )
            
            st.plotly_chart(fig_heatmap, use_container_width=True, key=f"heatmap_mcnemar_{timestamp}")
            
        except Exception as e:
            st.error(f"Error creando heatmap: {str(e)}")
    
    def graficar_matriz_confusion(self, cm, nombre_arquitectura):
        """Crea matriz de confusión interactiva"""
        try:
            fig_cm = go.Figure(data=go.Heatmap(
                z=cm,
                colorscale='Blues',
                text=cm,
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig_cm.update_layout(
                title=f"📊 {nombre_arquitectura.replace('_', ' ')}",
                xaxis_title="Predicción",
                yaxis_title="Verdadero",
                height=300
            )
            
            return fig_cm
            
        except Exception as e:
            st.error(f"Error creando matriz de confusión: {str(e)}")
            return go.Figure()
    
    def generar_reporte_estadistico(self, resultados_estadisticos, resultados_evaluacion):
        """Genera reporte estadístico completo"""
        try:
            # Crear reporte en formato texto
            contenido_reporte = self.crear_contenido_reporte_estadistico(resultados_estadisticos, resultados_evaluacion)
            
            # Crear archivo
            marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo_reporte = f"reporte_estadistico_{marca_tiempo}.txt"
            
            with open(nombre_archivo_reporte, 'w', encoding='utf-8') as f:
                f.write(contenido_reporte)
            
            # Crear también JSON con datos estructurados
            nombre_archivo_json = f"datos_estadisticos_{marca_tiempo}.json"
            
            # Convertir numpy arrays para JSON
            datos_json = {}
            for clave, valor in resultados_estadisticos.items():
                if isinstance(valor, dict):
                    datos_json[clave] = {}
                    for subclave, subvalor in valor.items():
                        if isinstance(subvalor, np.ndarray):
                            datos_json[clave][subclave] = subvalor.tolist()
                        elif isinstance(subvalor, np.integer):
                            datos_json[clave][subclave] = int(subvalor)
                        elif isinstance(subvalor, np.floating):
                            datos_json[clave][subclave] = float(subvalor)
                        else:
                            datos_json[clave][subclave] = subvalor
                else:
                    datos_json[clave] = valor
            
            with open(nombre_archivo_json, 'w', encoding='utf-8') as f:
                json.dump(datos_json, f, indent=2, ensure_ascii=False)
            
            # Botones de descarga
            col1, col2 = st.columns(2)
            
            with col1:
                with open(nombre_archivo_reporte, 'r', encoding='utf-8') as f:
                    datos_reporte = f.read()
                
                st.download_button(
                    label="📄 Descargar Reporte TXT",
                    data=datos_reporte,
                    file_name=nombre_archivo_reporte,
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col2:
                with open(nombre_archivo_json, 'r', encoding='utf-8') as f:
                    datos_json = f.read()
                
                st.download_button(
                    label="📊 Descargar Datos JSON",
                    data=datos_json,
                    file_name=nombre_archivo_json,
                    mime="application/json",
                    use_container_width=True
                )
            
            st.success("✅ Reportes estadísticos generados correctamente!")
            
            # Limpiar archivos temporales
            try:
                os.remove(nombre_archivo_reporte)
                os.remove(nombre_archivo_json)
            except:
                pass
                
        except Exception as e:
            st.error(f"Error generando reporte estadístico: {str(e)}")
    
    def crear_contenido_reporte_estadistico(self, resultados_estadisticos, resultados_evaluacion):
        """Crea contenido del reporte estadístico"""
        reporte = f"""
REPORTE DE ANÁLISIS ESTADÍSTICO INFERENCIAL
===========================================

Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Sistema: Comparación de Arquitecturas CNN para Diagnóstico Ocular
Número de modelos evaluados: {len(self.modelos)}
Tamaño del dataset de prueba: {len(resultados_evaluacion['etiquetas_verdaderas'])}

1. COEFICIENTE DE CORRELACIÓN DE MATTHEWS (MCC)
===============================================

El MCC es una métrica balanceada que considera todas las categorías de la matriz de confusión.
Rango: -1 (completamente incorrecto) a +1 (predicción perfecta)

"""
        
        # Resultados MCC
        for arq in self.modelos.keys():
            puntuacion_mcc = resultados_estadisticos['puntuaciones_mcc'][arq]
            ci_inferior, ci_superior = resultados_estadisticos['intervalos_confianza_mcc'][arq]
            accuracy = resultados_estadisticos['puntuaciones_accuracy'][arq]
            
            reporte += f"""
{arq.replace('_', ' ')}:
  - MCC Score: {puntuacion_mcc:.6f}
  - IC 95%: [{ci_inferior:.6f}, {ci_superior:.6f}]
  - Accuracy: {accuracy:.6f}
  - Interpretación: {self.interpretar_mcc(puntuacion_mcc)}
"""
        
        reporte += f"""

2. PRUEBAS DE MCNEMAR
====================

La prueba de McNemar compara estadísticamente el rendimiento entre pares de modelos.
H₀: No hay diferencia entre los modelos
H₁: Hay diferencia significativa (α = 0.05)

"""
        
        # Resultados McNemar
        for comparacion, resultado in resultados_estadisticos['resultados_mcnemar'].items():
            if resultado:
                reporte += f"""
{comparacion.replace('_', ' ')}:
  - Estadístico McNemar: {resultado['estadistico']:.6f}
  - p-valor: {resultado['valor_p']:.6f}
  - Significativo: {'Sí' if resultado['significativo'] else 'No'}
  - N° desacuerdos: {resultado['n_desacuerdos']}
  - Interpretación: {resultado['interpretacion']}
"""
        
        # Resumen y recomendaciones
        comparaciones_significativas = [
            comp for comp, resultado in resultados_estadisticos['resultados_mcnemar'].items() 
            if resultado and resultado['significativo']
        ]
        
        mejor_mcc_arq = max(resultados_estadisticos['puntuaciones_mcc'], key=resultados_estadisticos['puntuaciones_mcc'].get)
        mejor_puntuacion_mcc = resultados_estadisticos['puntuaciones_mcc'][mejor_mcc_arq]
        
        reporte += f"""

3. RESUMEN Y RECOMENDACIONES
============================

Mejor modelo por MCC: {mejor_mcc_arq.replace('_', ' ')} (MCC = {mejor_puntuacion_mcc:.6f})
Comparaciones significativas: {len(comparaciones_significativas)} de {len(resultados_estadisticos['resultados_mcnemar'])}

"""
        
        if len(comparaciones_significativas) == 0:
            reporte += """
CONCLUSIÓN:
No se encontraron diferencias estadísticamente significativas entre los modelos.
Esto sugiere que todos los modelos tienen un rendimiento similar estadísticamente.
La selección del modelo puede basarse en otros criterios como velocidad o eficiencia.

"""
        else:
            reporte += f"""
CONCLUSIÓN:
Se encontraron {len(comparaciones_significativas)} diferencias estadísticamente significativas:

"""
            for comp in comparaciones_significativas:
                resultado = resultados_estadisticos['resultados_mcnemar'][comp]
                reporte += f"- {comp.replace('_', ' ')}: {resultado['interpretacion']}\n"
        
        reporte += f"""

4. DETALLES TÉCNICOS
====================

Dataset de evaluación: {len(resultados_evaluacion['etiquetas_verdaderas'])} imágenes
Métodos estadísticos utilizados:
- Coeficiente de Correlación de Matthews
- Prueba de McNemar con corrección de continuidad de Yates
- Intervalos de confianza bootstrap (95%)
- Matrices de confusión

Arquitecturas evaluadas:
"""
        
        for arq in self.modelos.keys():
            info = self.informacion_arquitecturas[arq]
            reporte += f"- {info['nombre_completo']}: {info['descripcion']}\n"
        
        return reporte
    
    # ========== FUNCIONES ORIGINALES (MANTENER TODAS) ==========
    
    def encontrar_mejor_arquitectura(self, predicciones):
        """Encuentra la mejor arquitectura por diferentes métricas"""
        if not predicciones or len(predicciones) < 2:
            return {}
        
        # Mejor por confianza
        mejor_confianza = max(predicciones, key=lambda x: x['confianza'])
        
        # Más rápido
        mas_rapido = min(predicciones, key=lambda x: x['tiempo_prediccion'])
        
        # Más eficiente (mayor confianza / tiempo)
        for pred in predicciones:
            pred['eficiencia'] = pred['confianza'] / pred['tiempo_prediccion']
        mas_eficiente = max(predicciones, key=lambda x: x['eficiencia'])
        
        # Más ligero
        mas_ligero = min(predicciones, key=lambda x: x['tamaño_modelo'])
        
        return {
            'mayor_confianza': mejor_confianza,
            'mas_rapido': mas_rapido,
            'mas_eficiente': mas_eficiente,
            'mas_ligero': mas_ligero
        }
    
    def mostrar_encabezado(self):
        """Header de la aplicación"""
        st.title("🏆 DETECCION DE ENFERMEDADES OCULARES 👁️")
        st.subheader("MobileNetV2 vs EfficientNet-B0 vs ResNet-50 V2 + Análisis Estadístico")
        st.markdown("---")
    
    def mostrar_vitrina_arquitecturas(self):
        """Muestra las características de cada arquitectura"""
        st.header("🏗️ LAS 3 ARQUITECTURAS EN COMPETENCIA")
        
        cols = st.columns(3)
        
        for i, (nombre_arq, info) in enumerate(self.informacion_arquitecturas.items()):
            with cols[i]:
                # Header de la arquitectura
                st.subheader(f"{info['icon']} {info['nombre_completo']}")
                
                # Descripción
                st.info(f"**{info['descripcion']}**")
                
                # Características técnicas
                st.markdown("**📊 Características:**")
                st.markdown(f"• **Tipo:** {info['caracteristicas']['Tipo']}")
                st.markdown(f"• **Parámetros:** {info['caracteristicas']['Parámetros']}")
                st.markdown(f"• **Ventaja:** {info['caracteristicas']['Ventaja principal']}")
                st.markdown(f"• **Año:** {info['caracteristicas']['Año']}")
                
                # Ventajas
                st.markdown("**✅ Ventajas:**")
                for ventaja in info['ventajas']:
                    st.markdown(f"• {ventaja}")
                
                st.markdown("---")
    
    def mostrar_resultados_prediccion(self, predicciones):
        """Muestra resultados de las 3 arquitecturas lado a lado"""
        st.header("🎯 RESULTADOS DE PREDICCIÓN")
        
        cols = st.columns(3)
        
        for i, pred in enumerate(predicciones):
            nombre_arq = pred['arquitectura']
            info = self.informacion_arquitecturas[nombre_arq]
            
            with cols[i]:
                # Nombre de la arquitectura
                st.subheader(f"{info['icon']} {nombre_arq.replace('_', ' ')}")
                
                # Diagnóstico
                clase_predicha = pred['clase_predicha']
                info_clase = self.informacion_clases.get(clase_predicha, {})
                nombre_es = info_clase.get('nombre', clase_predicha)
                
                st.success(f"**Diagnóstico:** {nombre_es}")
                
                # Confianza (métrica principal)
                st.metric(
                    label="🎯 Confianza",
                    value=f"{pred['confianza']:.1%}",
                    delta=None
                )
                
                # Métricas técnicas
                st.markdown("**📊 Métricas Técnicas:**")
                st.markdown(f"⏱️ **Tiempo:** {pred['tiempo_prediccion']:.3f}s")
                st.markdown(f"💾 **Tamaño:** {pred['tamaño_modelo']:.1f}MB")
                st.markdown(f"🔢 **Parámetros:** {pred['conteo_parametros']:,}")
                
                st.markdown("---")
    
    def mostrar_comparacion_rendimiento(self, predicciones):
        """Gráficos comparativos de rendimiento"""
        st.markdown("## 📊 ANÁLISIS COMPARATIVO DE RENDIMIENTO")
        
        # Crear timestamp único
        import time
        timestamp = str(int(time.time() * 1000))
        
        # Crear DataFrame para gráficos
        df = pd.DataFrame([
            {
                'Arquitectura': pred['arquitectura'].replace('_', ' '),
                'Confianza': pred['confianza'],
                'Tiempo (s)': pred['tiempo_prediccion'],
                'Tamaño (MB)': pred['tamaño_modelo'],
                'Parámetros (M)': pred['conteo_parametros'] / 1_000_000,
                'Eficiencia (Conf/Tiempo)': pred['confianza'] / pred['tiempo_prediccion']
            }
            for pred in predicciones
        ])
        
        # Colores para gráficos
        colores = [self.informacion_arquitecturas[pred['arquitectura']]['color'] for pred in predicciones]
        
        # 4 gráficos en 2x2
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de confianza
            fig_conf = go.Figure(data=[
                go.Bar(
                    x=df['Arquitectura'],
                    y=df['Confianza'],
                    text=[f"{conf:.1%}" for conf in df['Confianza']],
                    textposition='auto',
                    marker_color=colores,
                    name='Confianza'
                )
            ])
            fig_conf.update_layout(
                title='🎯 Confianza de Predicción',
                yaxis=dict(tickformat='.0%'),
                height=400
            )
            st.plotly_chart(fig_conf, use_container_width=True, key=f"grafico_confianza_{timestamp}")
            
            # Gráfico de tamaño
            fig_tamaño = go.Figure(data=[
                go.Bar(
                    x=df['Arquitectura'],
                    y=df['Tamaño (MB)'],
                    text=[f"{tamaño:.1f}MB" for tamaño in df['Tamaño (MB)']],
                    textposition='auto',
                    marker_color=colores,
                    name='Tamaño'
                )
            ])
            fig_tamaño.update_layout(
                title='💾 Tamaño del Modelo',
                yaxis_title='Tamaño (MB)',
                height=400
            )
            st.plotly_chart(fig_tamaño, use_container_width=True, key=f"grafico_tamaño_{timestamp}")
        
        with col2:
            # Gráfico de tiempo
            fig_tiempo = go.Figure(data=[
                go.Bar(
                    x=df['Arquitectura'],
                    y=df['Tiempo (s)'],
                    text=[f"{tiempo:.3f}s" for tiempo in df['Tiempo (s)']],
                    textposition='auto',
                    marker_color=colores,
                    name='Tiempo'
                )
            ])
            fig_tiempo.update_layout(
                title='⏱️ Tiempo de Predicción',
                yaxis_title='Tiempo (segundos)',
                height=400
            )
            st.plotly_chart(fig_tiempo, use_container_width=True, key=f"grafico_tiempo_{timestamp}")
            
            # Gráfico de eficiencia
            fig_eff = go.Figure(data=[
                go.Bar(
                    x=df['Arquitectura'],
                    y=df['Eficiencia (Conf/Tiempo)'],
                    text=[f"{eff:.1f}" for eff in df['Eficiencia (Conf/Tiempo)']],
                    textposition='auto',
                    marker_color=colores,
                    name='Eficiencia'
                )
            ])
            fig_eff.update_layout(
                title='⚡ Eficiencia (Confianza/Tiempo)',
                yaxis_title='Eficiencia Score',
                height=400
            )
            st.plotly_chart(fig_eff, use_container_width=True, key=f"grafico_eficiencia_{timestamp}")
    
    def mostrar_comparacion_radar(self, predicciones):
        """Gráfico radar comparando todas las métricas"""
        st.markdown("### 🕸️ Comparación Multidimensional")
        
        # Crear timestamp único
        import time
        timestamp = str(int(time.time() * 1000))
        
        # Normalizar métricas para el radar (0-1)
        max_conf = max(pred['confianza'] for pred in predicciones)
        min_tiempo = min(pred['tiempo_prediccion'] for pred in predicciones)
        max_tiempo = max(pred['tiempo_prediccion'] for pred in predicciones)
        min_tamaño = min(pred['tamaño_modelo'] for pred in predicciones)
        max_tamaño = max(pred['tamaño_modelo'] for pred in predicciones)
        
        fig = go.Figure()
        
        categorias = ['Confianza', 'Velocidad', 'Eficiencia Memoria', 'Score General']
        
        for pred in predicciones:
            nombre_arq = pred['arquitectura']
            info = self.informacion_arquitecturas[nombre_arq]
            
            # Normalizar valores (más alto = mejor)
            norm_conf = pred['confianza'] / max_conf if max_conf > 0 else 0
            norm_velocidad = (max_tiempo - pred['tiempo_prediccion']) / (max_tiempo - min_tiempo) if max_tiempo > min_tiempo else 1
            norm_memoria = (max_tamaño - pred['tamaño_modelo']) / (max_tamaño - min_tamaño) if max_tamaño > min_tamaño else 1
            norm_general = (norm_conf + norm_velocidad + norm_memoria) / 3
            
            valores = [norm_conf, norm_velocidad, norm_memoria, norm_general]
            
            fig.add_trace(go.Scatterpolar(
                r=valores,
                theta=categorias,
                fill='toself',
                name=nombre_arq.replace('_', ' '),
                line_color=info['color']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickformat='.0%'
                )),
            title="🕸️ Perfil Multidimensional de Arquitecturas",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True, key=f"grafico_radar_{timestamp}")
    
    def mostrar_podio_ganadores(self, mejores_modelos):
        """Muestra el podio de ganadores por categoría"""
        st.header("🏆 PODIO DE GANADORES")
        
        categorias = [
            ('mayor_confianza', '🎯 Mayor Confianza', 'El más preciso'),
            ('mas_rapido', '⚡ Más Rápido', 'El velocista'),
            ('mas_ligero', '🪶 Más Ligero', 'El eficiente'),
            ('mas_eficiente', '⚖️ Más Eficiente', 'El balanceado')
        ]
        
        cols = st.columns(2)
        
        for i, (clave, titulo, subtitulo) in enumerate(categorias):
            col = cols[i % 2]
            
            with col:
                if clave in mejores_modelos:
                    ganador = mejores_modelos[clave]
                    nombre_arq = ganador['arquitectura']
                    info = self.informacion_arquitecturas[nombre_arq]
                    
                    if clave == 'mayor_confianza':
                        valor_metrica = f"{ganador['confianza']:.1%}"
                    elif clave == 'mas_rapido':
                        valor_metrica = f"{ganador['tiempo_prediccion']:.3f}s"
                    elif clave == 'mas_ligero':
                        valor_metrica = f"{ganador['tamaño_modelo']:.1f}MB"
                    else:  # mas_eficiente
                        valor_metrica = f"{ganador['eficiencia']:.1f}"
                    
                    # Usar diferentes tipos de alertas para cada categoría
                    if clave == 'mayor_confianza':
                        st.success(f"**{titulo}**\n\n{info['icon']} **{nombre_arq.replace('_', ' ')}**\n\n{valor_metrica}\n\n*{subtitulo}*")
                    elif clave == 'mas_rapido':
                        st.info(f"**{titulo}**\n\n{info['icon']} **{nombre_arq.replace('_', ' ')}**\n\n{valor_metrica}\n\n*{subtitulo}*")
                    elif clave == 'mas_ligero':
                        st.warning(f"**{titulo}**\n\n{info['icon']} **{nombre_arq.replace('_', ' ')}**\n\n{valor_metrica}\n\n*{subtitulo}*")
                    else:  # mas_eficiente
                        st.error(f"**{titulo}**\n\n{info['icon']} **{nombre_arq.replace('_', ' ')}**\n\n{valor_metrica}\n\n*{subtitulo}*")
    
    def mostrar_analisis_detallado(self, predicciones, mejores_modelos):
        """Análisis detallado y recomendaciones"""
        st.markdown("## 🔬 ANÁLISIS DETALLADO")
        
        # Encontrar el mejor general (combinación de métricas)
        for pred in predicciones:
            # Score combinado: 50% confianza + 25% velocidad + 25% eficiencia memoria
            max_conf = max(p['confianza'] for p in predicciones)
            min_tiempo = min(p['tiempo_prediccion'] for p in predicciones)
            min_tamaño = min(p['tamaño_modelo'] for p in predicciones)
            
            score_conf = pred['confianza'] / max_conf
            score_velocidad = min_tiempo / pred['tiempo_prediccion']
            score_memoria = min_tamaño / pred['tamaño_modelo']
            
            pred['score_general'] = 0.5 * score_conf + 0.25 * score_velocidad + 0.25 * score_memoria
        
        mejor_general = max(predicciones, key=lambda x: x['score_general'])
        
        # Mostrar ganador general
        nombre_arq = mejor_general['arquitectura']
        info = self.informacion_arquitecturas[nombre_arq]
        
        st.balloons()  # Celebración!
        st.success(f"## 👑 GANADOR GENERAL: {info['icon']} {nombre_arq.replace('_', ' ')}")
        st.metric(
            label="🏆 Score General",
            value=f"{mejor_general['score_general']:.3f}",
            delta="¡El mejor balance de todas las métricas!"
        )
        
        # Análisis por arquitectura
        st.markdown("### 📋 Fortalezas y Debilidades")
        
        for pred in predicciones:
            nombre_arq = pred['arquitectura']
            info = self.informacion_arquitecturas[nombre_arq]
            
            with st.expander(f"{info['icon']} {nombre_arq.replace('_', ' ')} - Análisis Detallado"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🟢 Fortalezas:**")
                    fortalezas = []
                    
                    if pred == mejores_modelos.get('mayor_confianza'):
                        fortalezas.append("✅ Mayor confianza de predicción")
                    if pred == mejores_modelos.get('mas_rapido'):
                        fortalezas.append("✅ Tiempo de respuesta más rápido")
                    if pred == mejores_modelos.get('mas_ligero'):
                        fortalezas.append("✅ Menor uso de memoria")
                    if pred == mejores_modelos.get('mas_eficiente'):
                        fortalezas.append("✅ Mejor relación confianza/tiempo")
                    
                    # Agregar fortalezas generales
                    for ventaja in info['ventajas']:
                        fortalezas.append(f"✅ {ventaja}")
                    
                    for fortaleza in fortalezas:
                        st.markdown(fortaleza)
                
                with col2:
                    st.markdown("**🔴 Áreas de mejora:**")
                    debilidades = []
                    
                    if pred != mejores_modelos.get('mayor_confianza'):
                        debilidades.append(f"🔸 Confianza: {pred['confianza']:.1%} vs {mejores_modelos['mayor_confianza']['confianza']:.1%}")
                    if pred != mejores_modelos.get('mas_rapido'):
                        debilidades.append(f"🔸 Velocidad: {pred['tiempo_prediccion']:.3f}s vs {mejores_modelos['mas_rapido']['tiempo_prediccion']:.3f}s")
                    if pred != mejores_modelos.get('mas_ligero'):
                        debilidades.append(f"🔸 Tamaño: {pred['tamaño_modelo']:.1f}MB vs {mejores_modelos['mas_ligero']['tamaño_modelo']:.1f}MB")
                    
                    for debilidad in debilidades:
                        st.markdown(debilidad)
                
                # Métricas técnicas
                st.markdown("**📊 Métricas Técnicas:**")
                st.markdown(f"""
                - **Parámetros**: {pred['conteo_parametros']:,}
                - **Tiempo de predicción**: {pred['tiempo_prediccion']:.3f}s
                - **Tamaño del modelo**: {pred['tamaño_modelo']:.1f}MB
                - **Eficiencia**: {pred['eficiencia']:.1f} (confianza/tiempo)
                - **Score general**: {pred['score_general']:.3f}
                """)
        
        # Recomendaciones de uso
        st.markdown("### 💡 RECOMENDACIONES DE USO")
        
        rec_col1, rec_col2, rec_col3 = st.columns(3)
        
        with rec_col1:
            st.markdown("""
            **🏥 Aplicaciones Clínicas:**
            - Usa el modelo con **mayor confianza**
            - Prioriza precisión sobre velocidad
            - Ideal para diagnósticos complejos
            """)
        
        with rec_col2:
            st.markdown("""
            **📱 Aplicaciones Móviles:**
            - Usa el modelo **más rápido y ligero**
            - Balance entre precisión y recursos
            - Ideal para apps en tiempo real
            """)
        
        with rec_col3:
            st.markdown("""
            **🔄 Sistemas de Producción:**
            - Usa el modelo **más eficiente**
            - Considera el volumen de procesamiento
            - Ideal para escalabilidad
            """)

    
    def generar_reporte_pdf_completo(self, predicciones, imagen, marca_tiempo_analisis):
        """Genera reporte PDF profesional completo"""
        try:
            # Crear PDF
            pdf = FPDF()
            pdf.add_page()
            
            # --- PORTADA ---
            pdf.set_font('Arial', 'B', 20)
            pdf.cell(0, 15, 'REPORTE DE DIAGNÓSTICO OCULAR AVANZADO', 0, 1, 'C')
            pdf.ln(5)
            
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Sistema Multi-Arquitectura CNN', 0, 1, 'C')
            pdf.ln(10)
            
            # Información general
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f'Fecha del análisis: {marca_tiempo_analisis}', 0, 1)
            pdf.cell(0, 8, f'Arquitecturas analizadas: {len(predicciones)}', 0, 1)
            pdf.cell(0, 8, f'Enfermedades detectables: 10 patologías especializadas', 0, 1)
            pdf.ln(10)
            
            # --- RESUMEN EJECUTIVO ---
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'RESUMEN EJECUTIVO', 0, 1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            
            # Encontrar ganador general
            mejor_general = max(predicciones, key=lambda x: x.get('score_general', 0))
            info_ganador = self.informacion_arquitecturas[mejor_general['arquitectura']]
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, f'ARQUITECTURA RECOMENDADA: {info_ganador["nombre_completo"]}', 0, 1)
            
            pdf.set_font('Arial', '', 11)
            clase_predicha = mejor_general['clase_predicha']
            info_clase = self.informacion_clases.get(clase_predicha, {})
            
            pdf.cell(0, 6, f'Diagnóstico principal: {info_clase.get("nombre", clase_predicha)}', 0, 1)
            pdf.cell(0, 6, f'Nivel de confianza: {mejor_general["confianza"]:.1%}', 0, 1)
            pdf.cell(0, 6, f'Gravedad: {info_clase.get("gravedad", "No especificada")}', 0, 1)
            pdf.ln(8)
            
            # Agregar imagen de manera segura
            try:
                if imagen is not None:
                    # Crear nombre único para imagen temporal
                    nombre_img_temp = f"temp_img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    
                    # Convertir y guardar imagen
                    if hasattr(imagen, 'save'):
                        # Es una imagen PIL
                        imagen_rgb = imagen.convert('RGB')
                        imagen_rgb.save(nombre_img_temp, 'JPEG', quality=85)
                    else:
                        # Crear imagen placeholder si hay problemas
                        import matplotlib.pyplot as plt
                        fig, ax = plt.subplots(1, 1, figsize=(4, 3))
                        ax.text(0.5, 0.5, 'Imagen Analizada', ha='center', va='center', fontsize=14)
                        ax.set_xlim(0, 1)
                        ax.set_ylim(0, 1)
                        ax.axis('off')
                        plt.savefig(nombre_img_temp, dpi=150, bbox_inches='tight')
                        plt.close()
                    
                    # Agregar imagen al PDF
                    pdf.cell(0, 10, 'IMAGEN ANALIZADA:', 0, 1)
                    pdf.image(nombre_img_temp, w=80)
                    pdf.ln(5)
                    
            except Exception as error_img:
                # Si hay error con la imagen, continuar sin ella
                pdf.set_font('Arial', 'I', 10)
                pdf.cell(0, 6, f'[Imagen no disponible: {str(error_img)[:50]}...]', 0, 1)
                pdf.ln(5)
            
            # --- NUEVA PÁGINA: COMPARACIÓN DE ARQUITECTURAS ---
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 12, 'COMPARACIÓN DE ARQUITECTURAS CNN', 0, 1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(8)
            
            # Tabla comparativa
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(50, 8, 'Arquitectura', 1, 0, 'C')
            pdf.cell(35, 8, 'Confianza', 1, 0, 'C')
            pdf.cell(30, 8, 'Tiempo (ms)', 1, 0, 'C')
            pdf.cell(25, 8, 'Tamaño (MB)', 1, 0, 'C')
            pdf.cell(30, 8, 'Eficiencia', 1, 1, 'C')
            
            pdf.set_font('Arial', '', 9)
            for pred in predicciones:
                nombre_arq = pred['arquitectura'].replace('_', ' ')
                pdf.cell(50, 6, nombre_arq, 1, 0)
                pdf.cell(35, 6, f"{pred['confianza']:.1%}", 1, 0, 'C')
                pdf.cell(30, 6, f"{pred['tiempo_prediccion']*1000:.1f}", 1, 0, 'C')
                pdf.cell(25, 6, f"{pred['tamaño_modelo']:.1f}", 1, 0, 'C')
                pdf.cell(30, 6, f"{pred.get('eficiencia', 0):.1f}", 1, 1, 'C')
            
            pdf.ln(10)
            
            # --- ANÁLISIS CLÍNICO DETALLADO ---
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'ANÁLISIS CLÍNICO DETALLADO', 0, 1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            
            # Para cada predicción única
            diagnosticos_unicos = list(set(pred['clase_predicha'] for pred in predicciones))
            
            for diagnostico in diagnosticos_unicos:
                info_clase = self.informacion_clases.get(diagnostico, {})
                
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 8, f'{info_clase.get("nombre", diagnostico)}', 0, 1)
                
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 5, f'Descripción: {info_clase.get("descripcion", "No disponible")}', 0, 1)
                pdf.cell(0, 5, f'Gravedad: {info_clase.get("gravedad", "No especificada")}', 0, 1)
                pdf.cell(0, 5, f'Tratamiento: {info_clase.get("tratamiento", "Consultar especialista")}', 0, 1)
                pdf.cell(0, 5, f'Pronóstico: {info_clase.get("pronostico", "Variable")}', 0, 1)
                pdf.ln(5)
            
            # --- RECOMENDACIONES TÉCNICAS ---
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 12, 'RECOMENDACIONES TÉCNICAS', 0, 1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(8)
            
            # Ganadores por categoría
            mejores_modelos = self.encontrar_mejor_arquitectura(predicciones)
            
            categorias = [
                ('mayor_confianza', 'Mayor Confianza', 'Uso clínico de alta precisión'),
                ('mas_rapido', 'Más Rápido', 'Aplicaciones tiempo real/móviles'),
                ('mas_ligero', 'Más Ligero', 'Dispositivos recursos limitados'),
                ('mas_eficiente', 'Más Eficiente', 'Sistemas de producción escalables')
            ]
            
            for clave, titulo, contexto in categorias:
                if clave in mejores_modelos:
                    ganador = mejores_modelos[clave]
                    info_arq = self.informacion_arquitecturas[ganador['arquitectura']]
                    
                    pdf.set_font('Arial', 'B', 11)
                    pdf.cell(0, 7, f'{titulo}: {info_arq["nombre_completo"]}', 0, 1)
                    pdf.set_font('Arial', '', 10)
                    pdf.cell(0, 5, f'Contexto: {contexto}', 0, 1)
                    
                    if clave == 'mayor_confianza':
                        pdf.cell(0, 5, f'Confianza: {ganador["confianza"]:.1%}', 0, 1)
                    elif clave == 'mas_rapido':
                        pdf.cell(0, 5, f'Tiempo: {ganador["tiempo_prediccion"]:.3f}s', 0, 1)
                    elif clave == 'mas_ligero':
                        pdf.cell(0, 5, f'Tamaño: {ganador["tamaño_modelo"]:.1f}MB', 0, 1)
                    else:
                        pdf.cell(0, 5, f'Eficiencia: {ganador.get("eficiencia", 0):.1f}', 0, 1)
                    
                    pdf.ln(3)
            
            # --- DISCLAIMER MÉDICO ---
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'DISCLAIMER MÉDICO', 0, 1)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(0, 4, 
                'Este reporte es generado por un sistema de inteligencia artificial y debe ser '
                'utilizado únicamente como herramienta de apoyo diagnóstico. No reemplaza el '
                'criterio clínico profesional. Se recomienda confirmación por oftalmólogo '
                'certificado antes de tomar decisiones terapéuticas.')
            
            # Generar archivo PDF
            marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo_pdf = f"reporte_diagnostico_ocular_{marca_tiempo}.pdf"
            pdf.output(nombre_archivo_pdf)
            
            # Limpiar archivo temporal de imagen si existe
            try:
                if 'nombre_img_temp' in locals() and os.path.exists(nombre_img_temp):
                    os.remove(nombre_img_temp)
            except:
                pass
            
            return nombre_archivo_pdf
            
        except Exception as e:
            st.error(f"Error generando PDF: {str(e)}")
            return None
    
    def exportar_datos_tecnicos(self, predicciones, marca_tiempo_analisis):
        """Exporta datos técnicos completos en JSON"""
        try:
            # Crear estructura de datos completa
            datos_tecnicos = {
                'metadatos': {
                    'marca_tiempo': marca_tiempo_analisis,
                    'version_sistema': '2.1 Multi-Architecture + Statistical Analysis',
                    'total_arquitecturas': len(predicciones),
                    'enfermedades_detectables': len(self.informacion_clases),
                    'tipo_analisis': 'Comparative Multi-CNN with Statistical Inference'
                },
                'comparacion_arquitecturas': [],
                'metricas_rendimiento': {},
                'analisis_clinico': {},
                'recomendaciones': {}
            }
            
            # Datos por arquitectura
            for pred in predicciones:
                datos_arq = {
                    'nombre_arquitectura': pred['arquitectura'],
                    'info_modelo': self.informacion_arquitecturas[pred['arquitectura']],
                    'resultados_prediccion': {
                        'clase_predicha': pred['clase_predicha'],
                        'confianza': float(pred['confianza']),
                        'todas_probabilidades': [float(p) for p in pred['todas_probabilidades']],
                        'tiempo_prediccion_segundos': float(pred['tiempo_prediccion']),
                        'tamaño_modelo_mb': float(pred['tamaño_modelo']),
                        'conteo_parametros': int(pred['conteo_parametros']),
                        'score_eficiencia': float(pred.get('eficiencia', 0)),
                        'score_general': float(pred.get('score_general', 0))
                    },
                    'info_clinica': self.informacion_clases.get(pred['clase_predicha'], {})
                }
                datos_tecnicos['comparacion_arquitecturas'].append(datos_arq)
            
            # Métricas de rendimiento
            confianzas = [pred['confianza'] for pred in predicciones]
            tiempos = [pred['tiempo_prediccion'] for pred in predicciones]
            tamaños = [pred['tamaño_modelo'] for pred in predicciones]
            
            datos_tecnicos['metricas_rendimiento'] = {
                'estadisticas_confianza': {
                    'media': float(np.mean(confianzas)),
                    'desviacion_estandar': float(np.std(confianzas)),
                    'minimo': float(np.min(confianzas)),
                    'maximo': float(np.max(confianzas))
                },
                'estadisticas_tiempo': {
                    'media_ms': float(np.mean(tiempos) * 1000),
                    'desviacion_estandar_ms': float(np.std(tiempos) * 1000),
                    'mas_rapido_ms': float(np.min(tiempos) * 1000),
                    'mas_lento_ms': float(np.max(tiempos) * 1000)
                },
                'estadisticas_tamaño': {
                    'media_mb': float(np.mean(tamaños)),
                    'desviacion_estandar_mb': float(np.std(tamaños)),
                    'mas_ligero_mb': float(np.min(tamaños)),
                    'mas_pesado_mb': float(np.max(tamaños))
                }
            }
            
            # Análisis clínico
            diagnosticos = [pred['clase_predicha'] for pred in predicciones]
            diagnosticos_unicos = list(set(diagnosticos))
            
            datos_tecnicos['analisis_clinico'] = {
                'diagnosticos_unicos': len(diagnosticos_unicos),
                'diagnostico_consenso': max(set(diagnosticos), key=diagnosticos.count) if diagnosticos else None,
                'acuerdo_diagnostico': (diagnosticos.count(max(set(diagnosticos), key=diagnosticos.count)) / len(diagnosticos)) if diagnosticos else 0,
                'distribucion_gravedad': {
                    diagnostico: self.informacion_clases.get(diagnostico, {}).get('gravedad', 'Desconocida')
                    for diagnostico in diagnosticos_unicos
                }
            }
            
            # Recomendaciones
            mejores_modelos = self.encontrar_mejor_arquitectura(predicciones)
            datos_tecnicos['recomendaciones'] = {
                categoria: {
                    'arquitectura': datos_modelo['arquitectura'],
                    'razon': f'Mejor {categoria.replace("_", " ")}',
                    'valor_metrica': datos_modelo.get('confianza' if 'confianza' in categoria else 
                                                  'tiempo_prediccion' if 'rapido' in categoria else
                                                  'tamaño_modelo' if 'ligero' in categoria else 'eficiencia', 0)
                }
                for categoria, datos_modelo in mejores_modelos.items()
            }
            
            # Guardar archivo JSON
            marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo_json = f"analisis_tecnico_{marca_tiempo}.json"
            
            with open(nombre_archivo_json, 'w', encoding='utf-8') as f:
                json.dump(datos_tecnicos, f, indent=2, ensure_ascii=False)
            
            return nombre_archivo_json
            
        except Exception as e:
            st.error(f"Error exportando datos técnicos: {str(e)}")
            return None
    
    def mostrar_seccion_reportes_avanzados(self, predicciones, imagen, marca_tiempo_analisis):
        """Sección avanzada de reportes y exportación"""
        st.markdown("---")
        st.header("📋 SISTEMA AVANZADO DE REPORTES")
        
        # Métricas de cobertura del sistema
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🏥 Enfermedades Detectables",
                value="10",
                delta="6 más que sistemas básicos",
                help="Nuestro sistema detecta 10 vs 4 de sistemas convencionales"
            )
        
        with col2:
            st.metric(
                label="🧠 Arquitecturas CNN",
                value=len(predicciones),
                delta="Análisis multi-arquitectura",
                help="Comparación simultánea de múltiples modelos"
            )
        
        with col3:
            diagnosticos_unicos = len(set(pred['clase_predicha'] for pred in predicciones))
            st.metric(
                label="🎯 Diagnósticos Únicos",
                value=diagnosticos_unicos,
                delta="En este análisis",
                help="Número de diagnósticos diferentes detectados"
            )
        
        with col4:
            confianza_promedio = np.mean([pred['confianza'] for pred in predicciones])
            st.metric(
                label="📊 Confianza Promedio",
                value=f"{confianza_promedio:.1%}",
                delta=f"±{np.std([pred['confianza'] for pred in predicciones]):.1%}",
                help="Confianza promedio entre todas las arquitecturas"
            )
        
        # Sección de exportación
        st.markdown("### 📤 Exportar Análisis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Generar Reporte PDF Completo", type="primary", use_container_width=True, key="boton_pdf"):
                try:
                    estado_pdf = st.empty()
                    estado_pdf.info("🔄 Generando reporte PDF profesional...")
                    archivo_pdf = self.generar_reporte_pdf_completo(predicciones, imagen, marca_tiempo_analisis)
                    
                    if archivo_pdf and os.path.exists(archivo_pdf):
                        estado_pdf.success("✅ PDF generado exitosamente!")
                        
                        with open(archivo_pdf, "rb") as f:
                            bytes_pdf = f.read()
                        
                        st.download_button(
                            label="⬇️ DESCARGAR REPORTE PDF",
                            data=bytes_pdf,
                            file_name=f"reporte_diagnostico_ocular_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                            key="descargar_pdf"
                        )
                        
                        st.balloons()
                        
                        try:
                            os.remove(archivo_pdf)
                        except:
                            pass
                    else:
                        st.error("❌ Error generando el reporte PDF")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        with col2:
            if st.button("📊 Exportar Datos Técnicos (JSON)", use_container_width=True, key="boton_json"):
                try:
                    estado_json = st.empty()
                    estado_json.info("🔄 Exportando datos técnicos...")
                    
                    archivo_json = self.exportar_datos_tecnicos(predicciones, marca_tiempo_analisis)
                    
                    if archivo_json and os.path.exists(archivo_json):
                        estado_json.success("✅ Datos técnicos exportados!")
                        
                        with open(archivo_json, "r", encoding='utf-8') as f:
                            datos_json = f.read()
                        
                        st.download_button(
                            label="⬇️ DESCARGAR DATOS JSON",
                            data=datos_json,
                            file_name=f"analisis_tecnico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True,
                            key="descargar_json"
                        )
                        
                        try:
                            os.remove(archivo_json)
                        except:
                            pass
                    else:
                        st.error("❌ Error exportando datos técnicos")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        with col3:
            if st.button("📈 Exportar CSV Comparativo", use_container_width=True, key="boton_csv"):
                try:
                    estado_csv = st.empty()
                    estado_csv.info("🔄 Preparando CSV...")
                    
                    df_exportar = pd.DataFrame([
                        {
                            'Marca_Tiempo': marca_tiempo_analisis,
                            'Arquitectura': pred['arquitectura'].replace('_', ' '),
                            'Diagnóstico': pred['clase_predicha'],
                            'Diagnóstico_ES': self.informacion_clases.get(pred['clase_predicha'], {}).get('nombre', pred['clase_predicha']),
                            'Confianza': pred['confianza'],
                            'Tiempo_ms': pred['tiempo_prediccion'] * 1000,
                            'Tamaño_MB': pred['tamaño_modelo'],
                            'Parámetros': pred['conteo_parametros'],
                            'Eficiencia': pred.get('eficiencia', 0),
                            'Score_General': pred.get('score_general', 0),
                            'Gravedad': self.informacion_clases.get(pred['clase_predicha'], {}).get('gravedad', 'No especificada')
                        }
                        for pred in predicciones
                    ])
                    
                    datos_csv = df_exportar.to_csv(index=False, encoding='utf-8')
                    estado_csv.success("✅ CSV listo!")
                    
                    st.download_button(
                        label="⬇️ DESCARGAR CSV",
                        data=datos_csv,
                        file_name=f"analisis_comparativo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="descargar_csv"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Información adicional sobre las descargas
        st.markdown("---")
        st.info("""
        💡 **Información sobre las descargas:**
        - **PDF**: Reporte completo con análisis clínico y recomendaciones técnicas
        - **JSON**: Datos técnicos estructurados para análisis posterior 
        - **CSV**: Tabla comparativa simple para Excel/análisis estadístico
        
        📁 Los archivos se descargan automáticamente a tu carpeta de Descargas
        """)
    
    # ========== FUNCIÓN EJECUTAR PRINCIPAL (MODIFICADA) ==========
    def ejecutar(self):
        """Ejecuta la aplicación principal CON ANÁLISIS ESTADÍSTICO"""
        # Inicializar session state
        if 'analisis_completado' not in st.session_state:
            st.session_state.analisis_completado = False
        if 'predicciones' not in st.session_state:
            st.session_state.predicciones = None
        if 'imagen_analisis' not in st.session_state:
            st.session_state.imagen_analisis = None
        if 'marca_tiempo_analisis' not in st.session_state:
            st.session_state.marca_tiempo_analisis = None
        if 'resultados_estadisticos' not in st.session_state:
            st.session_state.resultados_estadisticos = None
        
        # Header
        self.mostrar_encabezado()
        
        # Sidebar
        st.sidebar.markdown("## 🎛️ Panel de Control")
        st.sidebar.markdown("---")
        
        # Cargar modelos
        if self.modelos is None:
            with st.spinner("🔄 Cargando las 3 arquitecturas..."):
                self.modelos, self.nombres_clases, self.nombres_clases_individuales = self.cargar_modelos()
        
        if len(self.modelos) < 2:
            st.error("❌ Se necesitan al menos 2 modelos para comparar")
            st.stop()
        
        # Info en sidebar
        st.sidebar.success(f"✅ {len(self.modelos)} arquitecturas cargadas")
        
        # Pestañas principales
        tab1, tab2 = st.tabs(["🔬 Análisis Individual", "📊 Evaluación Estadística"])
        
        with tab1:
            # Botón para limpiar análisis
            if st.sidebar.button("🔄 Nuevo Análisis", help="Limpia el análisis actual"):
                st.session_state.analisis_completado = False
                st.session_state.predicciones = None
                st.session_state.imagen_analisis = None
                st.session_state.marca_tiempo_analisis = None
                st.rerun()
            
            # Mostrar características
            self.mostrar_vitrina_arquitecturas()
            
            st.markdown("---")
            
            # Si ya hay un análisis completo, mostrar resultados
            if st.session_state.analisis_completado and st.session_state.predicciones:
                st.success("🎉 **Análisis ya completado!** Puedes descargar los reportes o hacer un nuevo análisis.")
                
                # Mostrar imagen analizada
                if st.session_state.imagen_analisis:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.image(st.session_state.imagen_analisis, caption="Imagen analizada", use_container_width=True)
                
                # Mostrar todos los resultados usando el estado guardado
                predicciones = st.session_state.predicciones
                
                self.mostrar_resultados_prediccion(predicciones)
                st.markdown("---")
                self.mostrar_comparacion_rendimiento(predicciones)
                st.markdown("---")
                self.mostrar_comparacion_radar(predicciones)
                
                mejores_modelos = self.encontrar_mejor_arquitectura(predicciones)
                st.markdown("---")
                self.mostrar_podio_ganadores(mejores_modelos)
                st.markdown("---")
                self.mostrar_analisis_detallado(predicciones, mejores_modelos)
                
                # SECCIÓN DE REPORTES AVANZADOS
                self.mostrar_seccion_reportes_avanzados(predicciones, st.session_state.imagen_analisis, st.session_state.marca_tiempo_analisis)
                
                # Tabla resumen
                with st.expander("📊 Tabla Resumen de Métricas"):
                    df_resumen = pd.DataFrame([
                        {
                            'Arquitectura': pred['arquitectura'].replace('_', ' '),
                            'Diagnóstico': pred['clase_predicha'],
                            'Diagnóstico_ES': self.informacion_clases.get(pred['clase_predicha'], {}).get('nombre', pred['clase_predicha']),
                            'Confianza': f"{pred['confianza']:.1%}",
                            'Tiempo': f"{pred['tiempo_prediccion']:.3f}s",
                            'Tamaño': f"{pred['tamaño_modelo']:.1f}MB",
                            'Parámetros': f"{pred['conteo_parametros']:,}",
                            'Eficiencia': f"{pred.get('eficiencia', 0):.1f}",
                            'Score General': f"{pred.get('score_general', 0):.3f}",
                            'Gravedad': self.informacion_clases.get(pred['clase_predicha'], {}).get('gravedad', 'No especificada')
                        }
                        for pred in predicciones
                    ])
                    
                    st.dataframe(df_resumen, use_container_width=True)
                
                # Timestamp
                st.markdown("---")
                st.markdown(f"📅 Análisis realizado: {st.session_state.marca_tiempo_analisis}")
                
            else:
                # Interfaz para nuevo análisis
                st.markdown("## 📸 Subir Imagen para Comparar Arquitecturas")
                archivo_subido = st.file_uploader(
                    "Selecciona una imagen de retina para la batalla de arquitecturas",
                    type=['png', 'jpg', 'jpeg'],
                    help="La imagen será analizada por las 3 arquitecturas simultáneamente"
                )
                
                if archivo_subido is not None:
                    # Mostrar imagen
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        imagen = Image.open(archivo_subido)
                        st.image(imagen, caption="Imagen para la batalla", use_container_width=True)
                    
                    # Botón de análisis
                    if st.button("🚀 INICIAR BATALLA DE ARQUITECTURAS", type="primary", use_container_width=True):
                        
                        marca_tiempo_analisis = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Preprocesamiento y predicciones
                        with st.spinner("🔄 Procesando imagen para todas las arquitecturas..."):
                            array_img = self.preprocesar_imagen(imagen)
                        
                        if array_img is not None:
                            predicciones = []
                            
                            with st.spinner("🏗️ Analizando con las 3 arquitecturas..."):
                                barra_progreso = st.progress(0)
                                
                                for i, (nombre_arq, modelo) in enumerate(self.modelos.items()):
                                    pred = self.predecir_con_cronometraje(modelo, array_img, nombre_arq)
                                    if pred:
                                        predicciones.append(pred)
                                    barra_progreso.progress((i + 1) / len(self.modelos))
                            
                            if len(predicciones) >= 2:
                                st.success("✅ ¡Batalla completada! Analizando resultados...")
                                
                                # Calcular scores adicionales
                                for pred in predicciones:
                                    max_conf = max(p['confianza'] for p in predicciones)
                                    min_tiempo = min(p['tiempo_prediccion'] for p in predicciones)
                                    min_tamaño = min(p['tamaño_modelo'] for p in predicciones)
                                    
                                    score_conf = pred['confianza'] / max_conf
                                    score_velocidad = min_tiempo / pred['tiempo_prediccion']
                                    score_memoria = min_tamaño / pred['tamaño_modelo']
                                    
                                    pred['score_general'] = 0.5 * score_conf + 0.25 * score_velocidad + 0.25 * score_memoria
                                    pred['eficiencia'] = pred['confianza'] / pred['tiempo_prediccion']
                                
                                # GUARDAR EN SESSION STATE
                                st.session_state.predicciones = predicciones
                                st.session_state.imagen_analisis = imagen
                                st.session_state.marca_tiempo_analisis = marca_tiempo_analisis
                                st.session_state.analisis_completado = True
                                
                                # Forzar rerun para mostrar resultados
                                st.rerun()
                            
                            else:
                                st.error("❌ Error en las predicciones")
        
        with tab2:
            # NUEVA PESTAÑA: ANÁLISIS ESTADÍSTICO
            self.mostrar_seccion_analisis_estadistico()
        
        # Footer técnico (expandido)
        st.markdown("---")
        st.markdown("""
        ### ⚙️ Sobre Este Sistema Avanzado con Análisis Estadístico
        
        **🚀 Sistema de Diagnóstico Ocular de Nueva Generación**
        
        **🔬 Nuevas Funcionalidades Estadísticas:**
        - **📊 Coeficiente de Matthews (MCC)**: Métrica balanceada para clases desbalanceadas
        - **🔬 Prueba de McNemar**: Comparación estadística rigurosa entre modelos
        - **📈 Intervalos de Confianza Bootstrap**: Robustez estadística (95% CI)
        - **🎭 Matrices de Confusión**: Análisis detallado por clase
        - **📋 Reportes Estadísticos**: Exportación completa de resultados
        
        **🔬 Ventajas Competitivas:**
        - **10 enfermedades especializadas** vs 4 básicas de sistemas convencionales
        - **Análisis multi-arquitectura** con comparación simultánea de CNNs
        - **Evaluación estadística rigurosa** con pruebas de significancia
        - **Reportes profesionales PDF** con análisis clínico y estadístico
        - **Exportación técnica completa** (JSON, CSV, TXT) para investigación
        - **Recomendaciones contextuales** basadas en evidencia estadística
        
        **🏗️ Arquitecturas Implementadas:**
        - **🧠 CNN Híbrida (MobileNetV2)**: Transfer Learning especializado
        - **⚡ EfficientNet-B0**: Compound Scaling balanceado
        - **🔗 ResNet-50 V2**: Conexiones residuales profundas
        
        **📊 Métricas Evaluadas:**
        - 🎯 **Precisión**: Confianza, MCC y consenso diagnóstico
        - ⚡ **Velocidad**: Tiempo de inferencia optimizado
        - 💾 **Eficiencia**: Uso de memoria y escalabilidad
        - 🏆 **Balance**: Score general multi-criterio
        - 📈 **Significancia**: Pruebas estadísticas inferenciales
        
        **🎯 Aplicaciones:**
        - 🏥 **Clínicas**: Diagnóstico de alta precisión con validación estadística
        - 📱 **Móviles**: Apps de telemedicina con métricas robustas
        - 🔄 **Producción**: Sistemas hospitalarios escalables con evidencia estadística
        - 🔬 **Investigación**: Datos completos para publicaciones científicas
        
        **💡 Innovación**: Primer sistema que combina múltiples arquitecturas CNN con 
        análisis estadístico inferencial completo para diagnóstico ocular especializado.
        
        **📚 Métodos Estadísticos:**
        - **MCC**: Coeficiente de Correlación de Matthews para métricas balanceadas
        - **McNemar**: Prueba chi-cuadrado para comparación de clasificadores
        - **Bootstrap**: Intervalos de confianza no paramétricos
        - **Corrección de Yates**: Para muestras pequeñas en McNemar
        """)

# Ejecutar aplicación
if __name__ == "__main__":
    aplicacion = AplicacionTresArquitecturas()
    aplicacion.ejecutar()