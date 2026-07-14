import os
import sys
import json
import pickle
import tensorflow as tf
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Asegurar codificación utf-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from backend import auth, predict, stats, reports

# Rutas de los modelos entrenados
MODELS_PATHS = {
    "mobilenet": "eye_disease_model",
    "resnet": "ensemble_resnet_model",
    "efficientnet": "ensemble_efficientnet_model",
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carga de modelos durante el inicio
    print("⏳ Pre-cargando modelos TensorFlow en memoria...")
    app.state.models = {}
    
    # 1. Cargar modelos base si existen
    for name, path in MODELS_PATHS.items():
        if os.path.exists(path):
            try:
                print(f"   Cargando modelo base: {name} de '{path}'...")
                app.state.models[name] = tf.keras.models.load_model(path)
                print(f"   ✅ {name} cargado con éxito.")
            except Exception as e:
                print(f"   ❌ Error al cargar modelo base {name}: {str(e)}")
                
    # 2. Cargar el mejor modelo (Champion de CV) y su metadata desde 'models/'
    meta_path = "models/best_model_meta_v1.json"
    best_model_path = "models/best_ocular_model_v1.h5"
    best_rf_path = "models/best_rf_classifier_v1.pkl"
    
    # Fallback al directorio raíz si no está en la carpeta models/ aún
    if not os.path.exists(meta_path):
        meta_path = "best_model_meta.json"
        best_model_path = "best_ocular_model.h5"
        best_rf_path = "best_rf_classifier.pkl"
        
    if os.path.exists(meta_path) and os.path.exists(best_model_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            app.state.models["champion_meta"] = meta
            
            print(f"   Cargando mejor modelo de CV ({meta.get('nombre', 'unificado')})...")
            app.state.models["champion"] = tf.keras.models.load_model(best_model_path)
            print("   ✅ Modelo Champion cargado.")
            
            if meta.get("tipo") == "cnn_rf" and os.path.exists(best_rf_path):
                print("   Cargando clasificador Random Forest complementario...")
                with open(best_rf_path, "rb") as f:
                    app.state.models["rf_classifier"] = pickle.load(f)
                print("   ✅ Random Forest cargado.")
        except Exception as e:
            print(f"   ❌ Error cargando modelo champion: {str(e)}")
            
    print("🚀 Modelos pre-cargados y listos en memoria.")
    yield
    # Limpieza al apagar
    app.state.models.clear()

app = FastAPI(
    title="Hospital Ocular - API de Diagnóstico Clínico",
    description="Servicios de inferencia y validación estadística con soporte para mapas de activación Grad-CAM y CLAHE.",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para conectar con React en el puerto 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login", tags=["Authentication"])
def login(req: LoginRequest):
    """
    Endpoint para login de usuarios del personal clínico.
    Retorna un JWT de acceso si las credenciales son válidas.
    """
    if req.username == "admin" and req.password == "admin":
        access_token = auth.create_access_token(data={"sub": req.username})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "username": req.username
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Intente con admin / admin.",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Registrar Routers de Endpoints
app.include_router(predict.router)
app.include_router(stats.router)
app.include_router(reports.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
