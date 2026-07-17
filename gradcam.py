import numpy as np
import tensorflow as tf
import cv2

def get_gradcam_heatmap(model, img_array, class_idx=None):
    """
    Genera el mapa de calor Grad-CAM de forma genérica para modelos Keras
    compatibles con MobileNetV2, ResNet50V2 y EfficientNetV2B0.
    """
    # Intentar buscar el submodelo base (como en Transfer Learning)
    base_model = None
    for layer in model.layers:
        if isinstance(layer, tf.keras.Model) or hasattr(layer, 'layers'):
            base_model = layer
            break
            
    if base_model is None:
        base_model = model

    # Buscar la última capa convolucional en el modelo base
    last_conv_layer = None
    # Nombres típicos de capas finales convolucionales según la arquitectura
    nombres_capas_candidatas = [
        'Conv_1',               # MobileNetV2
        'post_relu',            # ResNet50V2
        'top_activation',       # EfficientNetV2B0/EfficientNetB0
        'conv5_block3_out',     # ResNet50
        'conv2d'                # Genérico
    ]
    
    # Primero buscamos en base a nombres comunes
    for name in nombres_capas_candidatas:
        try:
            last_conv_layer = base_model.get_layer(name)
            break
        except ValueError:
            continue
            
    # Si no se encuentra por nombre, buscar la última capa que tenga 'conv' o 'activation' en su nombre
    if last_conv_layer is None:
        for layer in reversed(base_model.layers):
            if 'conv' in layer.name.lower() or 'activation' in layer.name.lower():
                last_conv_layer = layer
                break
                
    if last_conv_layer is None:
        # Fallback al último elemento del modelo base
        last_conv_layer = base_model.layers[-1]

    # Crear un modelo que genere los mapas de activación de la última capa conv
    # y la salida de predicción final
    try:
        # Si es un modelo secuencial que envuelve al submodelo base
        if base_model != model:
            base_idx = model.layers.index(base_model)
            
            # Crear un modelo intermedio para el submodelo base
            grad_model_base = tf.keras.Model(
                inputs=base_model.inputs,
                outputs=[last_conv_layer.output, base_model.output]
            )
            
            # Registrar gradientes con GradientTape
            with tf.GradientTape() as tape:
                conv_outputs, base_outputs = grad_model_base(img_array)
                # Pasar las salidas del base_model a través de las capas restantes de model
                x = base_outputs
                for layer in model.layers[base_idx+1:]:
                    x = layer(x)
                predictions = x
                
                if class_idx is None:
                    class_idx = tf.argmax(predictions[0])
                class_channel = predictions[:, class_idx]
                
            # Gradientes del canal de clase con respecto a los mapas de activación de la conv
            grads = tape.gradient(class_channel, conv_outputs)
            
        else:
            # Modelo funcional directo (ej. Fusión)
            grad_model = tf.keras.Model(
                inputs=model.inputs,
                outputs=[last_conv_layer.output, model.output]
            )
            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(img_array)
                if class_idx is None:
                    class_idx = tf.argmax(predictions[0])
                class_channel = predictions[:, class_idx]
                
            grads = tape.gradient(class_channel, conv_outputs)
            
        # Media de los gradientes sobre los ejes espaciales (pooled gradients)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Multiplicar los mapas de activación por la importancia de canal
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        # Aplicar ReLU para mantener solo las características positivas
        heatmap = tf.maximum(heatmap, 0.0)
        max_val = tf.math.reduce_max(heatmap)
        if max_val > 0:
            heatmap = heatmap / max_val
            
        return heatmap.numpy()
        
    except Exception as e:
        print(f"Error generando heatmap Grad-CAM: {str(e)}")
        # Generar un heatmap vacío si hay algún error inesperado
        return np.zeros((7, 7))

def overlay_gradcam(img_array, heatmap, alpha=0.4, colormap=cv2.COLORMAP_JET):
    """
    Superpone el mapa de calor sobre la imagen original.
    """
    img = img_array.copy()
    if len(img.shape) == 3 and img.shape[2] == 3:
        # Escalar a 0-255 si está en formato float 0-1
        if img.max() <= 1.0:
            img = np.uint8(255 * img)
    else:
        # Formato incorrecto, retornar original
        return img
        
    # Redimensionar el heatmap a las dimensiones de la imagen original
    heatmap_resized = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
    
    # Convertir a uint8 [0, 255]
    heatmap_uint8 = np.uint8(255 * heatmap_resized)
    
    # Aplicar mapa de colores
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, colormap)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    # Superponer
    output_img = cv2.addWeighted(img, 1.0 - alpha, heatmap_colored, alpha, 0)
    return output_img
