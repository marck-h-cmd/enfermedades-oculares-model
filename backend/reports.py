import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from backend.auth import get_current_user
import report_generator
import stats_validation
from backend.stats import load_cv_results

router = APIRouter(prefix="/api/reports", tags=["Reports"])

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
            detail="Formato de reporte inválido. Debe ser 'pdf', 'word' o 'excel'."
        )
        
    if not os.path.exists(file_path):
         raise HTTPException(status_code=500, detail="El archivo de reporte no pudo ser creado.")
         
    return FileResponse(
        path=file_path,
        filename=file_name,
        media_type=media_type
    )
