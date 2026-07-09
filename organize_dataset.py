import os
import shutil
import pandas as pd
import ast

def organizar():
    csv_path = r"Dataset/DATASET_DESCARGADO/full_df.csv"
    src_dir = r"Dataset/DATASET_DESCARGADO/preprocessed_images"
    dest_base = r"Dataset"
    
    if not os.path.exists(csv_path):
        print(f"Error: No se encuentra el archivo CSV en '{csv_path}'")
        return
        
    if not os.path.exists(src_dir):
        print(f"Error: No se encuentra la carpeta de imágenes en '{src_dir}'")
        return
        
    print("Cargando CSV y organizando imágenes...")
    df = pd.read_csv(csv_path)
    
    # Mapeo de abreviaturas del CSV a las carpetas destino
    mapeo_clases = {
        'N': 'normal',
        'D': 'diabetes',
        'G': 'glaucoma',
        'C': 'cataract',
        'A': 'ageDegeneration',
        'H': 'hypertension',
        'M': 'myopia',
        'O': 'others'
    }
    
    # Asegurar que las carpetas destino existen
    for carpeta in mapeo_clases.values():
        os.makedirs(os.path.join(dest_base, carpeta), exist_ok=True)
        
    contador_copiados = {k: 0 for k in mapeo_clases.values()}
    total_filas = len(df)
    procesados = 0
    
    for idx, row in df.iterrows():
        filename = row['filename']
        # La columna 'labels' suele tener la forma "['N']" o "['D']"
        labels_str = row['labels']
        
        # Intentar extraer la etiqueta de la lista
        try:
            labels_list = ast.literal_eval(labels_str)
            label = labels_list[0] if len(labels_list) > 0 else 'O'
        except:
            label = 'O'
            
        clase_destino = mapeo_clases.get(label, 'others')
        
        src_file = os.path.join(src_dir, filename)
        dest_file = os.path.join(dest_base, clase_destino, filename)
        
        if os.path.exists(src_file):
            shutil.copy2(src_file, dest_file)
            contador_copiados[clase_destino] += 1
            procesados += 1
            
    print("\nOrganización completada.")
    print("Resumen de imágenes copiadas por clase:")
    print("=" * 40)
    for clase, count in contador_copiados.items():
        print(f"- {clase}: {count} imágenes")
    print("=" * 40)
    print(f"Total de imágenes copiadas: {procesados} / {total_filas}")

if __name__ == '__main__':
    organizar()
