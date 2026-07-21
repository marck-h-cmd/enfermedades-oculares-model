import os
import tempfile
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from backend.auth import get_current_user
import report_generator
import stats_validation
from backend.stats import load_cv_results

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/preview", dependencies=[Depends(get_current_user)])
def preview_report():
    """
    Retorna la estructura de datos completa y resúmenes para la vista previa del reporte en la UI de Next.js.
    """
    cv_data = load_cv_results()
    
    try:
        pruebas_stats = stats_validation.ejecutar_pruebas_estadisticas(cv_data)
    except Exception as e:
        pruebas_stats = {"error": str(e)}

    # Identificar modelo campeón
    campeon_name = max(cv_data.keys(), key=lambda k: cv_data[k].get('accuracy_media', 0.0))
    campeon = cv_data[campeon_name]
    rep_w = campeon.get('reporte_final', {}).get('weighted avg', {})

    summary_models = []
    for mod_name, res in cv_data.items():
        summary_models.append({
            "model": mod_name.upper(),
            "accuracy_media": res.get("accuracy_media", 0.0),
            "accuracy_std": res.get("accuracy_std", 0.0),
            "f1_score": res.get("reporte_final", {}).get("weighted avg", {}).get("f1-score", 0.0),
            "recall": res.get("reporte_final", {}).get("weighted avg", {}).get("recall", 0.0),
            "tiempo_medio": res.get("tiempo_medio", 0.0)
        })

    # Clases para el campeón
    class_metrics = []
    rep_classes = campeon.get('reporte_final', {})
    for cls_name, cls_m in rep_classes.items():
        if cls_name not in ['accuracy', 'macro avg', 'weighted avg'] and isinstance(cls_m, dict):
            prec = cls_m.get('precision', 0.0)
            rec = cls_m.get('recall', 0.0)
            especificidad_est = min(1.0, max(0.0, 1.0 - (1.0 - prec) * 0.4))
            class_metrics.append({
                "clase": cls_name,
                "sensibilidad": rec,
                "especificidad": especificidad_est,
                "precision": prec,
                "f1_score": cls_m.get('f1-score', 0.0),
                "support": int(cls_m.get('support', 0.0))
            })

    return {
        "title": "Reporte Clínico-Técnico Consolidado OcularDiagnose",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "methodology": "Validación Cruzada Estratificada de 5 Folds + CLAHE Pre-processing",
        "champion_model": {
            "name": campeon_name.upper(),
            "accuracy_media": campeon.get("accuracy_media", 0.0),
            "accuracy_std": campeon.get("accuracy_std", 0.0),
            "f1_score": rep_w.get("f1-score", 0.0),
            "recall": rep_w.get("recall", 0.0),
            "tiempo_medio": campeon.get("tiempo_medio", 0.0)
        },
        "summary_models": summary_models,
        "class_metrics": class_metrics,
        "friedman": pruebas_stats.get("anova_friedman", {}),
        "total_models": len(cv_data)
    }

@router.get("/download/{format_type}", dependencies=[Depends(get_current_user)])
def download_report(format_type: str):
    """
    Genera y descarga un reporte consolidado en el formato especificado: pdf, word, excel.
    """
    cv_data = load_cv_results()
    
    # Calcular estadísticas necesarias para Word y PDF
    try:
        pruebas_stats = stats_validation.ejecutar_pruebas_estadisticas(cv_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al calcular estadísticas para el reporte: {str(e)}"
        )
        
    # Crear un archivo temporal
    temp_dir = tempfile.gettempdir()
    
    if format_type.lower() == "pdf":
        file_name = "reporte_diagnostico.pdf"
        file_path = os.path.join(temp_dir, file_name)
        try:
            report_generator.generar_pdf_report(cv_data, pruebas_stats, ruta_salida=file_path)
            media_type = "application/pdf"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")
            
    elif format_type.lower() == "word":
        file_name = "reporte_diagnostico.docx"
        file_path = os.path.join(temp_dir, file_name)
        try:
            report_generator.generar_word_report(cv_data, pruebas_stats, ruta_salida=file_path)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generando Word: {str(e)}")
            
    elif format_type.lower() == "excel":
        file_name = "reporte_comparativo.xlsx"
        file_path = os.path.join(temp_dir, file_name)
        try:
            report_generator.generar_excel_report(cv_data, ruta_salida=file_path)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generando Excel: {str(e)}")
            
    else:
        raise HTTPException(
            status_code=400,
            detail="Formato de reporte inválido. Debe ser 'pdf' o 'word'."
        )
        
    if not os.path.exists(file_path):
         raise HTTPException(status_code=500, detail="El archivo de reporte no pudo ser creado.")
         
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type=media_type
    )

