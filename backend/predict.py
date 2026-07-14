import io
import os
import json
import pickle
import base64
import numpy as np
import cv2
import tensorflow as tf
from PIL import Image
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from backend.auth import get_current_user
import gradcam

router = APIRouter(prefix="/api", tags=["Prediction"])

# Mapeo de clases e información clínica
INFORMACION_CLASES = {
    'ageDegeneration': {
        'nombre': 'Degeneración Macular (AMD)',
        'descripcion': 'Deterioro de la mácula que afecta la visión central y los detalles finos.',
        'gravedad': 'Alta',
        'tratamiento': 'Inyecciones intravítreas anti-VEGF, suplementos vitamínicos, fotocoagulación con láser.',
        'pronostico': 'Progresivo, pero manejable con tratamientos tempranos para retrasar la pérdida de visión.'
    },
    'cataract': {
        'nombre': 'Catarata',
        'descripcion': 'Opacidad del cristalino del ojo que causa pérdida de visión progresiva y visión borrosa.',
        'gravedad': 'Moderada',
        'tratamiento': 'Cirugía ambulatoria de reemplazo del cristalino por una lente intraocular (LIO).',
        'pronostico': 'Excelente, con recuperación casi total de la agudeza visual tras la cirugía.'
    },
    'diabetes': {
        'nombre': 'Retinopatía Diabética',
        'descripcion': 'Daño a los vasos sanguíneos de la retina causado por niveles crónicos de glucosa alta.',
        'gravedad': 'Alta',
        'tratamiento': 'Control estricto de glucosa y presión arterial, inyecciones anti-VEGF, fotocoagulación láser, vitrectomía.',
        'pronostico': 'Manejo temprano altamente efectivo; la falta de tratamiento puede llevar a ceguera irreversible.'
    },
    'glaucoma': {
        'nombre': 'Glaucoma',
        'descripcion': 'Daño progresivo al nervio óptico, comúnmente asociado con presión intraocular (PIO) elevada.',
        'gravedad': 'Alta',
        'tratamiento': 'Gotas oftálmicas hipotensoras, trabeculoplastia láser, microcirugía (trabeculectomía).',
        'pronostico': 'La pérdida visual es irreversible; el tratamiento detiene la progresión de la enfermedad.'
    },
    'hypertension': {
        'nombre': 'Retinopatía Hipertensiva',
        'descripcion': 'Alteraciones vasculares de la retina secundarias a presión arterial sistémica elevada.',
        'gravedad': 'Moderada a Alta',
        'tratamiento': 'Control farmacológico riguroso de la hipertensión arterial sistémica.',
        'pronostico': 'Buen pronóstico visual si se controla la presión arterial; las lesiones agudas suelen ser reversibles.'
    },
    'myopia': {
        'nombre': 'Miopía Patológica / Degenerativa',
        'descripcion': 'Elongación excesiva del globo ocular que causa adelgazamiento de la retina y coroides.',
        'gravedad': 'Moderada',
        'tratamiento': 'Uso de lentes correctoras, lentes de contacto, cirugía refractiva, fotocoagulación láser en caso de desgarros.',
        'pronostico': 'Riesgo elevado de desprendimiento de retina y neovascularización coroidea en casos graves.'
    },
    'normal': {
        'nombre': 'Ojo Sano / Normal',
        'descripcion': 'Fondo de ojo con estructuras retinales, nervio óptico y vasculatura en estado fisiológico saludable.',
        'gravedad': 'Ninguna',
        'tratamiento': 'No requiere tratamiento. Se recomiendan chequeos oftalmológicos preventivos anuales.',
        'pronostico': 'Excelente salud ocular.'
    },
    'others': {
        'nombre': 'Otras Patologías',
        'descripcion': 'Hallazgos retinales anormales (ej. oclusión de venas, coriorretinitis, drusas, etc.) fuera de las categorías principales.',
        'gravedad': 'Variable',
        'tratamiento': 'Depende del diagnóstico específico realizado por el oftalmólogo.',
        'pronostico': 'Reservado, requiere evaluación clínica y de gabinete complementaria.'
    }
}

