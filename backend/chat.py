from fastapi import APIRouter, Depends
from pydantic import BaseModel
from backend.auth import get_current_user
import re

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str
    language: str  # 'es' o 'en'

class ChatResponse(BaseModel):
    response: str
    detected_language: str

# Base de datos local de conocimiento bilingüe
CONOCIMIENTO = {
    "es": [
        {
            "patrones": [r"glaucoma", r"óptico", r"nervio óptico", r"presión intraocular", r"pio"],
            "respuesta": "El Glaucoma es una patología crónica y progresiva que daña el nervio óptico, a menudo relacionada con una presión intraocular elevada. La pérdida visual es irreversible, pero el diagnóstico temprano y el tratamiento (gotas, láser o cirugía) permiten detener la progresión de la enfermedad."
        },
        {
            "patrones": [r"catarata", r"cristalino", r"opacidad"],
            "respuesta": "La Catarata es la opacidad del cristalino del ojo, que provoca una pérdida de visión progresiva y visión borrosa. Se trata con gran éxito mediante cirugía ambulatoria, sustituyendo el cristalino opaco por una lente intraocular (LIO)."
        },
        {
            "patrones": [r"diabet", r"retinopatía diabética", r"azúcar", r"glucosa"],
            "respuesta": "La Retinopatía Diabética es una complicación ocular de la diabetes causada por el daño a los vasos sanguíneos de la retina. El control metabólico y tratamientos como inyecciones anti-VEGF, láser o vitrectomía previenen la ceguera si se aplican a tiempo."
        },
        {
            "patrones": [r"hiperten", r"presión alta", r"vascular", r"hipertensiva"],
            "respuesta": "La Retinopatía Hipertensiva consiste en alteraciones de los vasos retinales causadas por la presión arterial sistémica elevada. El control clínico estricto de la presión arterial detiene las lesiones y, en fases agudas, puede revertirlas."
        },
        {
            "patrones": [r"degeneración macular", r"amd", r"mácula", r"visión central", r"degeneration"],
            "respuesta": "La Degeneración Macular Asociada a la Edad (AMD) afecta la mácula, la zona de la retina responsable de la visión central detallada. Puede ser seca o húmeda, esta última tratable con inyecciones intravítreas anti-VEGF para ralentizar la pérdida visual."
        },
        {
            "patrones": [r"miopía", r"miope", r"elongación", r"refractivo"],
            "respuesta": "La Miopía Patológica o Degenerativa ocurre cuando el ojo se elonga en exceso, aumentando el riesgo de desprendimiento de retina, cicatrices maculares y neovascularización coroidea. Requiere controles de fondo de ojo periódicos."
        },
        {
            "patrones": [r"normal", r"sano", r"fisiológico", r"saludable"],
            "respuesta": "Un ojo sano presenta estructuras retinales, nervio óptico y vasculatura sin anomalías fisiológicas. Se recomiendan revisiones preventivas anuales para mantener la salud ocular."
        },
        {
            "patrones": [r"clahe", r"contraste", r"filtro", r"ecualización"],
            "respuesta": "CLAHE (Contrast Limited Adaptive Histogram Equalization) es un método de procesamiento digital que realza los contrastes de las imágenes médicas locales sin sobreamplificar el ruido, facilitando la visualización de microaneurismas y vasos sanguíneos."
        },
        {
            "patrones": [r"gradcam", r"grad-cam", r"mapa de calor", r"activación", r"explicabilidad"],
            "respuesta": "Grad-CAM (Gradient-weighted Class Activation Mapping) genera un mapa de calor que visualiza en qué regiones de la retina se enfocaron las neuronas convolucionales para tomar la decisión diagnóstica, proporcionando explicabilidad clínica."
        },
        {
            "patrones": [r"mcnemar", r"wilcoxon", r"shapiro", r"cohen", r"estadístic", r"holm", r"hipótesis"],
            "respuesta": "Nuestra suite incluye pruebas de significancia estadística robustas: Shapiro-Wilk para verificar normalidad, T-Student y Wilcoxon para comparar la exactitud de los folds, la d de Cohen para calcular el tamaño de efecto, y McNemar para comparar el nivel de error directo entre modelos."
        },
        {
            "patrones": [r"modelo", r"red", r"arquitectura", r"mobilenet", r"resnet", r"efficientnet", r"híbrido", r"consenso", r"campeón", r"champion"],
            "respuesta": "El sistema evalúa 5 modelos en total: 3 clásicos (MobileNetV2, ResNet50V2 y EfficientNetV2B0), un Ensemble de Consenso que promedia sus probabilidades, y un modelo Champion de Validación Cruzada (que puede ser una Fusión profunda o MobileNet+Random Forest). El mejor modelo se graba automáticamente en formato .h5."
        },
        {
            "patrones": [r"hola", r"buenos días", r"saludos", r"ayuda"],
            "respuesta": "Hola. Soy tu asistente clínico virtual. Puedo ayudarte con dudas sobre glaucoma, retinopatías, cataratas, modelos neuronales, procesamiento CLAHE, o sobre las pruebas estadísticas de la suite clínica. ¿Qué deseas consultar?"
        }
    ],
    "en": [
        {
            "patrones": [r"glaucoma", r"optic nerve", r"intraocular pressure", r"iop"],
            "respuesta": "Glaucoma is a progressive optic nerve disease, often associated with high intraocular pressure (IOP). Vision loss is irreversible, but early diagnosis and management (drops, laser, or surgery) can stop its progression."
        },
        {
            "patrones": [r"cataract", r"lens", r"clouding", r"blurry"],
            "respuesta": "Cataracts involve the clouding of the eye's natural lens, leading to progressive vision loss. It is successfully treated with outpatient surgery, replacing the cloudy lens with an artificial Intraocular Lens (IOL)."
        },
        {
            "patrones": [r"diabet", r"diabetic retinopathy", r"sugar", r"glucose"],
            "respuesta": "Diabetic Retinopathy is a diabetes complication that damages the blood vessels in the retina. Strict metabolic control and treatments (anti-VEGF injections, laser, or vitrectomy) prevent blindness if diagnosed early."
        },
        {
            "patrones": [r"hyperten", r"high blood pressure", r"vascular", r"hypertensive"],
            "respuesta": "Hypertensive Retinopathy is damage to the retinal blood vessels caused by chronic high blood pressure. Controlling systemic blood pressure arrests the lesions and, in acute stages, can reverse them."
        },
        {
            "patrones": [r"macular degeneration", r"amd", r"macula", r"central vision"],
            "respuesta": "Age-related Macular Degeneration (AMD) affects the macula, the part of the retina responsible for sharp central vision. Wet AMD is treated with intraocular anti-VEGF injections to slow down visual loss."
        },
        {
            "patrones": [r"myopia", r"myopic", r"elongation", r"refractive"],
            "respuesta": "Pathological Myopia is caused by excessive elongation of the eyeball, increasing the risks of retinal detachment, macular scars, and choroidal neovascularization. It requires regular fundus examinations."
        },
        {
            "patrones": [r"normal", r"healthy", r"physiological", r"clean"],
            "respuesta": "A healthy eye presents physiological retinal structures, optic disc, and vasculature with no abnormalities. Annual preventive screenings are recommended to preserve ocular health."
        },
        {
            "patrones": [r"clahe", r"contrast", r"filter", r"equalization"],
            "respuesta": "CLAHE (Contrast Limited Adaptive Histogram Equalization) is a preprocessing technique that enhances local image contrast in medical imaging without amplifying noise, helping visualize tiny vessels and microaneurysms."
        },
        {
            "patrones": [r"gradcam", r"grad-cam", r"heatmap", r"activation", r"explainability"],
            "respuesta": "Grad-CAM (Gradient-weighted Class Activation Mapping) produces a visual heatmap showing which regions of the retina the convolutional neural network focused on, offering clinical explainability."
        },
        {
            "patrones": [r"mcnemar", r"wilcoxon", r"shapiro", r"cohen", r"statistic", r"holm", r"hypothesis"],
            "respuesta": "Our suite includes robust statistical tests: Shapiro-Wilk for normality checks, paired T-student & Wilcoxon to compare accuracy distribution across folds, Cohen's d for effect size, and McNemar's test for direct error matrices comparison."
        },
        {
            "patrones": [r"model", r"network", r"architecture", r"mobilenet", r"resnet", r"efficientnet", r"hybrid", r"consensus", r"champion"],
            "respuesta": "The suite runs 5 models: 3 base CNNs (MobileNetV2, ResNet50V2, EfficientNetV2B0), a Consensus Ensemble, and a Cross-Validation Champion (deep hybrid feature fusion or CNN+RF). The best model is auto-saved as a .h5 file."
        },
        {
            "patrones": [r"hello", r"hi", r"greetings", r"help"],
            "respuesta": "Hello. I am your virtual clinical assistant. I can answer questions about glaucoma, retinopathy, cataracts, neural network architectures, CLAHE filtering, or the statistical test suite. How can I help you?"
        }
    ]
}

