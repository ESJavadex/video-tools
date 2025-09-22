import google.generativeai as genai
from typing import List, Dict, Any
import time
import json
import re
from app.config import get_settings

class SuggestionsService:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

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

        RESPONDE ÚNICAMENTE CON UN JSON VÁLIDO con esta estructura:
        {{
            "title": "Título atractivo para YouTube (máximo 60 caracteres)",
            "description": "Descripción SEO de 150-200 palabras que resuma el contenido, incluya palabras clave relevantes y sea atractiva para el público objetivo",
            "thumbnail_prompt": "Prompt detallado para generar una imagen thumbnail llamativa que incluya elementos visuales específicos del contenido, colores, texto y composición",
            "highlights": [
                {{"timestamp": "00:00", "text": "Introducción: el problema de los títulos"}},
                {{"timestamp": "01:43", "text": "Idea: usar IA para transcribir y generar títulos"}},
                {{"timestamp": "03:15", "text": "Cómo funciona el flujo (transcripción + LLM)"}},
                {{"timestamp": "05:05", "text": "Qué genera: títulos, descripciones, tags y highlights"}},
                {{"timestamp": "07:37", "text": "Stack elegido (React + FastAPI + Gemini)"}},
                {{"timestamp": "09:11", "text": "Problemas con archivos grandes y solución"}},
                {{"timestamp": "11:38", "text": "Resultados de la transcripción y sugerencias"}},
                {{"timestamp": "13:17", "text": "Reflexión: convertirlo en un SaaS"}},
                {{"timestamp": "15:30", "text": "Conclusión y próximos pasos"}}
            ],
            "action_items": [
                {{
                    "action": "Compartir enlace del repositorio",
                    "context": "Prometí compartir el código en GitHub",
                    "priority": "alta"
                }},
                {{
                    "action": "Enviar presentación por email",
                    "context": "Mencioné que enviaría las diapositivas después de la reunión",
                    "priority": "media"
                }}
            ]
        }}

        IMPORTANTE:
        - Escapa correctamente las comillas en el JSON
        - Basa las sugerencias ÚNICAMENTE en el contenido transcrito
        - Incluye TODOS los momentos importantes del video (mínimo 10-20 highlights para videos largos)
        - Si el video es largo (>10 min), genera AL MENOS 15-25 highlights/capítulos
        - Distribuye los highlights uniformemente a lo largo de TODO el video
        - ESPACIADO CRÍTICO: Mínimo 1 minuto entre highlights, pero sigue el flujo natural del contenido
        - Ejemplo: 00:00, 01:43, 02:50, 06:05...
        - NO pongas highlights consecutivos como 00:30, 00:45 - respeta mínimo 1 minuto
        - El timing debe reflejar cambios reales de tema, no intervalos artificiales
        - NO omitas secciones importantes del video
        - La descripción debe ser SEO optimizada y atractiva

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
        """

        print(f"DEBUG: Generating suggestions with analysis ID: {analysis_id}")
        print(f"DEBUG: Looking for action items in transcription...")
        response = self.model.generate_content(prompt)
        print(f"DEBUG: Raw Gemini response (first 500 chars): {response.text[:500]}")
        print(f"DEBUG: Checking if 'action_items' in response: {'action_items' in response.text}")

        return self._parse_response(response.text)

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

        RESPONDE ÚNICAMENTE CON UN JSON VÁLIDO:
        {{
            "titles": [
                "Título opción 1 (máximo 60 caracteres)",
                "Título opción 2 (máximo 60 caracteres)",
                "Título opción 3 (máximo 60 caracteres)",
                "Título opción 4 (máximo 60 caracteres)"
            ],
            "description": "Descripción SEO de 150-200 palabras optimizada según las instrucciones personalizadas",
            "thumbnail_prompt": "Prompt detallado para thumbnail adaptado a las instrucciones personalizadas"
        }}

        IMPORTANTE:
        - Los 4 títulos deben ser únicos y variados
        - Sigue las instrucciones personalizadas si se proporcionan
        - Escapa correctamente las comillas en el JSON
        """

        print(f"DEBUG: Regenerating suggestions with ID: {analysis_id}")
        response = self.model.generate_content(prompt)

        return self._parse_response(response.text)

    def _format_transcription(self, transcription: List[Dict]) -> str:
        """Convert transcription segments to formatted text"""
        return "\n".join([
            f"[{segment.get('timestamp', '00:00')}] {segment.get('text', '')}"
            for segment in transcription
        ])

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from Gemini"""
        try:
            print(f"DEBUG: Response length: {len(response_text)} chars")

            # Extract JSON from response
            json_str = ""

            # Method 1: Extract from ```json blocks
            if '```json' in response_text:
                start_marker = '```json'
                start_idx = response_text.rfind(start_marker) + len(start_marker)
                remaining_text = response_text[start_idx:]
                end_idx = remaining_text.find('```')
                if end_idx != -1:
                    json_str = remaining_text[:end_idx].strip()
                else:
                    json_str = remaining_text.strip()

            # Method 2: Find JSON object boundaries
            if not json_str or not json_str.startswith('{'):
                start_idx = response_text.find('{')
                if start_idx != -1:
                    brace_count = 0
                    end_idx = start_idx
                    for i, char in enumerate(response_text[start_idx:], start_idx):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                    json_str = response_text[start_idx:end_idx]

            # Clean up JSON
            json_str = json_str.strip()
            last_brace = json_str.rfind('}')
            if last_brace != -1:
                json_str = json_str[:last_brace + 1]

            result = json.loads(json_str)
            print(f"DEBUG: Successfully parsed suggestions")
            print(f"DEBUG: Action items found: {result.get('action_items', [])}")

            # Ensure action_items key exists even if empty
            if 'action_items' not in result:
                result['action_items'] = []
                print(f"DEBUG: No action_items in response, adding empty list")

            # DEBUG: If no action items found, add a demo one for testing UI
            if len(result.get('action_items', [])) == 0:
                print("DEBUG: No action items detected - adding demo item for UI testing")
                result['action_items'] = [{
                    "action": "Revisar el contenido procesado",
                    "context": "DEBUG: No se detectaron acciones específicas en este video. Este es un item de demostración.",
                    "priority": "baja"
                }]

            return result

        except Exception as e:
            print(f"DEBUG: JSON parsing failed: {str(e)}")
            # Fallback response
            return {
                "title": "Título generado automáticamente",
                "titles": [
                    "Título opción 1",
                    "Título opción 2",
                    "Título opción 3",
                    "Título opción 4"
                ] if "titles" in response_text.lower() else None,
                "description": "Descripción generada automáticamente basada en el contenido del video.",
                "thumbnail_prompt": "Thumbnail atractivo para video de YouTube",
                "highlights": [],
                "action_items": []
            }