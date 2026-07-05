

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
from sklearn.metrics import matthews_corrcoef, confusion_matrix, classification_report, roc_curve, auc, roc_auc_score
from sklearn.preprocessing import label_binarize
from scipy.stats import chi2
from scipy import stats
import itertools
from pathlib import Path
from translations import get_text, get_available_languages
import download_models

warnings.filterwarnings('ignore')

# Configuración de página
def configurar_pagina(lang='es'):
    st.set_page_config(
        page_title=get_text('page_title', lang),
        page_icon="👁️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Agregar selector de idioma en el sidebar
def mostrar_selector_idioma():
    if 'language' not in st.session_state:
        st.session_state.language = 'es'
    
    languages = get_available_languages()
    
    current_index = list(languages.keys()).index(st.session_state.language) if st.session_state.language in languages else 0
    
    selected_lang = st.sidebar.selectbox(
        get_text('select_language', st.session_state.language),
        options=list(languages.keys()),
        format_func=lambda x: languages[x],
        index=current_index,
        key="language_selector"
    )
    
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()
    
    return st.session_state.language

class AplicacionMetodologiasHibridas:    
    def __init__(self):
        # Inicializar idioma
        if 'language' not in st.session_state:
            st.session_state.language = 'es'
        self.lang = st.session_state.language
        
        # ========== METODOLOGÍAS HÍBRIDAS: ResNet50V2 + MobileNet + CNN Original ==========
        self.informacion_arquitecturas = {
            # METODOLOGÍA HÍBRIDA 1: ResNet50V2 + CLAHE + Data Augmentation
            'ResNet50V2': {
                'nombre_completo': get_text('hybrid_resnet_name', self.lang),
                'descripcion': get_text('hybrid_resnet_desc', self.lang),
                'color': '#E91E63',
                'icon': '🧬',
                'ventajas': [
                    get_text('hybrid_resnet_advantage1', self.lang),
                    get_text('hybrid_resnet_advantage2', self.lang),
                    get_text('hybrid_resnet_advantage3', self.lang),
                    get_text('hybrid_resnet_advantage4', self.lang)
                ],
                'caracteristicas': {
                    get_text('type', self.lang): get_text('hybrid_resnet_type', self.lang),
                    get_text('parameters_count', self.lang): '~25.6M + CLAHE',
                    get_text('main_advantage', self.lang): get_text('hybrid_resnet_main_advantage', self.lang),
                    get_text('year', self.lang): get_text('hybrid_year', self.lang),
                    get_text('preprocessing', self.lang): get_text('hybrid_preprocessing', self.lang)
                }
            },
            # METODOLOGÍA HÍBRIDA 2: MobileNet + CLAHE + Data Augmentation  
            'CNN_Original': {
                'nombre_completo': get_text('hybrid_mobilenet_name', self.lang),
                'descripcion': get_text('hybrid_mobilenet_desc', self.lang),
                'color': '#00BCD4',
                'icon': '🔬',
                'ventajas': [
                    get_text('hybrid_mobilenet_advantage1', self.lang),
                    get_text('hybrid_mobilenet_advantage2', self.lang),
                    get_text('hybrid_mobilenet_advantage3', self.lang),
                    get_text('hybrid_mobilenet_advantage4', self.lang)
                ],
                'caracteristicas': {
                    get_text('type', self.lang): get_text('hybrid_mobilenet_type', self.lang),
                    get_text('parameters_count', self.lang): '~3.5M + CLAHE',
                    get_text('main_advantage', self.lang): get_text('hybrid_mobilenet_main_advantage', self.lang),
                    get_text('year', self.lang): get_text('hybrid_year', self.lang),
                    get_text('preprocessing', self.lang): get_text('hybrid_preprocessing', self.lang)
                }
            },
            # GRUPO CONTROL: EfficientNetB0 sin metodología híbrida
            'EfficientNetB0': {
                'nombre_completo': get_text('control_efficientnet_name', self.lang),
                'descripcion': get_text('control_efficientnet_desc', self.lang),
                'color': '#FF9800',
                'icon': '🧠',
                'ventajas': [
                    get_text('control_efficientnet_advantage1', self.lang),
                    get_text('control_efficientnet_advantage2', self.lang),
                    get_text('control_efficientnet_advantage3', self.lang)
                ],
                'caracteristicas': {
                    get_text('type', self.lang): get_text('control_efficientnet_type', self.lang),
                    get_text('parameters_count', self.lang): '~5.3M',
                    get_text('main_advantage', self.lang): get_text('control_efficientnet_main_advantage', self.lang),
                    get_text('year', self.lang): '2019',
                    get_text('preprocessing', self.lang): get_text('standard_preprocessing', self.lang)
                }
            }
        }
        
        # Mantener información de clases original
        self.informacion_clases = {
            'Central Serous Chorioretinopathy [Color Fundus]': {
                'nombre': get_text('CentralSerous_nombre', self.lang),
                'descripcion': get_text('CentralSerous_descripcion', self.lang),
                'gravedad': get_text('CentralSerous_gravedad', self.lang),
                'color': '#FFA07A',
                'tratamiento': get_text('CentralSerous_tratamiento', self.lang),
                'pronostico': get_text('CentralSerous_pronostico', self.lang)
            },
            'Diabetic Retinopathy': {
                'nombre': get_text('Diabetic_nombre', self.lang),
                'descripcion': get_text('Diabetic_descripcion', self.lang),
                'gravedad': get_text('Diabetic_gravedad', self.lang),
                'color': '#FF6B6B',
                'tratamiento': get_text('Diabetic_tratamiento', self.lang),
                'pronostico': get_text('Diabetic_pronostico', self.lang)
            },
            'Disc Edema': {
                'nombre': get_text('DiscEdema_nombre', self.lang),
                'descripcion': get_text('DiscEdema_descripcion', self.lang),
                'gravedad': get_text('DiscEdema_gravedad', self.lang),
                'color': '#FF4444',
                'tratamiento': get_text('DiscEdema_tratamiento', self.lang),
                'pronostico': get_text('DiscEdema_pronostico', self.lang)
            },
            'Glaucoma': {
                'nombre': get_text('Glaucoma_nombre', self.lang),
                'descripcion': get_text('Glaucoma_descripcion', self.lang),
                'gravedad': get_text('Glaucoma_gravedad', self.lang),
                'color': '#DC143C',
                'tratamiento': get_text('Glaucoma_tratamiento', self.lang),
                'pronostico': get_text('Glaucoma_pronostico', self.lang)
            },
            'Healthy': {
                'nombre': get_text('Healthy_nombre', self.lang),
                'descripcion': get_text('Healthy_descripcion', self.lang),
                'gravedad': get_text('Healthy_gravedad', self.lang),
                'color': '#32CD32',
                'tratamiento': get_text('Healthy_tratamiento', self.lang),
                'pronostico': get_text('Healthy_pronostico', self.lang)
            },
            'Macular Scar': {
                'nombre': get_text('MacularScar_nombre', self.lang),
                'descripcion': get_text('MacularScar_descripcion', self.lang),
                'gravedad': get_text('MacularScar_gravedad', self.lang),
                'color': '#DAA520',
                'tratamiento': get_text('MacularScar_tratamiento', self.lang),
                'pronostico': get_text('MacularScar_pronostico', self.lang)
            },
            'Myopia': {
                'nombre': get_text('Myopia_nombre', self.lang),
                'descripcion': get_text('Myopia_descripcion', self.lang),
                'gravedad': get_text('Myopia_gravedad', self.lang),
                'color': '#87CEEB',
                'tratamiento': get_text('Myopia_tratamiento', self.lang),
                'pronostico': get_text('Myopia_pronostico', self.lang)
            },
            'Pterygium': {
                'nombre': get_text('Pterygium_nombre', self.lang),
                'descripcion': get_text('Pterygium_descripcion', self.lang),
                'gravedad': get_text('Pterygium_gravedad', self.lang),
                'color': '#DDA0DD',
                'tratamiento': get_text('Pterygium_tratamiento', self.lang),
                'pronostico': get_text('Pterygium_pronostico', self.lang)
            },
            'Retinal Detachment': {
                'nombre': get_text('RetinalDetachment_nombre', self.lang),
                'descripcion': get_text('RetinalDetachment_descripcion', self.lang),
                'gravedad': get_text('RetinalDetachment_gravedad', self.lang),
                'color': '#B22222',
                'tratamiento': get_text('RetinalDetachment_tratamiento', self.lang),
                'pronostico': get_text('RetinalDetachment_pronostico', self.lang)
            },
            'Retinitis Pigmentosa': {
                'nombre': get_text('Retinitis_nombre', self.lang),
                'descripcion': get_text('Retinitis_descripcion', self.lang),
                'gravedad': get_text('Retinitis_gravedad', self.lang),
                'color': '#8B0000',
                'tratamiento': get_text('Retinitis_tratamiento', self.lang),
                'pronostico': get_text('Retinitis_pronostico', self.lang)
            }
        }
        
        self.modelos = None
        self.nombres_clases = None
        self.nombres_clases_individuales = None
        self.analisis_actual = None
        self.resultados_estadisticos = None
        
        # Parámetros técnicos para el informe
        self.parametros_clahe = {
            'clipLimit': 2.5,
            'tileGridSize': (8, 8),
            'colorSpace': 'LAB',
            'channels': ['L', 'Green'],
            'normalization': 'NORM_MINMAX',
            'description': get_text('clahe_technical_desc', self.lang)
        }
        
        self.parametros_augmentation = {
            'rotation_range': 15,  # ±15° exacto
            'zoom_range_resnet': 0.1,     # 10% para ResNet
            'zoom_range_mobilenet': 0.05,  # 5% para MobileNet
            'shift_range_resnet': 0.08,    # 8% para ResNet
            'shift_range_mobilenet': 0.05, # 5% para MobileNet
            'border_mode': 'BORDER_REFLECT_101',
            'interpolation': 'INTER_CUBIC',
            'description': get_text('augmentation_technical_desc', self.lang)
        }
    
    # ========== FUNCIONES METODOLOGÍA HÍBRIDA ==========
    
    def aplicar_clahe_normalizado(self, imagen_pil):
        """
        Aplicación de CLAHE (Contrast Limited Adaptive Histogram Equalization)
        Parámetros técnicos optimizados para imágenes oftalmológicas
        """
        try:
            img_array = np.array(imagen_pil)
            
            # Log técnico para el informe
            st.sidebar.info(get_text('applying_clahe', self.lang))
            
            if len(img_array.shape) == 3:
                # Conversión a espacio de color LAB para mejor procesamiento CLAHE
                img_lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
                
                # Configuración CLAHE con parámetros específicos
                clahe = cv2.createCLAHE(
                    clipLimit=self.parametros_clahe['clipLimit'],        # 2.5 - límite de contraste
                    tileGridSize=self.parametros_clahe['tileGridSize']   # (8,8) - regiones adaptativas
                )
                
                # Aplicar CLAHE al canal L (luminancia)
                img_lab[:,:,0] = clahe.apply(img_lab[:,:,0])
                
                # Convertir de vuelta a RGB
                img_enhanced = cv2.cvtColor(img_lab, cv2.COLOR_LAB2RGB)
                
                # Mejora adicional en canal verde (crítico en oftalmología)
                img_enhanced[:,:,1] = clahe.apply(img_enhanced[:,:,1])
                
            else:
                # Para escala de grises
                clahe = cv2.createCLAHE(
                    clipLimit=self.parametros_clahe['clipLimit'], 
                    tileGridSize=self.parametros_clahe['tileGridSize']
                )
                img_enhanced = clahe.apply(img_array)
            
            # Normalización final
            img_enhanced = cv2.normalize(img_enhanced, None, 0, 255, cv2.NORM_MINMAX)
            
            return Image.fromarray(img_enhanced.astype(np.uint8))
            
        except Exception as e:
            st.error(f"{get_text('clahe_error', self.lang)}: {str(e)}")
            return imagen_pil
    
    def aplicar_data_augmentation_hibrido(self, imagen_pil, arquitectura='ResNet50V2'):
        """
        Data Augmentation con parámetros específicos por arquitectura
        - Rotaciones ±15° (exacto según especificaciones)
        - Zoom y desplazamientos variables por arquitectura
        """
        try:
            img_array = np.array(imagen_pil)
            h, w = img_array.shape[:2]
            
            st.sidebar.info(get_text('applying_augmentation', self.lang, arch=arquitectura))
            
            # Parámetros específicos por arquitectura híbrida
            if arquitectura == 'ResNet50V2':
                zoom_range = self.parametros_augmentation['zoom_range_resnet']      # 10%
                shift_range = self.parametros_augmentation['shift_range_resnet']    # 8%
            elif arquitectura == 'CNN_Original':  # MobileNet híbrido
                zoom_range = self.parametros_augmentation['zoom_range_mobilenet']   # 5%
                shift_range = self.parametros_augmentation['shift_range_mobilenet'] # 5%
            else:
                zoom_range = 0.05
                shift_range = 0.05
            
            rotation_range = self.parametros_augmentation['rotation_range']  # ±15° fijo
            
            # 1. ROTACIÓN ±15° (parámetro crítico del profesor)
            center = (w//2, h//2)
            angle = np.random.uniform(-rotation_range, rotation_range)
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            
            img_rotated = cv2.warpAffine(
                img_array, rotation_matrix, (w, h),
                borderMode=cv2.BORDER_REFLECT_101
            )
            
            # 2. ZOOM con preservación de aspectos médicos
            zoom_factor = np.random.uniform(1-zoom_range, 1+zoom_range)
            new_h, new_w = int(h * zoom_factor), int(w * zoom_factor)
            
            img_zoomed = cv2.resize(img_rotated, (new_w, new_h), 
                                  interpolation=cv2.INTER_CUBIC)
            
            # Ajuste de tamaño
            if zoom_factor > 1:
                start_h = (new_h - h) // 2
                start_w = (new_w - w) // 2
                img_zoomed = img_zoomed[start_h:start_h+h, start_w:start_w+w]
            else:
                pad_h = (h - new_h) // 2
                pad_w = (w - new_w) // 2
                pad_h_extra = h - new_h - pad_h
                pad_w_extra = w - new_w - pad_w
                img_zoomed = cv2.copyMakeBorder(
                    img_zoomed, pad_h, pad_h_extra, pad_w, pad_w_extra, 
                    cv2.BORDER_REFLECT_101
                )
            
            # 3. DESPLAZAMIENTOS
            shift_x = int(np.random.uniform(-shift_range, shift_range) * w)
            shift_y = int(np.random.uniform(-shift_range, shift_range) * h)
            
            translation_matrix = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
            img_shifted = cv2.warpAffine(
                img_zoomed, translation_matrix, (w, h),
                borderMode=cv2.BORDER_REFLECT_101
            )
            
            return Image.fromarray(img_shifted.astype(np.uint8))
            
        except Exception as e:
            st.error(f"{get_text('augmentation_error', self.lang)}: {str(e)}")
            return imagen_pil
    
    def preprocesar_imagen_metodologia_hibrida(self, imagen, arquitectura='standard'):
        """
        Pipeline completo de preprocesamiento híbrido
        """
        try:
            if imagen.mode != 'RGB':
                imagen = imagen.convert('RGB')
            
            # Aplicar metodología híbrida según arquitectura
            if arquitectura == 'ResNet50V2':
                st.sidebar.success(get_text('applying_hybrid_resnet', self.lang))
                imagen = self.aplicar_clahe_normalizado(imagen)
                imagen = self.aplicar_data_augmentation_hibrido(imagen, 'ResNet50V2')
                
            elif arquitectura == 'CNN_Original':  # MobileNet híbrido
                st.sidebar.success(get_text('applying_hybrid_mobilenet', self.lang))
                imagen = self.aplicar_clahe_normalizado(imagen)
                imagen = self.aplicar_data_augmentation_hibrido(imagen, 'CNN_Original')
                
            else:  # EfficientNetB0 - Control sin metodología híbrida
                st.sidebar.info(get_text('applying_control', self.lang))
            
            # Preprocesamiento final estándar
            imagen = imagen.resize((224, 224))
            array_img = np.array(imagen)
            array_img = array_img.astype('float32') / 255.0
            array_img = np.expand_dims(array_img, axis=0)
            
            return array_img
            
        except Exception as e:
            st.error(f"{get_text('preprocessing_error', self.lang)}: {str(e)}")
            return None
    
    def generar_informe_tecnico_parametros(self):
        """
        Genera informe técnico detallado de parámetros para el artículo
        """
        informe = f"""
        {get_text('technical_report_title', self.lang)}
        
        {get_text('hybrid_methodologies_title', self.lang)}:
        
        1. {get_text('hybrid_methodology_1', self.lang)}
           - {get_text('base_architecture', self.lang)}: ResNet-50 V2
           - {get_text('parameters_count', self.lang)}: ~25.6M
           - {get_text('methodology', self.lang)}: CLAHE + Data Augmentation
        
        2. {get_text('hybrid_methodology_2', self.lang)}
           - {get_text('base_architecture', self.lang)}: MobileNetV2 
           - {get_text('parameters_count', self.lang)}: ~3.5M
           - {get_text('methodology', self.lang)}: CLAHE + Data Augmentation
        
        3. {get_text('control_group', self.lang)}
           - {get_text('base_architecture', self.lang)}: EfficientNet-B0
           - {get_text('parameters_count', self.lang)}: ~5.3M
           - {get_text('methodology', self.lang)}: {get_text('standard_preprocessing', self.lang)}
        
        {get_text('clahe_parameters_title', self.lang)}:
        - clipLimit: {self.parametros_clahe['clipLimit']}
        - tileGridSize: {self.parametros_clahe['tileGridSize']}
        - {get_text('color_space', self.lang)}: {self.parametros_clahe['colorSpace']}
        - {get_text('normalization', self.lang)}: {self.parametros_clahe['normalization']}
        
        {get_text('augmentation_parameters_title', self.lang)}:
        - {get_text('rotation_range', self.lang)}: ±{self.parametros_augmentation['rotation_range']}°
        - Zoom ResNet: ±{self.parametros_augmentation['zoom_range_resnet']*100}%
        - Zoom MobileNet: ±{self.parametros_augmentation['zoom_range_mobilenet']*100}%
        - {get_text('shift_range', self.lang)} ResNet: ±{self.parametros_augmentation['shift_range_resnet']*100}%
        - {get_text('shift_range', self.lang)} MobileNet: ±{self.parametros_augmentation['shift_range_mobilenet']*100}%
        - {get_text('border_mode', self.lang)}: {self.parametros_augmentation['border_mode']}
        - {get_text('interpolation', self.lang)}: {self.parametros_augmentation['interpolation']}
        """
        
        return informe
    
    # ========== FUNCIONES EXISTENTES ADAPTADAS ==========
    
    @st.cache_resource
    def cargar_modelos(_self):
        """Carga las arquitecturas con mapeo correcto"""
        try:
            modelos = {}
            
            # Mapeo correcto para metodologías híbridas
            archivos_modelos = {
                'ResNet50V2': 'ensemble_resnet_model.h5',        # Metodología Híbrida 1
                'CNN_Original': 'eye_disease_model.h5',          # Metodología Híbrida 2 (MobileNet)
                'EfficientNetB0': 'ensemble_efficientnet_model.h5' # Control
            }
            
            for nombre_arq, nombre_archivo in archivos_modelos.items():
                if os.path.exists(nombre_archivo):
                    modelos[nombre_arq] = tf.keras.models.load_model(nombre_archivo)
                    if nombre_arq in ['ResNet50V2', 'CNN_Original']:
                        st.success(get_text('hybrid_model_loaded', _self.lang, name=nombre_arq))
                    else:
                        st.success(get_text('control_model_loaded', _self.lang, name=nombre_arq))
                else:
                    st.warning(get_text('model_not_found', _self.lang, filename=nombre_archivo))
            
            # Cargar nombres de clases
            nombres_clases_conjunto = {}
            if os.path.exists('ensemble_class_indices.npy'):
                indices_clases = np.load('ensemble_class_indices.npy', allow_pickle=True).item()
                nombres_clases_conjunto = {v: k for k, v in indices_clases.items()}
            
            nombres_clases_individuales = {}
            if os.path.exists('class_indices.npy'):
                indices_clases = np.load('class_indices.npy', allow_pickle=True).item()
                nombres_clases_individuales = {v: k for k, v in indices_clases.items()}
            
            if not nombres_clases_conjunto:
                nombres_clases_conjunto = {i: f"Clase_{i}" for i in range(10)}
            if not nombres_clases_individuales:
                nombres_clases_individuales = {i: f"Clase_{i}" for i in range(10)}
            
            return modelos, nombres_clases_conjunto, nombres_clases_individuales
            
        except Exception as e:
            st.error(get_text('loading_error', _self.lang, error=str(e)))
            return {}, {}, {}
    
    def predecir_con_cronometraje(self, modelo, array_img, nombre_arq):
        """Predicción con información de metodología aplicada"""
        try:
            tiempo_inicio = time.time()
            predicciones = modelo.predict(array_img, verbose=0)
            tiempo_fin = time.time()
            
            tiempo_prediccion = tiempo_fin - tiempo_inicio
            indice_clase_predicha = np.argmax(predicciones[0])
            confianza = float(predicciones[0][indice_clase_predicha])
            
            # Nombres de clases
            if nombre_arq == 'CNN_Original':
                clase_predicha = self.nombres_clases_individuales[indice_clase_predicha]
            else:
                clase_predicha = self.nombres_clases[indice_clase_predicha]
            
            # Información de metodología
            if nombre_arq in ['ResNet50V2', 'CNN_Original']:
                metodologia_aplicada = get_text('hybrid_methodology_applied', self.lang)
            else:
                metodologia_aplicada = get_text('standard_methodology_applied', self.lang)
            
            return {
                'arquitectura': nombre_arq,
                'clase_predicha': clase_predicha,
                'indice_clase_predicha': indice_clase_predicha,
                'confianza': confianza,
                'todas_probabilidades': predicciones[0],
                'tiempo_prediccion': tiempo_prediccion,
                'tamaño_modelo': self.obtener_tamaño_modelo(modelo),
                'conteo_parametros': modelo.count_params(),
                'metodologia': metodologia_aplicada
            }
            
        except Exception as e:
            st.error(f"{get_text('prediction_error', self.lang)}: {str(e)}")
            return None
    
    def obtener_tamaño_modelo(self, modelo):
        """Calcula el tamaño del modelo en MB"""
        try:
            conteo_parametros = modelo.count_params()
            tamaño_mb = (conteo_parametros * 4) / (1024 * 1024)
            return tamaño_mb
        except:
            return 0
    
    # ========== FUNCIONES DE INTERFAZ ==========
    
    def mostrar_encabezado(self):
        """Header con información de metodologías híbridas"""
        st.title(get_text('hybrid_main_title', self.lang))
        st.subheader(get_text('hybrid_subtitle', self.lang))
        
        st.info(get_text('hybrid_info_box', self.lang))
        st.markdown("---")
    
    def mostrar_vitrina_arquitecturas(self):
        """Muestra las metodologías híbridas"""
        st.header(get_text('hybrid_architectures_title', self.lang))
        
        cols = st.columns(3)

        
        for i, (nombre_arq, info) in enumerate(self.informacion_arquitecturas.items()):
            with cols[i]:
                st.subheader(f"{info['icon']} {info['nombre_completo']}")
                
                if nombre_arq in ['ResNet50V2', 'CNN_Original']:
                    st.success(f"**{get_text('hybrid_methodology', self.lang)}**\n\n{info['descripcion']}")
                else:
                    st.info(f"**{get_text('control_group', self.lang)}**\n\n{info['descripcion']}")
                
                st.markdown(f"**{get_text('characteristics', self.lang)}:**")
                for key, value in info['caracteristicas'].items():
                    st.markdown(f"• **{key}:** {value}")
                
                st.markdown(f"**{get_text('advantages', self.lang)}:**")
                for ventaja in info['ventajas']:
                    st.markdown(f"• {ventaja}")
                
                st.markdown("---")
    
    def mostrar_resultados_prediccion(self, predicciones):
        """Muestra resultados con información de metodología"""
        st.header(get_text('hybrid_results_title', self.lang))
        
        cols = st.columns(3)
        
        for i, pred in enumerate(predicciones):
            nombre_arq = pred['arquitectura']
            info = self.informacion_arquitecturas[nombre_arq]
            
            with cols[i]:
                st.subheader(f"{info['icon']} {nombre_arq.replace('_', ' ')}")
                
                if nombre_arq in ['ResNet50V2', 'CNN_Original']:
                    st.success(f"**{get_text('hybrid_methodology', self.lang)}**")
                    st.caption(get_text('clahe_augmentation_applied', self.lang))
                else:
                    st.info(f"**{get_text('control_group', self.lang)}**")
                    st.caption(get_text('standard_processing_applied', self.lang))
                
                clase_predicha = pred['clase_predicha']
                info_clase = self.informacion_clases.get(clase_predicha, {})
                nombre_es = info_clase.get('nombre', clase_predicha)
                
                st.write(get_text('diagnosis', self.lang, diagnosis=nombre_es))
                
                st.metric(
                    label=get_text('confidence', self.lang),
                    value=f"{pred['confianza']:.1%}",
                    delta=None
                )
                
                st.markdown(get_text('technical_metrics', self.lang))
                st.markdown(get_text('time', self.lang, time=pred['tiempo_prediccion']))
                st.markdown(get_text('size', self.lang, size=pred['tamaño_modelo']))
                st.markdown(get_text('parameters', self.lang, params=pred['conteo_parametros']))
                st.markdown(f"**{get_text('methodology', self.lang)}:** {pred.get('metodologia', 'N/A')}")
                
                st.markdown("---")
    
    def ejecutar(self):
        """Ejecuta la aplicación con metodologías híbridas"""
        self.__init__()
        
        if 'analisis_completado' not in st.session_state:
            st.session_state.analisis_completado = False
        if 'predicciones' not in st.session_state:
            st.session_state.predicciones = None
        if 'imagen_analisis' not in st.session_state:
            st.session_state.imagen_analisis = None
        if 'marca_tiempo_analisis' not in st.session_state:
            st.session_state.marca_tiempo_analisis = None
        
        self.mostrar_encabezado()
        
        st.sidebar.markdown(f"## {get_text('hybrid_control_panel', self.lang)}")
        st.sidebar.markdown("---")
        
        # Cargar modelos
        if self.modelos is None:
            with st.spinner(get_text('loading_hybrid_models', self.lang)):
                self.modelos, self.nombres_clases, self.nombres_clases_individuales = self.cargar_modelos()
        
        if len(self.modelos) < 2:
            st.error(get_text('models_error', self.lang))
            st.stop()
        
        st.sidebar.success(get_text('hybrid_models_loaded', self.lang, count=len(self.modelos)))
        st.sidebar.info(get_text('hybrid_distribution', self.lang))
        
        # Mostrar informe técnico
        with st.sidebar.expander(get_text('technical_parameters', self.lang)):
            st.text(self.generar_informe_tecnico_parametros())
        
        if st.sidebar.button(get_text('new_analysis', self.lang)):
            st.session_state.analisis_completado = False
            st.session_state.predicciones = None
            st.session_state.imagen_analisis = None
            st.session_state.marca_tiempo_analisis = None
            st.rerun()
        
        self.mostrar_vitrina_arquitecturas()
        st.markdown("---")
        
        if st.session_state.analisis_completado and st.session_state.predicciones:
            st.success(get_text('hybrid_analysis_completed', self.lang))
            
            if st.session_state.imagen_analisis:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(st.session_state.imagen_analisis, 
                           caption=get_text('hybrid_analyzed_image', self.lang), 
                           use_container_width=True)
            
            predicciones = st.session_state.predicciones
            self.mostrar_resultados_prediccion(predicciones)
            
        else:
            st.markdown(f"## {get_text('hybrid_upload_title', self.lang)}")
            archivo_subido = st.file_uploader(
                get_text('hybrid_upload_help', self.lang),
                type=['png', 'jpg', 'jpeg'],
                help=get_text('hybrid_upload_description', self.lang)
            )
            
            if archivo_subido is not None:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    imagen = Image.open(archivo_subido)
                    st.image(imagen, caption=get_text('hybrid_image_caption', self.lang), use_container_width=True)
                
                if st.button(get_text('hybrid_start_analysis', self.lang), type="primary", use_container_width=True):
                    
                    marca_tiempo_analisis = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    predicciones = []
                    
                    with st.spinner(get_text('hybrid_processing', self.lang)):
                        barra_progreso = st.progress(0)
                        
                        for i, (nombre_arq, modelo) in enumerate(self.modelos.items()):
                            if nombre_arq in ['ResNet50V2', 'CNN_Original']:
                                st.info(get_text('applying_hybrid_to', self.lang, arch=nombre_arq))
                            else:
                                st.info(get_text('applying_control_to', self.lang, arch=nombre_arq))
                            
                            array_img = self.preprocesar_imagen_metodologia_hibrida(imagen, nombre_arq)
                            
                            if array_img is not None:
                                pred = self.predecir_con_cronometraje(modelo, array_img, nombre_arq)
                                if pred:
                                    predicciones.append(pred)
                            
                            barra_progreso.progress((i + 1) / len(self.modelos))
                    
                    if len(predicciones) >= 2:
                        st.success(get_text('hybrid_analysis_success', self.lang))
                        
                        # Calcular scores
                        for pred in predicciones:
                            max_conf = max(p['confianza'] for p in predicciones)
                            min_tiempo = min(p['tiempo_prediccion'] for p in predicciones)
                            min_tamaño = min(p['tamaño_modelo'] for p in predicciones)
                            
                            score_conf = pred['confianza'] / max_conf
                            score_velocidad = min_tiempo / pred['tiempo_prediccion']
                            score_memoria = min_tamaño / pred['tamaño_modelo']
                            
                            pred['score_general'] = 0.5 * score_conf + 0.25 * score_velocidad + 0.25 * score_memoria
                            pred['eficiencia'] = pred['confianza'] / pred['tiempo_prediccion']
                        
                        st.session_state.predicciones = predicciones
                        st.session_state.imagen_analisis = imagen
                        st.session_state.marca_tiempo_analisis = marca_tiempo_analisis
                        st.session_state.analisis_completado = True
                        
                        st.rerun()
                    
                    else:
                        st.error(get_text('hybrid_prediction_error', self.lang))




