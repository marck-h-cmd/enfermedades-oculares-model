import os
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.optimizers import Adam, RMSprop
import time

class TunerHiperparametros:
    """
    Clase encargada de buscar hiperparámetros óptimos para los modelos CNN.
    Realiza una búsqueda tipo Grid Search o Random Search rápida sobre épocas controladas
    para no consumir excesivo tiempo de cómputo.
    """
    def __init__(self, ruta_dataset, alto_img=224, ancho_img=224):
        self.ruta_dataset = ruta_dataset
        self.alto_img = alto_img
        self.ancho_img = ancho_img
        self.division_validacion = 0.2

    def preparar_datos_rapidos(self, batch_size=32):
        """Generadores de datos rápidos para tuning"""
        gen_datos = ImageDataGenerator(
            rescale=1./255,
            validation_split=self.division_validacion
        )
        
        gen_train = gen_datos.flow_from_directory(
            self.ruta_dataset,
            target_size=(self.alto_img, self.ancho_img),
            batch_size=batch_size,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        gen_val = gen_datos.flow_from_directory(
            self.ruta_dataset,
            target_size=(self.alto_img, self.ancho_img),
            batch_size=batch_size,
            class_mode='categorical',
            subset='validation',
            shuffle=False
        )
        
        return gen_train, gen_val

    def construir_modelo(self, lr, dropout_rate, opt_name, num_clases):
        """Crea el modelo MobileNetV2 con parámetros variables"""
        modelo_base = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(self.alto_img, self.ancho_img, 3)
        )
        modelo_base.trainable = False  # Congelado para tuning rápido
        
        x = modelo_base.output
        x = layers.GlobalAveragePooling2D()(x)
        x = layers.Dropout(dropout_rate)(x)
        x = layers.Dense(128, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(dropout_rate / 2)(x)
        
        predicciones = layers.Dense(num_clases, activation='softmax')(x)
        modelo = Model(inputs=modelo_base.input, outputs=predicciones)
        
        # Seleccionar optimizador
        if opt_name == 'adam':
            optimizer = Adam(learning_rate=lr)
        else:
            optimizer = RMSprop(learning_rate=lr)
            
        modelo.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return modelo

    def buscar(self, epocas=3, batch_size=64, callback_progreso=None):
        """
        Ejecuta la búsqueda de hiperparámetros.
        Permite recibir un callback para reportar progreso a Streamlit.
        """
        gen_train, gen_val = self.preparar_datos_rapidos(batch_size)
        num_clases = len(gen_train.class_indices)
        
        # Espacio de búsqueda
        learning_rates = [0.001, 0.0001]
        dropouts = [0.2, 0.4]
        optimizadores = ['adam', 'rmsprop']
        
        total_combinaciones = len(learning_rates) * len(dropouts) * len(optimizadores)
        comb_actual = 0
        
        historial_busqueda = []
        mejor_accuracy = 0.0
        mejores_params = {}
        
        for lr in learning_rates:
            for dp in dropouts:
                for opt in optimizadores:
                    comb_actual += 1
                    params_str = f"LR={lr}, Dropout={dp}, Opt={opt}"
                    print(f"🔄 Probando combinación {comb_actual}/{total_combinaciones}: {params_str}")
                    
                    if callback_progreso:
                        callback_progreso(comb_actual, total_combinaciones, f"Probando: {params_str}")
                        
                    # Medir tiempo
                    t_inicio = time.time()
                    modelo = self.construir_modelo(lr, dp, opt, num_clases)
                    
                    # Entrenamiento muy rápido (pocas épocas)
                    # Usamos steps reducidos para que termine muy rápido
                    pasos_por_epoca = min(len(gen_train), 5) 
                    pasos_val = min(len(gen_val), 3)
                    
                    historial = modelo.fit(
                        gen_train,
                        epochs=epocas,
                        steps_per_epoch=pasos_por_epoca,
                        validation_data=gen_val,
                        validation_steps=pasos_val,
                        verbose=0
                    )
                    
                    t_fin = time.time()
                    val_acc = max(historial.history['val_accuracy'])
                    tiempo_transcurrido = t_fin - t_inicio
                    
                    historial_busqueda.append({
                        'lr': lr,
                        'dropout': dp,
                        'optimizador': opt,
                        'val_accuracy': val_acc,
                        'tiempo_segundos': tiempo_transcurrido
                    })
                    
                    print(f"   Accuracy validación: {val_acc:.4f} (Tiempo: {tiempo_transcurrido:.1f}s)")
                    
                    if val_acc > mejor_accuracy:
                        mejor_accuracy = val_acc
                        mejores_params = {
                            'lr': lr,
                            'dropout': dp,
                            'optimizador': opt,
                            'val_accuracy': val_acc
                        }
                        
        print(f"🏆 Mejor combinación encontrada: {mejores_params}")
        return mejores_params, historial_busqueda

if __name__ == "__main__":
    # Prueba rápida
    if os.path.exists("./Dataset"):
        tuner = TunerHiperparametros("./Dataset")
        mejores_p, hist = tuner.buscar(epocas=1)
        print("Finalizado. Mejor:", mejores_p)
