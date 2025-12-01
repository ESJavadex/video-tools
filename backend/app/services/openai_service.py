from openai import OpenAI
from typing import List, Dict, Any
import time
import json
from pydantic import BaseModel, Field
from app.config import get_settings


# Pydantic models for structured outputs
class HighlightItem(BaseModel):
    timestamp: str = Field(description="Timestamp in format MM:SS or HH:MM:SS")
    text: str = Field(description="Descriptive text for the highlight")


class ActionItemModel(BaseModel):
    action: str = Field(description="The action or commitment mentioned")
    context: str = Field(description="Context or quote from the video")
    priority: str = Field(description="Priority level: alta, media, or baja")


class VideoSuggestionsResponse(BaseModel):
    title: str = Field(description="Attractive YouTube title (max 60 characters)")
    description: str = Field(description="SEO optimized description (150-200 words)")
    thumbnail_prompt: str = Field(description="Detailed prompt for thumbnail generation")
    thumbnail_texts: List[str] = Field(description="5 clickbait texts for thumbnail overlay (short, impactful, max 4-5 words each)")
    highlights: List[HighlightItem] = Field(description="Video highlights/chapters (maximum 5)")
    action_items: List[ActionItemModel] = Field(description="Action items and commitments mentioned")
    linkedin_post: str = Field(description="Engaging LinkedIn post for sharing (350-500 words, very human and conversational)")


class RegenerationResponse(BaseModel):
    titles: List[str] = Field(description="4 alternative title options (max 60 chars each)")
    description: str = Field(description="SEO optimized description (150-200 words)")
    thumbnail_prompt: str = Field(description="Detailed prompt for thumbnail generation")
    thumbnail_texts: List[str] = Field(description="5 clickbait texts for thumbnail overlay (short, impactful, max 4-5 words each)")
    linkedin_post: str = Field(description="Engaging LinkedIn post for sharing (350-500 words, very human and conversational)")


