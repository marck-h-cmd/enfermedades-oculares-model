import requests
from backend.auth import create_access_token

# Generar un token válido
token = create_access_token({"sub": "testuser"})

# Enviar petición al chatbot
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "message": "¿Qué es el glaucoma y cómo se trata?",
    "language": "es"
}

print("Enviando petición a la IA (Groq)...")
try:
    response = requests.post("http://127.0.0.1:8000/api/chat", json=payload, headers=headers)
    print("Código de estado:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print("\n--- RESPUESTA DEL CHATBOT ---")
        print(data.get("response"))
        print("-----------------------------\n")
    else:
        print("Error en la respuesta:", response.text)
except requests.exceptions.ConnectionError:
    print("Error: El servidor backend no está corriendo en el puerto 8000.")