CLASES_LIST = [
    'ageDegeneration', 'cataract', 'diabetes', 'glaucoma', 
    'hypertension', 'myopia', 'normal', 'others'
]

def aplicar_clahe(img_np):
    """Aplica ecualización adaptativa CLAHE al canal de luminancia (L) de la imagen."""
    # Convertir a formato LAB
    lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    # Aplicar CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    # Fusionar canales y volver a RGB
    limg = cv2.merge((cl, a, b))
    img_clahe = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    return img_clahe

def encode_img_to_base64(img_np):
    """Convierte un array de imagen NumPy a una cadena Base64."""
    pil_img = Image.fromarray(img_np)
    buff = io.BytesIO()
    pil_img.save(buff, format="JPEG")
    img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

@router.post("/predict")
async def predict(request: Request, file: UploadFile = File(...), user: str = Depends(get_current_user)):
    """
    Recibe una imagen, aplica CLAHE, predice en paralelo usando los modelos
    cargados (MobileNetV2, ResNet50V2, EfficientNetV2B0, Champion CV y Ensemble),
    genera el mapa Grad-CAM y retorna el diagnóstico completo con las imágenes en base64.
    """
    # 1. Leer imagen
    contents = await file.read()
    try:
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Formato de imagen inválido.")
        
    img_orig_np = np.array(pil_img)
    
    # Redimensionar para la entrada de las redes
    img_resized = cv2.resize(img_orig_np, (224, 224))
    
    # 2. Aplicar CLAHE para visualización y diagnóstico
    img_clahe_np = aplicar_clahe(img_resized)
    
    # Normalizar imágenes para entrada a los modelos
    img_norm = np.expand_dims(img_resized.astype("float32") / 255.0, axis=0)
    img_clahe_norm = np.expand_dims(img_clahe_np.astype("float32") / 255.0, axis=0)
    
    # 3. Obtener los modelos pre-cargados del estado de la aplicación
    models = request.app.state.models
    
    # Diccionario para almacenar predicciones de probabilidad
    predicciones = {}
    
    # A. Predicción de Modelos Base
    for model_name in ["mobilenet", "resnet", "efficientnet"]:
        model = models.get(model_name)
        if model:
            try:
                # Los modelos base suelen entrenarse con imágenes preprocesadas
                prob = model.predict(img_clahe_norm, verbose=0)[0]
                predicciones[model_name] = prob.tolist()
            except Exception as e:
                print(f"Error prediciendo en {model_name}: {str(e)}")
                predicciones[model_name] = [0.125] * 8
        else:
            # Fallback en caso de que no esté entrenado aún
            predicciones[model_name] = [0.125] * 8
            
    # B. Predicción del Ensemble (promedio de los tres modelos base)
    probs_base = [predicciones[m] for m in ["mobilenet", "resnet", "efficientnet"]]
    ensemble_prob = np.mean(probs_base, axis=0)
    predicciones["ensemble"] = ensemble_prob.tolist()
    
    # C. Predicción del Campeón de CV
    champion_model = models.get("champion")
    rf_classifier = models.get("rf_classifier")
    meta_champion = models.get("champion_meta")
    
    if champion_model:
        try:
            if meta_champion and meta_champion.get("tipo") == "cnn_rf" and rf_classifier:
                # El extractor de características corre sobre la imagen norm
                features = champion_model.predict(img_norm, verbose=0)
                prob_rf = rf_classifier.predict_proba(features)[0]
                predicciones["champion"] = prob_rf.tolist()
            else:
                prob = champion_model.predict(img_norm, verbose=0)[0]
                predicciones["champion"] = prob.tolist()
        except Exception as e:
            print(f"Error prediciendo en Champion: {str(e)}")
            predicciones["champion"] = predicciones["ensemble"] # Fallback al ensemble
    else:
        predicciones["champion"] = predicciones["ensemble"]
        
    # 4. Generar Grad-CAM sobre el mejor modelo (o un modelo base si no hay mejor)
    heatmap_model = champion_model if (champion_model and meta_champion and meta_champion.get("tipo") != "cnn_rf") else models.get("mobilenet")
    img_gradcam_b64 = None
    
    if heatmap_model:
        try:
            # Encontrar el índice de la clase ganadora según el modelo principal
            clase_pred_idx = np.argmax(predicciones["champion"])
            # Generar heatmap Grad-CAM
            heatmap = gradcam.get_gradcam_heatmap(heatmap_model, img_clahe_norm, class_idx=clase_pred_idx)
            # Redimensionar al tamaño original de la imagen cargada
            img_original_resized = cv2.resize(img_orig_np, (400, 400))
            img_clahe_resized = cv2.resize(aplicar_clahe(img_original_resized), (400, 400))
            
            # Superponer Grad-CAM sobre la imagen original
            img_gradcam = gradcam.overlay_gradcam(img_clahe_resized, heatmap, alpha=0.45)
            img_gradcam_b64 = encode_img_to_base64(img_gradcam)
        except Exception as e:
            print(f"Error generando Grad-CAM en predict: {str(e)}")
            
    # Formatear respuesta de diagnóstico
    final_probabilities = predicciones["champion"]
    predicted_class_idx = int(np.argmax(final_probabilities))
    predicted_class_name = CLASES_LIST[predicted_class_idx]
    info_clinica = INFORMACION_CLASES.get(predicted_class_name, INFORMACION_CLASES['others'])
    
    # Generar respuesta estructurada por modelo
    detalles_modelos = {}
    for model_name, probs in predicciones.items():
        idx_max = int(np.argmax(probs))
        name_max = CLASES_LIST[idx_max]
        detalles_modelos[model_name] = {
            "clase_id": name_max,
            "clase_nombre": INFORMACION_CLASES.get(name_max, {}).get("nombre", name_max),
            "confianza": float(probs[idx_max]),
            "probabilidades_completas": {CLASES_LIST[i]: float(probs[i]) for i in range(8)}
        }
        
    # Codificar imágenes en base64 para el slider en frontend
    img_orig_400 = cv2.resize(img_orig_np, (400, 400))
    img_clahe_400 = aplicar_clahe(img_orig_400)
    
    # Calcular histogramas de luminancia (L)
    lab_orig = cv2.cvtColor(img_orig_400, cv2.COLOR_RGB2LAB)
    l_orig = cv2.split(lab_orig)[0]
    hist_orig = cv2.calcHist([l_orig], [0], None, [16], [0, 256]).flatten().tolist()
    
    lab_clahe = cv2.cvtColor(img_clahe_400, cv2.COLOR_RGB2LAB)
    l_clahe = cv2.split(lab_clahe)[0]
    hist_clahe = cv2.calcHist([l_clahe], [0], None, [16], [0, 256]).flatten().tolist()
    
    return {
        "diagnostico_principal": {
            "clase_id": predicted_class_name,
            "clase_nombre": info_clinica["nombre"],
            "confianza": float(final_probabilities[predicted_class_idx]),
            "descripcion": info_clinica["descripcion"],
            "gravedad": info_clinica["gravedad"],
            "tratamiento": info_clinica["tratamiento"],
            "pronostico": info_clinica["pronostico"]
        },
        "modelos": detalles_modelos,
        "imagenes": {
            "original": encode_img_to_base64(img_orig_400),
            "clahe": encode_img_to_base64(img_clahe_400),
            "gradcam": img_gradcam_b64
        },
        "histogramas": {
            "bins": [f"{i*16}-{(i+1)*16-1}" for i in range(16)],
            "original": hist_orig,
            "clahe": hist_clahe
        }
    }
