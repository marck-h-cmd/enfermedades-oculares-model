import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

# Importaciones modernas de TensorFlow
import tensorflow as tf
from keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.applications import MobileNetV2
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
    # Habilitar mixed precision para exprimir la RTX 3050 (hace el entrenamiento más rápido y usa menos VRAM)
    try:
        from tensorflow.keras import mixed_precision
        mixed_precision.set_global_policy('mixed_float16')
        print("⚡ [Optimizador GPU] Política de precisión mixta (float16) activada. ¡Máxima velocidad!")
    except Exception as e:
        print(f"No se pudo activar mixed precision: {e}")

class EntrenadorEnfermedadesOculares:
    def __init__(self):
        # Mapeo de clases en español
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
        
        # Configuración del modelo
        self.alto_img = 224
        self.ancho_img = 224
        self.tamaño_lote = 128
        self.division_validacion = 0.15
        
    def analizar_dataset(self, ruta_dataset):
        """Analiza el dataset antes del entrenamiento"""
        print("📊 Analizando dataset...")
        print("=" * 50)
        
        conteos_clases = {}
        total_imagenes = 0
        
        for nombre_clase in os.listdir(ruta_dataset):
            ruta_clase = os.path.join(ruta_dataset, nombre_clase)
            if os.path.isdir(ruta_clase):
                archivos_imagen = [f for f in os.listdir(ruta_clase) 
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                conteo = len(archivos_imagen)
                nombre_español = self.informacion_clases.get(nombre_clase, {}).get('nombre', nombre_clase)
                conteos_clases[nombre_español] = conteo
                total_imagenes += conteo
                print(f"✅ {nombre_español}: {conteo} imágenes")
        
        print("=" * 50)
        print(f"📈 Total de imágenes: {total_imagenes}")
        print(f"📁 Número de clases: {len(conteos_clases)}")
        print(f"📊 Promedio por clase: {total_imagenes/len(conteos_clases):.0f}")
        
        # Verificar balance
        conteos = list(conteos_clases.values())
        conteo_minimo, conteo_maximo = min(conteos), max(conteos)
        ratio_balance = conteo_minimo / conteo_maximo
        
        if ratio_balance < 0.5:
            print("⚠️  Dataset desbalanceado - considera técnicas de balanceo")
        else:
            print("✅ Dataset relativamente balanceado")
        
        print("=" * 50)
        return conteos_clases, total_imagenes
    
    def preparar_datos(self, ruta_dataset):
        """Prepara los generadores de datos"""
        print("🔄 Preparando generadores de datos...")
        
        # Data augmentation para entrenamiento
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
        
        # Solo rescaling para validación
        generador_datos_validacion = ImageDataGenerator(
            rescale=1./255,
            validation_split=self.division_validacion
        )
        
        # Generador de entrenamiento
        generador_entrenamiento = generador_datos_entrenamiento.flow_from_directory(
            ruta_dataset,
            target_size=(self.alto_img, self.ancho_img),
            batch_size=self.tamaño_lote,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        # Generador de validación
        generador_validacion = generador_datos_validacion.flow_from_directory(
            ruta_dataset,
            target_size=(self.alto_img, self.ancho_img),
            batch_size=self.tamaño_lote,
            class_mode='categorical',
            subset='validation',
            shuffle=False
        )
        
        print(f"✅ Datos de entrenamiento: {generador_entrenamiento.samples} imágenes")
        print(f"✅ Datos de validación: {generador_validacion.samples} imágenes")
        
        return generador_entrenamiento, generador_validacion
    
    def crear_modelo(self, num_clases):
        """Crea el modelo con transfer learning"""
        print("🧠 Creando modelo con transfer learning...")
        
        # Modelo base preentrenado
        modelo_base = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(self.alto_img, self.ancho_img, 3)
        )
        
        # Fine-tuning: descongelar las últimas capas
        modelo_base.trainable = True
        for capa in modelo_base.layers[:-20]:
            capa.trainable = False
        
        # Construir modelo completo
        modelo = tf.keras.Sequential([
            modelo_base,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.4),
            layers.Dense(256, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            layers.Dense(128, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            layers.Dense(num_clases, activation='softmax')
        ])
        
        # Compilar modelo
        modelo.compile(
            optimizer=Adam(learning_rate=0.0001),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'top_k_categorical_accuracy']
        )
        
        # Mostrar resumen
        print("📋 Resumen del modelo:")
        modelo.summary()
        
        return modelo
    
    def entrenar_modelo(self, ruta_dataset, epocas=20, ruta_guardado='eye_disease_model'):
        """Entrena el modelo completo"""
        print("🚀 Iniciando entrenamiento...")
        print("=" * 50)
        
        # Analizar dataset
        self.analizar_dataset(ruta_dataset)
        
        # Preparar datos
        gen_entrenamiento, gen_validacion = self.preparar_datos(ruta_dataset)
        num_clases = len(gen_entrenamiento.class_indices)
        
        # Crear modelo
        modelo = self.crear_modelo(num_clases)
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_accuracy',
                patience=7,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=4,
                min_lr=0.00001,
                verbose=1
            ),
            ModelCheckpoint(
                ruta_guardado,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Entrenar
        print(f"🎯 Entrenando por {epocas} épocas...")
        historial = modelo.fit(
            gen_entrenamiento,
            epochs=epocas,
            validation_data=gen_validacion,
            callbacks=callbacks,
            verbose=1
        )
        
        # Guardar modelo final y diccionarios
        modelo.save(ruta_guardado)
        indices_clases = gen_entrenamiento.class_indices
        np.save('class_indices.npy', indices_clases)
        
        print("=" * 50)
        print(f"✅ Modelo guardado como: {ruta_guardado}")
        print(f"✅ Índices de clases guardados como: class_indices.npy")
        
        # Mostrar métricas finales
        self.graficar_resultados_entrenamiento(historial)
        self.evaluar_modelo(modelo, gen_validacion)
        
        return modelo, historial
    
    def graficar_resultados_entrenamiento(self, historial):
        """Visualiza los resultados del entrenamiento"""
        print("📈 Generando gráficos de entrenamiento...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy
        axes[0, 0].plot(historial.history['accuracy'], label='Entrenamiento', color='blue')
        axes[0, 0].plot(historial.history['val_accuracy'], label='Validación', color='red')
        axes[0, 0].set_title('Precisión del Modelo')
        axes[0, 0].set_xlabel('Época')
        axes[0, 0].set_ylabel('Precisión')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Loss
        axes[0, 1].plot(historial.history['loss'], label='Entrenamiento', color='blue')
        axes[0, 1].plot(historial.history['val_loss'], label='Validación', color='red')
        axes[0, 1].set_title('Pérdida del Modelo')
        axes[0, 1].set_xlabel('Época')
        axes[0, 1].set_ylabel('Pérdida')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Top-k accuracy
        axes[1, 0].plot(historial.history['top_k_categorical_accuracy'], label='Top-K Entrenamiento', color='green')
        axes[1, 0].plot(historial.history['val_top_k_categorical_accuracy'], label='Top-K Validación', color='orange')
        axes[1, 0].set_title('Top-K Categorical Accuracy')
        axes[1, 0].set_xlabel('Época')
        axes[1, 0].set_ylabel('Top-K Accuracy')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Learning rate (si está disponible)
        if 'lr' in historial.history:
            axes[1, 1].plot(historial.history['lr'], color='purple')
            axes[1, 1].set_title('Learning Rate')
            axes[1, 1].set_xlabel('Época')
            axes[1, 1].set_ylabel('Learning Rate')
            axes[1, 1].set_yscale('log')
            axes[1, 1].grid(True)
        else:
            axes[1, 1].text(0.5, 0.5, 'Learning Rate\nno disponible', 
                           ha='center', va='center', transform=axes[1, 1].transAxes)
        
        plt.tight_layout()
        plt.savefig('medical_training_results.png', dpi=300, bbox_inches='tight')
        # plt.show()  # COMENTADO PARA EVITAR QUE EL SCRIPT SE QUEDE BLOQUEADO EN SEGUNDO PLANO
        
        # Mostrar métricas finales
        precision_final = historial.history['val_accuracy'][-1]
        perdida_final = historial.history['val_loss'][-1]
        print(f"📊 Precisión final en validación: {precision_final:.4f}")
        print(f"📊 Pérdida final en validación: {perdida_final:.4f}")
    
    def evaluar_modelo(self, modelo, gen_validacion):
        """Evalúa el modelo en el conjunto de validación"""
        print("🔬 Evaluando modelo en conjunto de validación...")
        
        # Resetear generador
        gen_validacion.reset()
        
        # Predicciones
        predicciones = modelo.predict(gen_validacion, verbose=1)
        clases_predichas = np.argmax(predicciones, axis=1)
        
        # Etiquetas verdaderas
        clases_verdaderas = gen_validacion.classes
        etiquetas_clases = list(gen_validacion.class_indices.keys())
        
        # Reporte de clasificación
        print("\n📋 Reporte de Clasificación:")
        print("=" * 80)
        reporte = classification_report(clases_verdaderas, clases_predichas, 
                                     target_names=etiquetas_clases, 
                                     output_dict=True)
        
        # Mostrar métricas por clase
        for nombre_clase, metricas in reporte.items():
            if isinstance(metricas, dict) and nombre_clase not in ['accuracy', 'macro avg', 'weighted avg']:
                nombre_español = self.informacion_clases.get(nombre_clase, {}).get('nombre', nombre_clase)
                print(f"{nombre_español:30} | Precisión: {metricas['precision']:.3f} | "
                      f"Recall: {metricas['recall']:.3f} | F1: {metricas['f1-score']:.3f}")
        
        print("=" * 80)
        print(f"Precisión general: {reporte['accuracy']:.4f}")
        print(f"F1-score promedio: {reporte['weighted avg']['f1-score']:.4f}")

def principal():
    """Función principal para entrenar el modelo"""
    print("👁️ ENTRENADOR DE CLASIFICADOR DE ENFERMEDADES OCULARES")
    print("=" * 60)
    
    # Configuración
    RUTA_DATASET = "./Dataset"  # Cambia esta ruta si es necesario
    EPOCAS = 25
    NOMBRE_MODELO = "eye_disease_model"
    
    # Verificar que existe el dataset
    if not os.path.exists(RUTA_DATASET):
        print(f"❌ Error: No se encontró el dataset en {RUTA_DATASET}")
        print("📁 Asegúrate de que la carpeta Dataset esté en el directorio actual")
        return
    
    # Crear entrenador
    entrenador = EntrenadorEnfermedadesOculares()
    
    # Entrenar modelo
    try:
        modelo, historial = entrenador.entrenar_modelo(
            ruta_dataset=RUTA_DATASET,
            epocas=EPOCAS,
            ruta_guardado=NOMBRE_MODELO
        )
        
        print("\n🎉 ¡ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
        print("=" * 60)
        print(f"✅ Modelo guardado: {NOMBRE_MODELO}")
        print(f"✅ Índices de clases: class_indices.npy")
        print(f"✅ Gráficos: training_results.png")
        print("\n🚀 Ahora puedes ejecutar 'streamlit run app.py' para usar la aplicación")
        
    except Exception as e:
        print(f"\n❌ Error durante el entrenamiento: {str(e)}")
        print("🔧 Verifica que todas las dependencias están instaladas correctamente")

if __name__ == "__main__":
    principal()
