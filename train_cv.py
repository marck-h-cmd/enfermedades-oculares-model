import os
import time
import pickle
import json
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, Model, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2, ResNet50V2, EfficientNetB0
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import label_binarize
import warnings
warnings.filterwarnings('ignore')

class EntrenadorCrossValidation:
    """
    Clase para el entrenamiento secuencial de 3 modelos clásicos y 2 híbridos
    utilizando Validación Cruzada Estratificada por K-Folds (configurable).
    """
    def __init__(self, ruta_dataset, num_folds=5, alto_img=224, ancho_img=224):
        self.ruta_dataset = Path(ruta_dataset) if isinstance(ruta_dataset, str) else ruta_dataset
        self.num_folds = num_folds
        self.alto_img = alto_img
        self.ancho_img = ancho_img
        
        # Mapeo de clases en español
        self.informacion_clases = {
            'ageDegeneration': 'Degeneración Macular (AMD)',
            'cataract': 'Catarata',
            'diabetes': 'Retinopatía Diabética',
            'glaucoma': 'Glaucoma',
            'hypertension': 'Retinopatía Hipertensiva',
            'myopia': 'Miopía',
            'normal': 'Ojo Sano',
            'others': 'Otras Patologías'
        }
        
    def obtener_lista_archivos(self):
        """Escanea el dataset y retorna un DataFrame con rutas de archivos y etiquetas"""
        formatos_soportados = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        datos = []
        
        for clase_dir in self.ruta_dataset.iterdir():
            if clase_dir.is_dir() and not clase_dir.name.startswith('.'):
                for archivo in clase_dir.iterdir():
                    if archivo.is_file() and archivo.suffix.lower() in formatos_soportados:
                        datos.append({
                            'ruta_completa': str(archivo),
                            'clase': clase_dir.name
                        })
        
        df = pd.DataFrame(datos)
        if df.empty:
            raise FileNotFoundError(f"No se encontraron imágenes válidas en '{self.ruta_dataset}'")
            
        print(f"✅ Total de archivos cargados para validación cruzada: {len(df)}")
        return df

    def crear_modelo_clasico(self, arquitectura, num_clases):
        """Construye uno de los tres modelos CNN clásicos"""
        entrada = Input(shape=(self.alto_img, self.ancho_img, 3))
        
        if arquitectura == 'mobilenet':
            modelo_base = MobileNetV2(weights='imagenet', include_top=False, input_tensor=entrada)
            # Fine tuning
            modelo_base.trainable = True
            for capa in modelo_base.layers[:-20]:
                capa.trainable = False
        elif arquitectura == 'resnet':
            modelo_base = ResNet50V2(weights='imagenet', include_top=False, input_tensor=entrada)
            # Fine tuning
            modelo_base.trainable = True
            for capa in modelo_base.layers[:-25]:
                capa.trainable = False
        elif arquitectura == 'efficientnet':
            modelo_base = EfficientNetB0(weights='imagenet', include_top=False, input_tensor=entrada)
            # Fine tuning
            modelo_base.trainable = True
            for capa in modelo_base.layers[:-15]:
                capa.trainable = False
        else:
            raise ValueError(f"Arquitectura clásica desconocida: {arquitectura}")
            
        x = modelo_base.output
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(0.4)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.2)(x)
        salida = layers.Dense(num_clases, activation='softmax')(x)
        
        modelo = Model(inputs=entrada, outputs=salida, name=f"Clasico_{arquitectura}")
        modelo.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return modelo

    def crear_modelo_fusion_hibrido(self, num_clases):
        """
        Construye el Modelo Híbrido 1: Fusión de Características (Deep Hybrid)
        Concatenación de características extraídas por MobileNetV2 y ResNet50V2.
        """
        entrada = Input(shape=(self.alto_img, self.ancho_img, 3))
        
        # Rama MobileNetV2
        mobilenet = MobileNetV2(weights='imagenet', include_top=False, input_tensor=entrada)
        mobilenet.trainable = False  # Congelado para estabilidad de fusión
        x_m = mobilenet.output
        x_m = layers.GlobalAveragePooling2D()(x_m)
        
        # Rama ResNet50V2
        resnet = ResNet50V2(weights='imagenet', include_top=False, input_tensor=entrada)
        resnet.trainable = False  # Congelado
        x_r = resnet.output
        x_r = layers.GlobalAveragePooling2D()(x_r)
        
        # Fusión por concatenación
        fusion = layers.concatenate([x_m, x_r])
        
        # Clasificador final
        x = layers.Dense(256, activation='relu')(fusion)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.4)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.Dropout(0.2)(x)
        salida = layers.Dense(num_clases, activation='softmax')(x)
        
        modelo = Model(inputs=entrada, outputs=salida, name="Hibrido_Fusion")
        modelo.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        return modelo

    def entrenar_hibrido_cnn_rf(self, df_train, df_val, fold, indices_clases):
        """
        Entrena el Modelo Híbrido 2: CNN + Random Forest
        Extrae características con MobileNetV2 y entrena un clasificador Random Forest.
        """
        print(f"🌲 Entrenando Híbrido CNN-RF (Fold {fold})...")
        
        # Generadores sin aumentación para extracción estable de características
        gen_datos = ImageDataGenerator(rescale=1./255)
        
        gen_train = gen_datos.flow_from_dataframe(
            df_train, x_col='ruta_completa', y_col='clase',
            target_size=(self.alto_img, self.ancho_img),
            batch_size=32, class_mode='categorical',
            classes=list(indices_clases.keys()), shuffle=False
        )
        
        gen_val = gen_datos.flow_from_dataframe(
            df_val, x_col='ruta_completa', y_col='clase',
            target_size=(self.alto_img, self.ancho_img),
            batch_size=32, class_mode='categorical',
            classes=list(indices_clases.keys()), shuffle=False
        )
        
        # Extractor de características (MobileNetV2 base)
        extractor = MobileNetV2(weights='imagenet', include_top=False, input_shape=(self.alto_img, self.ancho_img, 3))
        modelo_extractor = Model(inputs=extractor.input, outputs=layers.GlobalAveragePooling2D()(extractor.output))
        
        print("   Extrayendo características de entrenamiento...")
        X_train = modelo_extractor.predict(gen_train, verbose=0)
        y_train = gen_train.classes
        
        print("   Extrayendo características de validación...")
        X_val = modelo_extractor.predict(gen_val, verbose=0)
        y_val = gen_val.classes
        
        # Entrenar clasificador Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        t_inicio = time.time()
        rf.fit(X_train, y_train)
        t_proceso = time.time() - t_inicio
        
        # Predecir
        pred_prob_val = rf.predict_proba(X_val)
        pred_val = np.argmax(pred_prob_val, axis=1)
        
        acc_val = np.mean(pred_val == y_val)
        print(f"   Accuracy RF (Fold {fold}): {acc_val:.4f} (Tiempo: {t_proceso:.2f}s)")
        
        return rf, acc_val, y_val, pred_val, pred_prob_val, t_proceso, modelo_extractor

    def entrenar_cv(self, modelos_a_entrenar=None, epocas=5, batch_size=32, callback_progreso=None):
        """
        Ejecuta el ciclo de Validación Cruzada por K-Folds para los modelos indicados.
        """
        if modelos_a_entrenar is None:
            modelos_a_entrenar = ['mobilenet', 'resnet', 'efficientnet', 'fusion_net', 'cnn_rf']
            
        df_datos = self.obtener_lista_archivos()
        
        # Definir índices de clases uniformes
        clases_unicas = sorted(df_datos['clase'].unique())
        indices_clases = {clase: i for i, clase in enumerate(clases_unicas)}
        np.save('class_indices.npy', indices_clases)
        num_clases = len(clases_unicas)
        
        # Guardar mapeo de clases para el dashboard
        with open('class_indices.json', 'w', encoding='utf-8') as f:
            json.dump(indices_clases, f, indent=2, ensure_ascii=False)
            
        skf = StratifiedKFold(n_splits=self.num_folds, shuffle=True, random_state=42)
        
        # Diccionario para acumular resultados globales
        resultados_globales = {model_name: {
            'accuracies': [],
            'tiempos_entrenamiento': [],
            'confusion_matrices': [],
            'true_labels': [],
            'pred_labels': [],
            'pred_probabilities': []
        } for model_name in modelos_a_entrenar}
        
        total_pasos = len(modelos_a_entrenar) * self.num_folds
        paso_actual = 0
        
        mejor_acc_global = 0.0
        
        # Data Generator con data augmentation para entrenamiento
        generador_entrenamiento = ImageDataGenerator(
            rescale=1./255,
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            horizontal_flip=True
        )
        generador_validacion = ImageDataGenerator(rescale=1./255)
        
        for fold, (idx_train, idx_val) in enumerate(skf.split(df_datos, df_datos['clase'])):
            df_train = df_datos.iloc[idx_train]
            df_val = df_datos.iloc[idx_val]
            
            print(f"\n================ FOLD {fold + 1}/{self.num_folds} ================")
            
            # Flujos de datos para este fold
            gen_train = generador_entrenamiento.flow_from_dataframe(
                df_train, x_col='ruta_completa', y_col='clase',
                target_size=(self.alto_img, self.ancho_img),
                batch_size=batch_size, class_mode='categorical',
                classes=clases_unicas, shuffle=True
            )
            
            gen_val = generador_validacion.flow_from_dataframe(
                df_val, x_col='ruta_completa', y_col='clase',
                target_size=(self.alto_img, self.ancho_img),
                batch_size=batch_size, class_mode='categorical',
                classes=clases_unicas, shuffle=False
            )
            
            y_val_verdadero = gen_val.classes
            
            for modelo_name in modelos_a_entrenar:
                paso_actual += 1
                msg = f"Entrenando {modelo_name.upper()} - Fold {fold+1}/{self.num_folds}"
                print(f"\n🤖 {msg}...")
                
                if callback_progreso:
                    callback_progreso(paso_actual, total_pasos, msg)
                
                t_inicio = time.time()
                
                if modelo_name == 'cnn_rf':
                    # Modelo híbrido CNN + Random Forest
                    rf_model, acc_val, y_v, y_p, y_prob, t_proceso, extractor = self.entrenar_hibrido_cnn_rf(
                        df_train, df_val, fold + 1, indices_clases
                    )
                    
                    resultados_globales[modelo_name]['accuracies'].append(acc_val)
                    resultados_globales[modelo_name]['tiempos_entrenamiento'].append(t_proceso)
                    resultados_globales[modelo_name]['true_labels'].extend(y_v.tolist())
                    resultados_globales[modelo_name]['pred_labels'].extend(y_p.tolist())
                    resultados_globales[modelo_name]['pred_probabilities'].extend(y_prob.tolist())
                    
                    # Si es el mejor híbrido RF, guardamos el extractor en .h5 y el RF en .pkl
                    if acc_val > mejor_acc_global:
                        mejor_acc_global = acc_val
                        extractor.save('best_ocular_model.h5')
                        with open('best_rf_classifier.pkl', 'wb') as f:
                            pickle.dump(rf_model, f)
                        # Guardar metadato de tipo de modelo
                        with open('best_model_meta.json', 'w') as f:
                            json.dump({'tipo': 'cnn_rf'}, f)
                            
                else:
                    # Modelos Keras (Clásicos y Fusión Híbrida)
                    if modelo_name == 'mobilenet':
                        modelo = self.crear_modelo_classic_or_fusion = self.crear_modelo_clasico('mobilenet', num_clases)
                    elif modelo_name == 'resnet':
                        modelo = self.crear_modelo_clasico('resnet', num_clases)
                    elif modelo_name == 'efficientnet':
                        modelo = self.crear_modelo_clasico('efficientnet', num_clases)
                    elif modelo_name == 'fusion_net':
                        modelo = self.crear_modelo_fusion_hibrido(num_clases)
                        
                    # Callbacks
                    callbacks = [
                        EarlyStopping(monitor='val_accuracy', patience=3, restore_best_weights=True, verbose=0),
                        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, min_lr=1e-6, verbose=0)
                    ]
                    
                    # Entrenar
                    historial = modelo.fit(
                        gen_train,
                        epochs=epocas,
                        validation_data=gen_val,
                        callbacks=callbacks,
                        verbose=0
                    )
                    
                    t_proceso = time.time() - t_inicio
                    
                    # Evaluar
                    gen_val.reset()
                    pred_prob = modelo.predict(gen_val, verbose=0)
                    pred_labels = np.argmax(pred_prob, axis=1)
                    
                    acc_val = np.mean(pred_labels == y_val_verdadero)
                    print(f"   Accuracy (Fold {fold+1}): {acc_val:.4f} (Tiempo: {t_proceso:.1f}s)")
                    
                    resultados_globales[modelo_name]['accuracies'].append(acc_val)
                    resultados_globales[modelo_name]['tiempos_entrenamiento'].append(t_proceso)
                    resultados_globales[modelo_name]['true_labels'].extend(y_val_verdadero.tolist())
                    resultados_globales[modelo_name]['pred_labels'].extend(pred_labels.tolist())
                    resultados_globales[modelo_name]['pred_probabilities'].extend(pred_prob.tolist())
                    
                    # Guardar el mejor modelo de tipo red neuronal
                    if acc_val > mejor_acc_global:
                        mejor_acc_global = acc_val
                        modelo.save('best_ocular_model.h5')
                        with open('best_model_meta.json', 'w') as f:
                            json.dump({'tipo': 'neural_network', 'nombre': modelo_name}, f)
        
        # Guardar las métricas de CV consolidadas en JSON para uso en reportes y dashboard
        self.guardar_metricas_cv(resultados_globales, clases_unicas)
        
        print("\n================ ENTRENAMIENTO CV COMPLETADO ================")
        for name in modelos_a_entrenar:
            acc_media = np.mean(resultados_globales[name]['accuracies'])
            print(f"🏆 {name.upper()} -> Accuracy Medio CV: {acc_media:.4%}")
            
        return resultados_globales

    def guardar_metricas_cv(self, resultados, clases):
        """Consolida las métricas y calcula las curvas ROC y matrices de confusión"""
        datos_consolidados = {}
        
        for modelo_name, res in resultados.items():
            y_true = np.array(res['true_labels'])
            y_pred = np.array(res['pred_labels'])
            y_prob = np.array(res['pred_probabilities'])
            
            # Validar que existan predicciones para evitar errores
            if len(y_true) == 0:
                continue
                
            # Reporte de clasificación
            reporte = classification_report(y_true, y_pred, target_names=clases, output_dict=True)
            cm = confusion_matrix(y_true, y_pred).tolist()
            
            # Curvas ROC para multi-clase (One-vs-Rest)
            y_true_bin = label_binarize(y_true, classes=range(len(clases)))
            curvas_roc_clases = {}
            
            for idx_clase, clase_nombre in enumerate(clases):
                try:
                    fpr, tpr, _ = roc_curve(y_true_bin[:, idx_clase], y_prob[:, idx_clase])
                    auc_score = auc(fpr, tpr)
                    # Muestrear curvas ROC para no saturar el JSON
                    indices_muestreo = np.linspace(0, len(fpr) - 1, min(50, len(fpr))).astype(int)
                    curvas_roc_clases[clase_nombre] = {
                        'fpr': fpr[indices_muestreo].tolist(),
                        'tpr': tpr[indices_muestreo].tolist(),
                        'auc': float(auc_score)
                    }
                except:
                    curvas_roc_clases[clase_nombre] = {'fpr': [], 'tpr': [], 'auc': 0.0}
                    
            # Guardar información
            datos_consolidados[modelo_name] = {
                'accuracies_folds': [float(a) for a in res['accuracies']],
                'accuracy_media': float(np.mean(res['accuracies'])),
                'accuracy_std': float(np.std(res['accuracies'])),
                'tiempos_folds': [float(t) for t in res['tiempos_entrenamiento']],
                'tiempo_medio': float(np.mean(res['tiempos_folds'])),
                'reporte_final': reporte,
                'matriz_confusion': cm,
                'curvas_roc': curvas_roc_clases
            }
            
        with open('cv_metrics_results.json', 'w', encoding='utf-8') as f:
            json.dump(datos_consolidados, f, indent=2, ensure_ascii=False)
            
        print("💾 Resultados de validación cruzada guardados en 'cv_metrics_results.json'")

if __name__ == "__main__":
    # Prueba rápida
    if os.path.exists("./Dataset"):
        entrenador = EntrenadorCrossValidation("./Dataset", num_folds=2)
        entrenador.entrenar_cv(modelos_a_entrenar=['mobilenet', 'cnn_rf'], epocas=1)