class OpenAIService:
    """OpenAI service adapter that matches the Gemini service interface"""

    def __init__(self, model: str = "gpt-4.1-mini"):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model
        print(f"DEBUG: OpenAI service initialized with model: {self.model}")

    def generate_suggestions(self, transcription: List[Dict], original_filename: str = None) -> Dict[str, Any]:
        """Generate YouTube suggestions based on transcription"""

        # Convert transcription to text
        transcription_text = self._format_transcription(transcription)

        # Add filename context if available
        filename_context = ""
        if original_filename:
            filename_context = f"\n        CONTEXTO: Este contenido proviene del video '{original_filename}'."

        # Create unique prompt to avoid caching
        analysis_id = str(int(time.time()))[-8:]

        prompt = f"""
        ANÁLISIS ID: {analysis_id} | GENERACIÓN DE SUGERENCIAS PARA YOUTUBE
        {filename_context}

        TRANSCRIPCIÓN DEL VIDEO:
        {transcription_text}

        TAREA: Genera sugerencias optimizadas para YouTube basándote ÚNICAMENTE en el contenido transcrito arriba.

        IMPORTANTE:
        - Basa las sugerencias ÚNICAMENTE en el contenido transcrito
        - Genera MÁXIMO 5 highlights/capítulos que capturen ÚNICAMENTE los momentos MÁS IMPORTANTES del video
        - Selecciona los 5 momentos más relevantes, impactantes o representativos del contenido
        - Distribuye los highlights estratégicamente a lo largo de TODO el video
        - ESPACIADO: Los highlights deben estar bien espaciados temporalmente
        - Ejemplo para video de 15 min: 00:00, 03:15, 07:30, 11:45, 15:30
        - Cada highlight debe representar un cambio de tema importante, momento clave o sección destacada
        - El timing debe reflejar los puntos de inflexión o temas principales del contenido
        - La descripción debe ser SEO optimizada y atractiva
        - El título debe ser atractivo (máximo 60 caracteres)

        PARA THUMBNAIL TEXTS (TEXTOS CLICKBAIT):
        - Genera EXACTAMENTE 5 textos cortos y muy clickbait para poner encima del thumbnail
        - Cada texto debe tener MÁXIMO 4-5 palabras
        - Deben ser IMPACTANTES, generar CURIOSIDAD y ganas de hacer clic
        - Usa recursos como: números, preguntas, exclusividad, urgencia, controversia
        - Ejemplos de estilo: "NO HAGAS ESTO", "SECRETO REVELADO", "ESTO CAMBIA TODO", "NADIE TE DICE ESTO", "EL ERROR #1"
        - Deben estar relacionados con el contenido REAL del video
        - Usa MAYÚSCULAS para mayor impacto visual
        - Pueden incluir emojis si aumentan el impacto

        PARA ACTION ITEMS:
        - Identifica TODAS las acciones y compromisos mencionados, incluyendo:
          * Acciones futuras: "voy a", "vamos a", "haré", "haremos", "te voy a", "les voy a"
          * Promesas: "te vas a llevar", "tendrás", "recibirás", "obtendrás"
          * Compromisos: "compartir", "enviar", "mandar", "subir", "publicar", "dar", "proporcionar"
          * Entregas: "documentación", "flujos", "tutoriales", "materiales", "recursos"
        - Ejemplos de frases a detectar:
          * "te vas a llevar todos los flujos" → Acción: Proporcionar flujos
          * "vamos a ir elaborando documentación" → Acción: Crear y compartir documentación
          * "todo esto lo vas a tener disponible" → Acción: Dar acceso a materiales
          * "vamos a establecer contactos" → Acción: Facilitar networking
        - Si no encuentras acciones explícitas, busca compromisos implícitos
        - Asigna prioridad: alta (muy importante), media (normal), baja (mencionado de pasada)
        - El contexto debe incluir la cita exacta del video cuando sea posible

        PARA LINKEDIN POST:
        - Escribe un post SUPER HUMANO y conversacional para LinkedIn (350-500 palabras)
        - FORMATO: Texto plano SIN MARKDOWN (LinkedIn no acepta markdown)
        - Para viñetas usa: • o ► o simplemente saltos de línea
        - NO uses **, *, #, o cualquier sintaxis markdown
        - Usa emojis y MAYÚSCULAS para énfasis en lugar de markdown
        - Detecta si es un PODCAST basándote en:
          * Palabras en transcripción: "podcast", "episodio", "invitado", "conversación"
          * Contexto de entrevista/diálogo entre personas
          * Filename contiene "podcast"
        - Si ES PODCAST:
          * Comienza con "ESTRENO PODCAST!!" o similar entusiasta
          * Presenta al invitado con credenciales y logros
          * Usa • o ► para destacar temas principales (NO markdown)
          * Menciona "episodio", "conversación", "hablamos de"
          * Termina con "Link en comentarios!" o similar
        - Si NO es podcast (tutorial, vlog, etc):
          * Comienza con un gancho relacionado al tema
          * Resume el valor que aporta el contenido
          * Usa • para puntos clave (NO markdown)
          * Termina con call-to-action apropiado
        - IMPORTANTE: Tono muy natural, como si lo escribiera una persona real
        - Usa emojis ocasionales pero sin exagerar
        - Incluye entusiasmo genuino pero sin ser spam
        - Sé específico sobre el contenido, no genérico
        - Ejemplo de estilo del usuario: "Una conversación honesta, sin filtros como ya sabeis, sin guión y llena de experiencias reales"

        Genera las sugerencias en el formato estructurado especificado.
        """

        print(f"DEBUG: Generating suggestions with OpenAI (analysis ID: {analysis_id})")
        print(f"DEBUG: Transcription length: {len(transcription_text)} chars")

        try:
            # Use structured outputs with parse()
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en análisis de contenido para YouTube. Generas sugerencias optimizadas en español basándote en transcripciones de videos."},
                    {"role": "user", "content": prompt}
                ],
                response_format=VideoSuggestionsResponse,
                temperature=0.7
            )

            result = completion.choices[0].message.parsed
            print(f"DEBUG: OpenAI suggestions generated successfully")
            print(f"DEBUG: Title: {result.title}")
            print(f"DEBUG: Highlights: {len(result.highlights)}")
            print(f"DEBUG: Action items: {len(result.action_items)}")

            # Convert Pydantic models to dict format matching Gemini interface
            return {
                "title": result.title,
                "description": result.description,
                "thumbnail_prompt": result.thumbnail_prompt,
                "thumbnail_texts": result.thumbnail_texts,
                "highlights": [{"timestamp": h.timestamp, "text": h.text} for h in result.highlights],
                "action_items": [
                    {
                        "action": item.action,
                        "context": item.context,
                        "priority": item.priority
                    }
                    for item in result.action_items
                ],
                "linkedin_post": result.linkedin_post
            }

        except Exception as e:
            print(f"ERROR: OpenAI suggestions generation failed: {str(e)}")
            # Fallback response
            return {
                "title": "Título generado automáticamente",
                "description": "Descripción generada automáticamente basada en el contenido del video.",
                "thumbnail_prompt": "Thumbnail atractivo para video de YouTube",
                "thumbnail_texts": ["MIRA ESTO", "NO TE LO PIERDAS", "INCREÍBLE", "DEBES VERLO", "WOW"],
                "highlights": [],
                "action_items": [],
                "linkedin_post": "Post para LinkedIn generado automáticamente."
            }

    def regenerate_suggestions(self, transcription: List[Dict], custom_instructions: str = None) -> Dict[str, Any]:
        """Generate new suggestions with custom instructions and 4 title options"""

        transcription_text = self._format_transcription(transcription)

        # Build custom instructions part
        custom_part = ""
        if custom_instructions and custom_instructions.strip():
            custom_part = f"\n\nINSTRUCCIONES PERSONALIZADAS: {custom_instructions.strip()}\n"

        # Create unique prompt
        analysis_id = str(int(time.time()))[-8:]

        prompt = f"""
        REGENERACIÓN ID: {analysis_id} | NUEVAS SUGERENCIAS CON INSTRUCCIONES PERSONALIZADAS

        TRANSCRIPCIÓN DEL VIDEO:
        {transcription_text}
        {custom_part}

        TAREA: Genera nuevas sugerencias para YouTube con 4 opciones de títulos.

        IMPORTANTE:
        - Los 4 títulos deben ser únicos y variados (máximo 60 caracteres cada uno)
        - Sigue las instrucciones personalizadas si se proporcionan
        - La descripción debe ser SEO optimizada (150-200 palabras)
        - El thumbnail prompt debe ser detallado y específico

        PARA THUMBNAIL TEXTS (TEXTOS CLICKBAIT):
        - Genera EXACTAMENTE 5 textos cortos y muy clickbait para poner encima del thumbnail
        - Cada texto debe tener MÁXIMO 4-5 palabras
        - Deben ser IMPACTANTES, generar CURIOSIDAD y ganas de hacer clic
        - Usa recursos como: números, preguntas, exclusividad, urgencia, controversia
        - Ejemplos: "NO HAGAS ESTO", "SECRETO REVELADO", "ESTO CAMBIA TODO", "NADIE TE DICE ESTO", "EL ERROR #1"
        - Relacionados con el contenido REAL del video
        - Usa MAYÚSCULAS para mayor impacto visual

        PARA LINKEDIN POST:
        - Escribe un post SUPER HUMANO y conversacional para LinkedIn (350-500 palabras)
        - FORMATO: Texto plano SIN MARKDOWN (LinkedIn no acepta markdown)
        - Para viñetas usa: • o ► o simplemente saltos de línea
        - NO uses **, *, #, o cualquier sintaxis markdown
        - Usa emojis y MAYÚSCULAS para énfasis
        - Detecta si es un PODCAST basándote en la transcripción
        - Si ES PODCAST:
          * Comienza con "ESTRENO PODCAST!!" o similar entusiasta
          * Presenta al invitado con credenciales
          * Usa • o ► para temas principales (NO markdown)
          * Termina con "Link en comentarios!"
        - Si NO es podcast:
          * Gancho relacionado al tema
          * Valor del contenido
          * Call-to-action apropiado
        - Tono muy natural y humano, como en el ejemplo
        - Sigue las instrucciones personalizadas para el tono

        Genera las sugerencias en el formato estructurado especificado.
        """

        print(f"DEBUG: Regenerating suggestions with OpenAI (ID: {analysis_id})")
        print(f"DEBUG: Custom instructions provided: {bool(custom_instructions)}")

        try:
            # Use structured outputs with parse()
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en análisis de contenido para YouTube. Generas sugerencias optimizadas en español basándote en transcripciones de videos."},
                    {"role": "user", "content": prompt}
                ],
                response_format=RegenerationResponse,
                temperature=0.8  # Higher temperature for more variety
            )

            result = completion.choices[0].message.parsed
            print(f"DEBUG: OpenAI regeneration completed successfully")
            print(f"DEBUG: Generated {len(result.titles)} title options")

            # Convert to dict format
            return {
                "titles": result.titles,
                "description": result.description,
                "thumbnail_prompt": result.thumbnail_prompt,
                "thumbnail_texts": result.thumbnail_texts,
                "linkedin_post": result.linkedin_post
            }

        except Exception as e:
            print(f"ERROR: OpenAI regeneration failed: {str(e)}")
            # Fallback response
            return {
                "titles": [
                    "Título Regenerado 1",
                    "Título Regenerado 2",
                    "Título Regenerado 3",
                    "Título Regenerado 4"
                ],
                "description": "Descripción regenerada automáticamente basada en la transcripción del video.",
                "thumbnail_prompt": "Thumbnail atractivo para video de YouTube",
                "thumbnail_texts": ["MIRA ESTO", "NO TE LO PIERDAS", "INCREÍBLE", "DEBES VERLO", "WOW"],
                "linkedin_post": "Post para LinkedIn regenerado automáticamente."
            }

    def _format_transcription(self, transcription: List[Dict]) -> str:
        """Convert transcription segments to formatted text"""
        return "\n".join([
            f"[{segment.get('timestamp', '00:00')}] {segment.get('text', '')}"
            for segment in transcription
        ])
