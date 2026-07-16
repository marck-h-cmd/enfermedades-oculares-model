import os
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.auth import get_current_user
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str
    language: str

class ChatResponse(BaseModel):
    response: str
    detected_language: str

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

@router.post("", response_model=ChatResponse)
def get_chat_response(req: ChatRequest, user: str = Depends(get_current_user)):
    """
    Procesa un mensaje usando la API de Groq (Llama 3) y devuelve una respuesta médica.
    """
    message_text = req.message
    lang = req.language if req.language in ["es", "en", "pt", "fr", "zh"] else "es"
    
    # Prompt de sistema dinámico en función del idioma
    language_instructions = {
        "es": "Responde de manera concisa y estrictamente en español.",
        "en": "Respond concisely and strictly in English.",
        "pt": "Responda de forma concisa e estritamente em português.",
        "fr": "Répondez de manière concise et strictement en français.",
        "zh": "请简明扼要地严格用中文回复。"
    }

    system_prompt = (
        "Eres un asistente clínico oftalmológico experto de la suite médica OcularDiagnose. "
        "Tu objetivo es proveer información clara, profesional y muy útil sobre patologías (glaucoma, cataratas, retinopatía miópica, hipertensiva, diabética, AMD), "
        "y sobre los modelos de IA del sistema (MobileNet, ResNet, EfficientNet, Grad-CAM, CLAHE, Random Forest). "
        "Nunca des un diagnóstico definitivo a un paciente y mantén tus respuestas lo más cortas y precisas posibles (máximo 3-4 oraciones). "
        f"{language_instructions.get(lang, language_instructions['es'])}"
    )

    try:
        if not client.api_key or client.api_key == "PegaTuClaveDeGroqAqui" or client.api_key.strip() == "":
            raise ValueError("No hay una GROQ_API_KEY válida configurada.")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": message_text
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=300,
        )
        response_text = chat_completion.choices[0].message.content
        return ChatResponse(response=response_text, detected_language=lang)

    except Exception as e:
        # Fallback en caso de error
        print(f"Error con Groq API: {e}")
        error_msgs = {
            "es": "Actualmente no puedo conectar con el servidor de inteligencia artificial. Por favor, asegúrate de haber pegado tu API Key de Groq en el archivo .env y reiniciado el servidor.",
            "en": "I cannot connect to the AI server right now. Please ensure you have pasted your Groq API Key in the .env file and restarted the server.",
            "pt": "Não consigo conectar ao servidor de IA no momento. Certifique-se de ter colado sua API Key da Groq no arquivo .env e reiniciado o servidor.",
            "fr": "Je ne peux pas me connecter au serveur d'IA pour le moment. Veuillez vous assurer d'avoir collé votre clé API Groq dans le fichier .env et redémarré le serveur.",
            "zh": "我目前无法连接到人工智能服务器。请确保您已将 Groq API 密钥粘贴到 .env 文件中并重新启动了服务器。"
        }
        return ChatResponse(response=error_msgs.get(lang, error_msgs["es"]), detected_language=lang)
