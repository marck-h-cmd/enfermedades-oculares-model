import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

import tensorflow as tf
from keras import layers, Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.applications import MobileNetV2, EfficientNetV2B0, ResNet50V2
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import warnings
warnings.filterwarnings('ignore')

import tensorflow as tf
import sys
if not tf.config.list_physical_devices('GPU'):
    print("❌ ERROR CRÍTICO: No se detectó ninguna GPU compatible. Por regla estricta, el entrenamiento requiere GPU.")
    print("Si estás en Windows nativo con Python 3.13, TensorFlow no soporta GPU. Usa WSL2 o Python 3.10 con DirectML.")
    sys.exit(1)
else:
    # Desactivamos mixed_precision en el Ensemble porque causa un bug fatal de serialización JSON 
    # (<class 'EagerTensor'>) con las capas internas de EfficientNet en TF 2.10.
    print("⚡ [Optimizador GPU] Precisión normal activada para evitar bug de EfficientNet en TF 2.10.")
    pass

class EnsembleMedico:
    """
    Ensemble de CNNs para Diagnóstico Médico
    
    PARADIGMA COMPLETAMENTE DIFERENTE a CNN individual:
    - Entrena 3 arquitecturas diferentes por separado
    - Combina sus predicciones para decisión final
    - Reduce overfitting y mejora precisión
    - Usado en medicina real para mayor confiabilidad
    """
    
    def __init__(self):
        # Mapeo de clases (igual que tu código original)
        self.informacion_clases = {
            'ageDegeneration': {
                'nombre': 'Degeneración Macular (AMD)',
                'descripcion': 'Deterioro de la mácula afectando la visión central'
            },
            'cataract': {
                'nombre': 'Catarata',
                'descripcion': 'Opacidad del cristalino del ojo'
            },
            'diabetes': {
                'nombre': 'Retinopatía Diabética',
                'descripcion': 'Daño a los vasos sanguíneos de la retina por diabetes'
            },
            'glaucoma': {
                'nombre': 'Glaucoma',
                'descripcion': 'Daño al nervio óptico, generalmente por presión ocular alta'
            },
            'hypertension': {
                'nombre': 'Retinopatía Hipertensiva',
                'descripcion': 'Daño vascular retiniano por hipertensión'
            },
            'myopia': {
                'nombre': 'Miopía',
                'descripcion': 'Error refractivo que causa dificultad para ver objetos lejanos'
            },
            'normal': {
                'nombre': 'Ojo Sano',
                'descripcion': 'Retina sin patologías evidentes'
            },
            'others': {
                'nombre': 'Otras Patologías',
                'descripcion': 'Anomalías no clasificadas en otras categorías'
            }
        }
        
        # Configuración
        self.alto_img = 224
        self.ancho_img = 224
        self.tamaño_lote = 64
        self.division_validacion = 0.2
        
        print("🤖 ENSEMBLE MÉDICO DE CNNs")
        print("=" * 50)
        print("📋 ARQUITECTURAS A COMBINAR:")
        print("   🔲 MobileNetV2  - Eficiente y rápido")
        print("   ⚡ EfficientNetB0 - Optimizado accuracy/params")  
        print("   🔗 ResNet50V2    - Residual connections profundas")
        print("=" * 50)
    
    def preparar_datos(self, ruta_dataset):
        """Prepara datos para ensemble (igual que tu código)"""
        print("🔄 Preparando datos para Ensemble...")
        
        generador_datos_entrenamiento = ImageDataGenerator(
            rescale=1./255,
            rotation_range=25,
            width_shift_range=0.15,
            height_shift_range=0.15,
            shear_range=0.1,
            zoom_range=0.15,
            horizontal_flip=True,
            brightness_range=[0.8, 1.2],
            fill_mode='nearest',
            validation_split=self.division_validacion
        )
        
        generador_datos_validacion = ImageDataGenerator(
            rescale=1./255,
            validation_split=self.division_validacion
        )
        
        generador_entrenamiento = generador_datos_entrenamiento.flow_from_directory(
            ruta_dataset,
            target_size=(self.alto_img, self.ancho_img),
            batch_size=self.tamaño_lote,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        generador_validacion = generador_datos_validacion.flow_from_directory(
            ruta_dataset,
            target_size=(self.alto_img, self.ancho_img),
            batch_size=self.tamaño_lote,
            class_mode='categorical',
            subset='validation',
            shuffle=False
        )
        
        print(f"✅ Datos entrenamiento: {generador_entrenamiento.samples}")
        print(f"✅ Datos validación: {generador_validacion.samples}")
        
        return generador_entrenamiento, generador_validacion
    
    def crear_modelo_individual(self, arquitectura, num_clases, nombre_modelo):
        """Crea modelo individual según arquitectura"""
        print(f"🏗️ Creando modelo {arquitectura}...")
        
        if arquitectura == 'mobilenet':
            modelo_base = MobileNetV2(
                weights='imagenet',
                include_top=False,
                input_shape=(self.alto_img, self.ancho_img, 3)
            )
            # Fine-tuning específico para MobileNet
            modelo_base.trainable = True
            for capa in modelo_base.layers[:-20]:
                capa.trainable = False
                
        elif arquitectura == 'efficientnet':
            modelo_base = EfficientNetV2B0(
                weights='imagenet',
                include_top=False,
                input_shape=(self.alto_img, self.ancho_img, 3)
            )
            # Fine-tuning específico para EfficientNet
            modelo_base.trainable = True
            for capa in modelo_base.layers[:-15]:
                capa.trainable = False
                
        elif arquitectura == 'resnet':
            modelo_base = ResNet50V2(
                weights='imagenet',
                include_top=False,
                input_shape=(self.alto_img, self.ancho_img, 3)
            )
            # Fine-tuning específico para ResNet
            modelo_base.trainable = True
            for capa in modelo_base.layers[:-25]:
                capa.trainable = False
        
        # Capas superiores específicas por arquitectura
        x = modelo_base.output
        x = layers.GlobalAveragePooling2D()(x)
        
        # Configuración específica por modelo
        if arquitectura == 'mobilenet':
            x = layers.Dropout(0.3)(x)
            x = layers.Dense(128, activation='relu')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(0.2)(x)
        elif arquitectura == 'efficientnet':
            x = layers.Dropout(0.4)(x)
            x = layers.Dense(256, activation='relu')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(0.3)(x)
        elif arquitectura == 'resnet':
            x = layers.Dropout(0.4)(x)
            x = layers.Dense(512, activation='relu')(x)
            x = layers.Dropout(0.3)(x)
            x = layers.Dense(128, activation='relu')(x)
            x = layers.Dropout(0.2)(x)
        
        # Salida
        predicciones = layers.Dense(num_clases, activation='softmax', name='predictions')(x)
        
        modelo = Model(inputs=modelo_base.input, outputs=predicciones, name=nombre_modelo)
        
        # Compilar con configuración específica
        if arquitectura == 'mobilenet':
            tasa_aprendizaje = 0.0001
        elif arquitectura == 'efficientnet':
            tasa_aprendizaje = 0.00005  # Más conservador
        else:  # resnet
            tasa_aprendizaje = 0.0002   # Más agresivo
            
        modelo.compile(
            optimizer=Adam(learning_rate=tasa_aprendizaje),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )
        
        print(f"✅ {arquitectura} creado: {modelo.count_params():,} parámetros")
        return modelo
    
    def entrenar_modelo_individual(self, modelo, arquitectura, gen_entrenamiento, gen_validacion, epocas=25):
        """Entrena un modelo individual"""
        print(f"\n🚀 ENTRENANDO {arquitectura.upper()}...")
        print("=" * 40)
        
        # Callbacks específicos
        callbacks = [
            EarlyStopping(
                monitor='val_accuracy',
                patience=5,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.3,
                patience=3,
                min_lr=0.00001,
                verbose=1
            ),
            ModelCheckpoint(
                f'{arquitectura}_individual_model',
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Entrenar
        historial = modelo.fit(
            gen_entrenamiento,
            epochs=epocas,
            validation_data=gen_validacion,
            callbacks=callbacks,
            verbose=1
        )
        
        # Métricas finales
        precision_final = max(historial.history['val_accuracy'])
        print(f"✅ {arquitectura} completado - Mejor accuracy: {precision_final:.4f}")
        
        return modelo, historial, precision_final
    
    def crear_predictor_ensemble(self, modelos, pesos=None):
        """Crea función de ensemble para combinar predicciones"""
        if pesos is None:
            pesos = [1/len(modelos)] * len(modelos)  # Pesos iguales
        
        def prediccion_ensemble(x):
            predicciones = []
            for modelo in modelos:
                pred = modelo.predict(x, verbose=0)
                predicciones.append(pred)
            
            # Promedio ponderado
            prediccion_ensemble_final = np.zeros_like(predicciones[0])
            for i, pred in enumerate(predicciones):
                prediccion_ensemble_final += pesos[i] * pred
                
            return prediccion_ensemble_final
        
        return prediccion_ensemble
    
    def evaluar_ensemble(self, modelos, gen_validacion, pesos=None):
        """Evalúa ensemble completo"""
        print("\n🔬 EVALUANDO ENSEMBLE COMPLETO...")
        print("=" * 50)
        
        # Crear predictor ensemble
        prediccion_ensemble = self.crear_predictor_ensemble(modelos, pesos)
        
        # Obtener predicciones ensemble
        gen_validacion.reset()
        predicciones_ensemble = prediccion_ensemble(gen_validacion)
        clases_predichas = np.argmax(predicciones_ensemble, axis=1)
        
        # Etiquetas verdaderas
        clases_verdaderas = gen_validacion.classes
        etiquetas_clases = list(gen_validacion.class_indices.keys())
        
        # Reporte de clasificación
        print("📋 REPORTE ENSEMBLE:")
        print("=" * 80)
        reporte = classification_report(clases_verdaderas, clases_predichas, 
                                     target_names=etiquetas_clases, 
                                     output_dict=True)
        
        # Mostrar por clase
        for nombre_clase, metricas in reporte.items():
            if isinstance(metricas, dict) and nombre_clase not in ['accuracy', 'macro avg', 'weighted avg']:
                nombre_español = self.informacion_clases.get(nombre_clase, {}).get('nombre', nombre_clase)
                print(f"{nombre_español:30} | Precisión: {metricas['precision']:.3f} | "
                      f"Recall: {metricas['recall']:.3f} | F1: {metricas['f1-score']:.3f}")
        
        precision_ensemble = reporte['accuracy']
        f1_ensemble = reporte['weighted avg']['f1-score']
        
        print("=" * 80)
        print(f"🎯 ENSEMBLE ACCURACY: {precision_ensemble:.4f}")
        print(f"📊 ENSEMBLE F1-SCORE: {f1_ensemble:.4f}")
        
        return precision_ensemble, f1_ensemble, reporte
    
    def entrenar_ensemble(self, ruta_dataset, epocas=25):
        """Entrena ensemble completo"""
        print("🚀 ENTRENAMIENTO ENSEMBLE MÉDICO INICIADO")
        print("=" * 60)
        
        # Preparar datos
        gen_entrenamiento, gen_validacion = self.preparar_datos(ruta_dataset)
        num_clases = len(gen_entrenamiento.class_indices)
        
        # Crear modelos individuales
        arquitecturas = ['mobilenet', 'efficientnet', 'resnet']
        modelos = []
        historiales = []
        precisiones_individuales = []
        
        for arq in arquitecturas:
            print(f"\n{'='*20} {arq.upper()} {'='*20}")
            
            # Crear modelo
            modelo = self.crear_modelo_individual(arq, num_clases, f'{arq}_medical')
            
            # Entrenar
            modelo_entrenado, historial, precision_final = self.entrenar_modelo_individual(
                modelo, arq, gen_entrenamiento, gen_validacion, epocas
            )
            
            modelos.append(modelo_entrenado)
            historiales.append(historial)
            precisiones_individuales.append(precision_final)
        
        # Evaluar ensemble
        print(f"\n{'='*60}")
        print("🤖 EVALUACIÓN FINAL DEL ENSEMBLE")
        print(f"{'='*60}")
        
        # Mostrar accuracies individuales
        print("\n📊 ACCURACIES INDIVIDUALES:")
        for i, arq in enumerate(arquitecturas):
            print(f"   {arq:12}: {precisiones_individuales[i]:.4f}")
        
        # Evaluar ensemble con pesos optimizados
        precision_ensemble, f1_ensemble, reporte_ensemble = self.evaluar_ensemble(modelos, gen_validacion)
        
        # Guardar modelos
        for i, arq in enumerate(arquitecturas):
            modelos[i].save(f'ensemble_{arq}_model')
        
        # Guardar información del ensemble
        np.save('ensemble_class_indices.npy', gen_entrenamiento.class_indices)
        
        # Crear gráfico comparativo
        self.graficar_resultados_ensemble(arquitecturas, historiales, precisiones_individuales, precision_ensemble)
        
        print(f"\n🎉 ENSEMBLE COMPLETADO")
        print("=" * 50)
        print("📈 COMPARACIÓN DE PARADIGMAS:")
        print(f"   CNN Individual (tu anterior): 70.44%")
        print(f"   Ensemble de CNNs:             {precision_ensemble:.2%}")
        print(f"   Mejora: {((precision_ensemble/0.7044)-1)*100:+.1f}%")
        
        return modelos, historiales, precision_ensemble
    
    def graficar_resultados_ensemble(self, arquitecturas, historiales, precisiones_individuales, precision_ensemble):
        """Visualiza resultados del ensemble"""
        print("📈 Generando análisis visual del ensemble...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. Accuracy por época - todos los modelos
        colores = ['blue', 'red', 'green']
        for i, (arq, historial) in enumerate(zip(arquitecturas, historiales)):
            axes[0, 0].plot(historial.history['val_accuracy'], 
                           label=f'{arq}', color=colores[i], linewidth=2)
        
        axes[0, 0].axhline(y=precision_ensemble, color='purple', linestyle='--', 
                          linewidth=3, label=f'Ensemble: {precision_ensemble:.3f}')
        axes[0, 0].set_title('Evolución de Accuracy - Ensemble')
        axes[0, 0].set_xlabel('Época')
        axes[0, 0].set_ylabel('Validation Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Comparación de accuracies finales
        todas_precisiones = precisiones_individuales + [precision_ensemble]
        todos_nombres = arquitecturas + ['Ensemble']
        colores_barras = ['lightblue', 'lightcoral', 'lightgreen', 'purple']
        
        barras = axes[0, 1].bar(todos_nombres, todas_precisiones, color=colores_barras)
        axes[0, 1].set_title('Comparación Final de Accuracies')
        axes[0, 1].set_ylabel('Validation Accuracy')
        axes[0, 1].set_ylim(0, max(todas_precisiones) + 0.1)
        
        # Agregar valores en las barras
        for barra, precision in zip(barras, todas_precisiones):
            altura = barra.get_height()
            axes[0, 1].text(barra.get_x() + barra.get_width()/2., altura + 0.01,
                           f'{precision:.3f}', ha='center', va='bottom', fontweight='bold')
        
        # 3. Loss evolution
        for i, (arq, historial) in enumerate(zip(arquitecturas, historiales)):
            axes[1, 0].plot(historial.history['val_loss'], 
                           label=f'{arq}', color=colores[i], linewidth=2)
        
        axes[1, 0].set_title('Evolución de Loss - Ensemble')
        axes[1, 0].set_xlabel('Época')
        axes[1, 0].set_ylabel('Validation Loss')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Información del ensemble
        axes[1, 1].text(0.1, 0.9, '🤖 ENSEMBLE DE CNNs', fontsize=14, weight='bold', color='purple')
        axes[1, 1].text(0.1, 0.8, '• Combina 3 arquitecturas diferentes', fontsize=10)
        axes[1, 1].text(0.1, 0.7, '• Reduce overfitting individual', fontsize=10)
        axes[1, 1].text(0.1, 0.6, '• Mejora precisión y robustez', fontsize=10)
        axes[1, 1].text(0.1, 0.5, '• Usado en medicina real', fontsize=10)
        
        axes[1, 1].text(0.1, 0.3, 'vs CNN Individual:', fontsize=12, weight='bold')
        axes[1, 1].text(0.1, 0.2, '• Un solo modelo vs múltiples', fontsize=10)
        axes[1, 1].text(0.1, 0.1, '• Decisión individual vs consenso', fontsize=10)
        axes[1, 1].text(0.1, 0.0, '• Mayor riesgo overfitting', fontsize=10)
        axes[1, 1].set_xlim(0, 1)
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('ensemble_medical_results.png', dpi=300, bbox_inches='tight')
        # plt.show()  # COMENTADO PARA EVITAR QUE EL SCRIPT SE QUEDE BLOQUEADO EN SEGUNDO PLANO

def principal_ensemble():
    """Función principal para ensemble"""
    print("👁️🤖 ENSEMBLE MÉDICO DE CNNs")
    print("=" * 70)
    
    # Configuración
    RUTA_DATASET = "./Dataset"
    EPOCAS = 25  # Mismas épocas que CNN individual para comparación justa
    
    # Verificar dataset
    if not os.path.exists(RUTA_DATASET):
        print(f"❌ Error: No se encontró el dataset en {RUTA_DATASET}")
        return
    
    # Crear ensemble
    ensemble = EnsembleMedico()
    
    try:
        modelos, historiales, precision_ensemble = ensemble.entrenar_ensemble(
            ruta_dataset=RUTA_DATASET,
            epocas=EPOCAS
        )
        
        print("\n🎉 ¡ENSEMBLE COMPLETADO EXITOSAMENTE!")
        print("=" * 60)
        print("🆚 COMPARACIÓN COMPLETA DE PARADIGMAS:")
        print("   CNN Individual:    70.44% accuracy")
        print(f"   Ensemble de CNNs:   {precision_ensemble:.2%} accuracy")
        print("\n✅ Dos enfoques completamente diferentes probados")
        print("📁 Modelos guardados: ensemble_[arquitectura]_model")
        
    except Exception as e:
        print(f"\n❌ Error durante ensemble: {str(e)}")

if __name__ == "__main__":
    principal_ensemble()