@router.post("", response_model=ChatResponse)
def get_chat_response(req: ChatRequest, user: str = Depends(get_current_user)):
    """
    Procesa un mensaje del usuario buscando coincidencias de palabras clave clínicas y 
    devuelve la respuesta médica apropiada en español o inglés.
    """
    message_text = req.message.lower()
    lang = req.language if req.language in ["es", "en"] else "es"
    
    # Buscar coincidencia
    for item in CONOCIMIENTO[lang]:
        for patron in item["patrones"]:
            if re.search(patron, message_text):
                return ChatResponse(response=item["respuesta"], detected_language=lang)
                
    # Respuesta por defecto si no hay coincidencia
    if lang == "es":
        default_reply = "Entiendo. Por favor consulta sobre patologías específicas (glaucoma, retinopatía, miopía, cataratas, AMD), procesamiento visual (CLAHE, Grad-CAM), los modelos de la suite (MobileNet, ResNet, Fusión) o las pruebas estadísticas."
    else:
        default_reply = "I understand. Please consult on specific pathologies (glaucoma, retinopathy, cataracts, AMD, myopia), visual processing (CLAHE, Grad-CAM), our models (MobileNet, ResNet, Fusion), or statistical validation methods."
        
    return ChatResponse(response=default_reply, detected_language=lang)
