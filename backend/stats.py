import json
import os
from fastapi import APIRouter, Depends, HTTPException
from backend.auth import get_current_user
import stats_validation

router = APIRouter(prefix="/api/models", tags=["Statistics"])

CV_RESULTS_PATH = "cv_metrics_results.json"

def load_cv_results():
    if not os.path.exists(CV_RESULTS_PATH):
        raise HTTPException(
            status_code=404,
            detail="No se encontraron resultados de validación cruzada. Por favor entrena los modelos primero en Streamlit."
        )
    try:
        with open(CV_RESULTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error cargando resultados de CV: {str(e)}"
        )

@router.get("", dependencies=[Depends(get_current_user)])
def get_models():
    """
    Retorna la lista de modelos disponibles y sus detalles técnicos comparativos.
    """
    cv_data = load_cv_results()
    
    detalles_modelos = {
        "mobilenet": {
            "nombre": "MobileNetV2 (Clásico)",
            "parametros": "~3.5M",
            "ventaja": "Eficiencia y velocidad, ideal para dispositivos móviles"
        },
        "resnet": {
            "nombre": "ResNet50V2 (Clásico)",
            "parametros": "~23.5M",
            "ventaja": "Alta capacidad de representación mediante conexiones residuales"
        },
        "efficientnet": {
            "nombre": "EfficientNetV2-B0 (Clásico)",
            "parametros": "~5.9M",
            "ventaja": "Compound scaling optimizado para alta precisión y bajo peso"
        },
        "fusion_net": {
            "nombre": "Fusión ResNet+MobileNet (Híbrido 1)",
            "parametros": "~27.0M",
            "ventaja": "Fusión profunda de características multiescala"
        },
        "cnn_rf": {
            "nombre": "MobileNet + Random Forest (Híbrido 2)",
            "parametros": "MobileNet + 100 Estimadores RF",
            "ventaja": "Clasificador no paramétrico de margen máximo en baja dimensionalidad"
        }
    }
    
    response = []
    for cod, info in detalles_modelos.items():
        if cod in cv_data:
            res = cv_data[cod]
            response.append({
                "id": cod,
                "nombre": info["nombre"],
                "accuracy_media": res["accuracy_media"],
                "accuracy_std": res["accuracy_std"],
                "tiempo_medio": res["tiempo_medio"],
                "f1_score": res["reporte_final"]["weighted avg"]["f1-score"],
                "precision": res["reporte_final"]["weighted avg"]["precision"],
                "recall": res["reporte_final"]["weighted avg"]["recall"],
                "parametros": info["parametros"],
                "ventaja": info["ventaja"]
            })
    return response

@router.get("/best", dependencies=[Depends(get_current_user)])
def get_best_model():
    """
    Obtiene el mejor modelo actual de acuerdo a su exactitud media en cross-validation.
    """
    cv_data = load_cv_results()
    if not cv_data:
        raise HTTPException(status_code=404, detail="No hay modelos entrenados.")
        
    best_id = max(cv_data.keys(), key=lambda k: cv_data[k]["accuracy_media"])
    res = cv_data[best_id]
    
    return {
        "id": best_id,
        "nombre": best_id.upper(),
        "accuracy_media": res["accuracy_media"],
        "f1_score": res["reporte_final"]["weighted avg"]["f1-score"]
    }

@router.get("/results", dependencies=[Depends(get_current_user)])
def get_cv_results():
    """
    Retorna los datos crudos de validación cruzada (curvas ROC, matrices de confusión por fold, etc.)
    """
    return load_cv_results()

@router.get("/statistics", dependencies=[Depends(get_current_user)])
def get_statistics():
    """
    Retorna la significancia estadística consolidada por pares de modelos
    (Holm-Bonferroni, Shapiro-Wilk y d de Cohen).
    """
    cv_data = load_cv_results()
    try:
        reporte_stats = stats_validation.ejecutar_pruebas_estadisticas(cv_data)
        return reporte_stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando pruebas estadísticas: {str(e)}"
        )
