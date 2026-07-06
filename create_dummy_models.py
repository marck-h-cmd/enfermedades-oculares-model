import tensorflow as tf
import numpy as np
from keras import layers, models

def create_dummy_model():
    model = models.Sequential([
        layers.Input(shape=(224, 224, 3)),
        layers.GlobalAveragePooling2D(),
        layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

print("Creando modelos dummy...")

# Crear y guardar los modelos
model1 = create_dummy_model()
model1.save('eye_disease_model')
print("Guardado eye_disease_model")

model2 = create_dummy_model()
model2.save('ensemble_efficientnet_model')
print("Guardado ensemble_efficientnet_model")

model3 = create_dummy_model()
model3.save('ensemble_resnet_model')
print("Guardado ensemble_resnet_model")

# Nombres de las clases (10 clases según train_model.py)
class_names = [
    'Central Serous Chorioretinopathy [Color Fundus]',
    'Diabetic Retinopathy',
    'Disc Edema',
    'Glaucoma',
    'Healthy',
    'Macular Scar',
    'Myopia',
    'Pterygium',
    'Retinal Detachment',
    'Retinitis Pigmentosa'
]

# Crear diccionario {nombre: indice}
class_indices = {name: i for i, name in enumerate(class_names)}

# Guardar class_indices.npy y ensemble_class_indices.npy
np.save('class_indices.npy', class_indices)
np.save('ensemble_class_indices.npy', class_indices)
print("Guardados archivos de índices de clases (.npy)")
print("¡Listo!")
