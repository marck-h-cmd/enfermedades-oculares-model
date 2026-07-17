import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import shutil
from pathlib import Path

def es_imagen_valida(ruta_img):
    """
    Verifica si una imagen se puede abrir y decodificar correctamente con PIL y OpenCV.
    """
    try:
        # Intento con PIL
        with Image.open(ruta_img) as img:
            img.verify()
        
        # Intento de carga y decodificación con OpenCV
        # cv2.imread puede retornar None si la imagen está corrupta o el formato no es soportado
        img_cv = cv2.imread(str(ruta_img))
        if img_cv is None:
            return False
            
        return True
    except:
        return False

def realizar_eda(ruta_dataset, mover_corruptas=True):
    """
    Escanea la carpeta del dataset, identifica imágenes corruptas, realiza limpieza
    y genera estadísticas descriptivas sobre el dataset ocular.
    
    Retorna un diccionario con DataFrames y estadísticas listas para visualización.
    """
    ruta_dataset = Path(ruta_dataset)
    if not ruta_dataset.exists() or not ruta_dataset.is_dir():
        raise FileNotFoundError(f"La ruta del dataset '{ruta_dataset}' no existe o no es un directorio.")

    formatos_soportados = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    clases = [d.name for d in ruta_dataset.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    datos_imagenes = []
    imagenes_corruptas = []
    
    # Crear carpeta para imágenes corruptas si se activa el movimiento
    ruta_corruptas = ruta_dataset.parent / "corruptas_detectadas"
    if mover_corruptas:
        ruta_corruptas.mkdir(exist_ok=True)
        
    for clase in clases:
        ruta_clase = ruta_dataset / clase
        archivos = [f for f in ruta_clase.iterdir() if f.is_file() and f.suffix.lower() in formatos_soportados]
        
        for archivo in archivos:
            if es_imagen_valida(archivo):
                # Obtener propiedades de la imagen
                try:
                    # Leemos con OpenCV
                    img = cv2.imread(str(archivo))
                    alto, ancho, canales = img.shape
                    
                    # Calcular estadísticas de color (media y desviación estándar de RGB)
                    # OpenCV lee en BGR, convertimos para el reporte
                    media_bgr = cv2.mean(img)[:3]
                    media_rgb = (media_bgr[2], media_bgr[1], media_bgr[0])
                    
                    std_bgr, _ = cv2.meanStdDev(img)
                    std_rgb = (float(std_bgr[2][0]), float(std_bgr[1][0]), float(std_bgr[0][0]))
                    
                    tamano_kb = archivo.stat().st_size / 1024.0
                    
                    datos_imagenes.append({
                        'Nombre': archivo.name,
                        'Ruta': str(archivo),
                        'Clase': clase,
                        'Ancho': ancho,
                        'Alto': alto,
                        'Canales': canales,
                        'RelacionAspecto': ancho / alto,
                        'TamanoKB': tamano_kb,
                        'Media_R': media_rgb[0],
                        'Media_G': media_rgb[1],
                        'Media_B': media_rgb[2],
                        'Std_R': std_rgb[0],
                        'Std_G': std_rgb[1],
                        'Std_B': std_rgb[2]
                    })
                except Exception as e:
                    # Si falla al leer propiedades, la marcamos como corrupta
                    imagenes_corruptas.append((str(archivo), clase, str(e)))
                    if mover_corruptas:
                        try:
                            shutil.move(str(archivo), str(ruta_corruptas / archivo.name))
                        except:
                            pass
            else:
                imagenes_corruptas.append((str(archivo), clase, "Fallo en validación de formato/lectura"))
                if mover_corruptas:
                    try:
                        shutil.move(str(archivo), str(ruta_corruptas / archivo.name))
                    except:
                        pass
                        
    # Construir DataFrames
    df_clean = pd.DataFrame(datos_imagenes)
    df_corrupt = pd.DataFrame(imagenes_corruptas, columns=['Ruta', 'Clase', 'Error'])
    
    # Resumen de estadísticas
    resumen = {}
    if not df_clean.empty:
        resumen = {
            'total_imagenes_validas': len(df_clean),
            'total_imagenes_corruptas': len(df_corrupt),
            'clases_detectadas': clases,
            'distribucion_clases': df_clean['Clase'].value_counts().to_dict(),
            'resolucion_promedio': f"{df_clean['Ancho'].mean():.0f}x{df_clean['Alto'].mean():.0f}",
            'tamano_promedio_kb': df_clean['TamanoKB'].mean(),
            'relacion_aspecto_promedio': df_clean['RelacionAspecto'].mean(),
            'color_medio_rgb': [df_clean['Media_R'].mean(), df_clean['Media_G'].mean(), df_clean['Media_B'].mean()]
        }
    else:
        resumen = {
            'total_imagenes_validas': 0,
            'total_imagenes_corruptas': len(df_corrupt),
            'clases_detectadas': clases,
            'distribucion_clases': {},
            'resolucion_promedio': "N/A",
            'tamano_promedio_kb': 0,
            'relacion_aspecto_promedio': 1.0,
            'color_medio_rgb': [0.0, 0.0, 0.0]
        }
        
    return df_clean, df_corrupt, resumen

if __name__ == "__main__":
    # Prueba rápida de ejecución
    dataset_test = "./Dataset"
    if os.path.exists(dataset_test):
        print("Iniciando análisis exploratorio en local...")
        df_clean, df_corrupt, resumen = realizar_eda(dataset_test)
        print("Resumen de EDA:")
        for k, v in resumen.items():
            print(f" - {k}: {v}")
    else:
        print(f"Dataset de prueba no encontrado en: {dataset_test}")
