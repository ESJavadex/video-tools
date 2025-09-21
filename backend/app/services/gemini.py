import google.generativeai as genai
from typing import List, Dict, Any
import os
import time
from app.config import get_settings
from app.models.video import TranscriptionSegment, VideoSuggestions

class GeminiService:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def upload_video(self, video_path: str) -> str:
        """Upload video to Gemini File API"""
        import os
        import random
        filename = os.path.basename(video_path)

        # Create a more unique display name including random component and filename hash
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        file_hash = hash(filename) % 10000  # Simple hash of filename
        short_name = f"v{timestamp}{random_suffix}{file_hash}"[:30]  # Keep under 40 chars

        print(f"DEBUG: About to upload file with display_name: {short_name} (length: {len(short_name)})")
        print(f"DEBUG: Local file path: {video_path}")
        print(f"DEBUG: Original filename hash: {file_hash}")

        video_file = genai.upload_file(
            path=video_path,
            display_name=short_name
        )

        print(f"DEBUG: Upload successful. File name: {video_file.name}")
        print(f"DEBUG: File URI: {video_file.uri}")
        print(f"DEBUG: File display name: {getattr(video_file, 'display_name', 'N/A')}")

        # Wait for file to be processed with additional safety delay
        while video_file.state.name == "PROCESSING":
            print(f"DEBUG: File still processing, waiting...")
            time.sleep(3)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name != "ACTIVE":
            raise Exception(f"File upload failed with state: {video_file.state.name}")

        print(f"DEBUG: File is now ACTIVE, waiting additional 5 seconds for stability...")
        time.sleep(5)  # Additional delay to ensure file is fully ready

        return video_file.name  # Return the file name, not URI

    def transcribe_video_only(self, video_file_name: str, language: str = "es", original_filename: str = None) -> List[Dict[str, str]]:
        """First call: Only transcribe the video, no analysis"""

        import uuid
        transcription_id = str(uuid.uuid4())[:8]
        current_time = int(time.time())

        filename_context = ""
        if original_filename:
            filename_context = f"\nCONTEXTO: El video que debes transcribir se llama '{original_filename}'."

        # Simple transcription-only prompt
        transcription_prompt = f"""
        TRANSCRIPCIÓN ID: {transcription_id} | TIMESTAMP: {current_time}
        {filename_context}

        TAREA: SOLO TRANSCRIBIR el video completo con timestamps.

        INSTRUCCIONES:
        - Transcribe TODO el contenido del video de principio a fin
        - No omitas ninguna parte del video
        - Usa timestamps cada 15-30 segundos aproximadamente
        - El video está en idioma: {language}
        - NO hagas análisis, solo transcripción

        Formato JSON requerido:
        {{
            "transcription": [
                {{"timestamp": "00:00", "text": "texto exacto del video"}},
                {{"timestamp": "00:30", "text": "siguiente segmento"}},
                {{"timestamp": "01:00", "text": "más contenido"}}
            ]
        }}

        Responde SOLO con el JSON de transcripción:
        """

        print(f"DEBUG: [STEP 1] Starting transcription-only for: {video_file_name}")

        try:
            video_file_ref = genai.get_file(video_file_name)
            print(f"DEBUG: [STEP 1] Got file reference: {video_file_ref.name}")
        except Exception as e:
            print(f"DEBUG: [STEP 1] Error getting file reference: {str(e)}")
            raise

        response = self.model.generate_content([
            video_file_ref,
            transcription_prompt
        ])

        # Parse transcription response
        import json
        try:
            transcription_result = self._parse_response(response.text)
            transcription_segments = transcription_result.get("transcription", [])
            print(f"DEBUG: [STEP 1] Transcription completed: {len(transcription_segments)} segments")
            return transcription_segments
        except Exception as e:
            print(f"DEBUG: [STEP 1] Transcription parsing failed: {str(e)}")
            return self._parse_text_response(response.text).get("transcription", [])

    def analyze_transcription(self, transcription_segments: List[Dict[str, str]], original_filename: str = None) -> Dict[str, Any]:
        """Second call: Analyze the transcription to generate suggestions"""

        import uuid
        analysis_id = str(uuid.uuid4())[:8]

        # Convert transcription to text
        transcription_text = "\n".join([
            f"[{segment.get('timestamp', '00:00')}] {segment.get('text', '')}"
            for segment in transcription_segments
        ])

        filename_context = ""
        if original_filename:
            filename_context = f"\nVIDEO: '{original_filename}'"

        # Analysis-only prompt
        analysis_prompt = f"""
        ANÁLISIS ID: {analysis_id} | Javi (Canal YouTube)
        {filename_context}

        TAREA: Analizar la siguiente transcripción y generar sugerencias para YouTube.

        TRANSCRIPCIÓN DEL VIDEO:
        {transcription_text}

        INSTRUCCIONES:
        - Genera contenido listo para copiar/pegar en YouTube
        - Si el video es largo (>10 min), crea MUCHOS highlights (15-30 mínimo)
        - Distribuye highlights por TODO el video, no solo el inicio
        - ESPACIADO CRÍTICO: Mínimo 1 minuto entre highlights, pero sigue el flujo natural del contenido
        - Ejemplo: 00:00, 01:43, 02:50, 06:05...
        - NO pongas highlights consecutivos como 00:30, 00:45 - respeta mínimo 1 minuto
        - El timing debe reflejar cambios reales de tema, no intervalos artificiales
        - Cada highlight debe ser único y representativo
        - Hazlo personal para Javi

        Formato JSON requerido:
        {{
            "title": "Título YouTube atractivo (máx 60 caracteres)",
            "description": "Descripción SEO optimizada 150-200 palabras con palabras clave",
            "thumbnail_prompt": "Prompt detallado para thumbnail llamativo con elementos visuales específicos",
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
            ]
        }}

        Responde SOLO con el JSON de análisis:
        """

        print(f"DEBUG: [STEP 2] Starting analysis of {len(transcription_segments)} segments")

        response = self.model.generate_content(analysis_prompt)

        try:
            analysis_result = self._parse_response(response.text)
            print(f"DEBUG: [STEP 2] Analysis completed: {len(analysis_result.get('highlights', []))} highlights")
            return analysis_result
        except Exception as e:
            print(f"DEBUG: [STEP 2] Analysis parsing failed: {str(e)}")
            return {
                "title": "Título generado automáticamente",
                "description": "Descripción generada automáticamente",
                "thumbnail_prompt": "Thumbnail atractivo para YouTube",
                "highlights": []
            }

    def transcribe_video(self, video_file_name: str, language: str = "es", original_filename: str = None) -> Dict[str, Any]:
        """Main method: Two-step process - transcribe then analyze"""

        print(f"DEBUG: Starting two-step process for {original_filename or 'video'}")

        # Step 1: Transcribe only
        transcription_segments = self.transcribe_video_only(video_file_name, language, original_filename)

        # Step 2: Analyze transcription
        analysis_result = self.analyze_transcription(transcription_segments, original_filename)

        # Combine results
        final_result = {
            "transcription": transcription_segments,
            "title": analysis_result.get("title", ""),
            "description": analysis_result.get("description", ""),
            "thumbnail_prompt": analysis_result.get("thumbnail_prompt", ""),
            "highlights": analysis_result.get("highlights", [])
        }

        print(f"DEBUG: Two-step process completed:")
        print(f"  - Transcription: {len(transcription_segments)} segments")
        print(f"  - Highlights: {len(final_result['highlights'])} moments")

        return final_result

    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Fallback parser if JSON response fails"""
        print(f"DEBUG: Using fallback parser for response of length {len(text)}")

        lines = text.split('\n')
        transcription = []
        highlights = []
        title = "Video sin título"
        description = "Descripción generada automáticamente"
        thumbnail_prompt = "Thumbnail genérico para video de YouTube"

        # Try to extract structured content from the malformed response
        current_section = None
        for line in lines:
            line = line.strip()

            # Look for timestamp patterns like "timestamp": "00:00"
            if '"timestamp"' in line and '"text"' in line:
                try:
                    # Extract timestamp and text from JSON-like line
                    import re
                    timestamp_match = re.search(r'"timestamp":\s*"([^"]+)"', line)
                    text_match = re.search(r'"text":\s*"([^"]+)"', line)

                    if timestamp_match and text_match:
                        transcription.append({
                            "timestamp": timestamp_match.group(1),
                            "text": text_match.group(1)
                        })
                except:
                    pass

            # Look for title, description, etc.
            if '"title"' in line:
                try:
                    import re
                    title_match = re.search(r'"title":\s*"([^"]+)"', line)
                    if title_match:
                        title = title_match.group(1)
                except:
                    pass

            if '"description"' in line:
                try:
                    import re
                    desc_match = re.search(r'"description":\s*"([^"]+)"', line)
                    if desc_match:
                        description = desc_match.group(1)
                except:
                    pass

            if '"thumbnail_prompt"' in line:
                try:
                    import re
                    thumb_match = re.search(r'"thumbnail_prompt":\s*"([^"]+)"', line)
                    if thumb_match:
                        thumbnail_prompt = thumb_match.group(1)
                except:
                    pass

        # If no structured content found, try traditional timestamp parsing
        if not transcription:
            for line in lines:
                if line.strip().startswith('[') and ']' in line:
                    try:
                        timestamp = line[line.find('[')+1:line.find(']')]
                        text_content = line[line.find(']')+1:].strip()
                        if text_content:
                            transcription.append({
                                "timestamp": timestamp,
                                "text": text_content
                            })
                    except:
                        pass

        print(f"DEBUG: Fallback extracted {len(transcription)} transcription segments")
        print(f"DEBUG: Fallback title: {title}")

        # Generate basic suggestions
        return {
            "transcription": transcription if transcription else [{"timestamp": "00:00", "text": "Transcripción no disponible"}],
            "title": title,
            "description": description,
            "thumbnail_prompt": thumbnail_prompt,
            "highlights": highlights
        }

    def generate_chapters(self, transcription: List[Dict]) -> List[TranscriptionSegment]:
        """Generate chapter timestamps from transcription"""
        prompt = f"""
        Basándote en esta transcripción, genera capítulos/momentos destacados para YouTube.
        Cada capítulo debe tener:
        - Timestamp exacto
        - Título descriptivo corto
        - Tema principal

        Transcripción:
        {transcription}

        Responde con una lista de capítulos en formato:
        HH:MM:SS - Título del capítulo
        """

        response = self.model.generate_content(prompt)

        chapters = []
        for line in response.text.split('\n'):
            if '-' in line:
                parts = line.split('-', 1)
                if len(parts) == 2:
                    timestamp = parts[0].strip()
                    text = parts[1].strip()
                    chapters.append(TranscriptionSegment(
                        timestamp=timestamp,
                        text=text,
                        start_seconds=self._timestamp_to_seconds(timestamp)
                    ))

        return chapters

    def regenerate_suggestions(self, transcription: List[Dict], custom_instructions: str = None) -> Dict[str, Any]:
        """Generate new suggestions based on existing transcription with custom instructions"""

        # Convert transcription to text for context
        transcription_text = "\n".join([f"[{seg['timestamp']}] {seg['text']}" for seg in transcription])

        # Build custom instructions part
        custom_part = ""
        if custom_instructions and custom_instructions.strip():
            custom_part = f"\n\nINSTRUCCIONES PERSONALIZADAS: {custom_instructions.strip()}\n"

        # Prompt for regenerating suggestions
        regeneration_prompt = f"""
        INSTRUCCIONES: Basándote en la siguiente transcripción de video, genera nuevas sugerencias para YouTube. Responde ÚNICAMENTE con un JSON válido.

        TRANSCRIPCIÓN DEL VIDEO:
        {transcription_text}
        {custom_part}
        TAREAS:
        1. TÍTULOS: Genera 4 opciones de títulos atractivos (máximo 60 caracteres cada uno)
        2. DESCRIPCIÓN: Descripción SEO de 150-200 palabras
        3. THUMBNAIL: Prompt detallado para generar thumbnail

        IMPORTANTE:
        - Escapa correctamente las comillas en el JSON
        - Los títulos deben ser variados y atractivos
        - Incluye palabras clave relevantes en la descripción
        - El thumbnail debe ser específico del contenido

        Estructura JSON requerida:
        {{
            "titles": [
                "Título opción 1 (máximo 60 caracteres)",
                "Título opción 2 (máximo 60 caracteres)",
                "Título opción 3 (máximo 60 caracteres)",
                "Título opción 4 (máximo 60 caracteres)"
            ],
            "description": "Descripción SEO de 150-200 palabras que resuma el contenido del video, incluya palabras clave relevantes y sea atractiva para el público objetivo",
            "thumbnail_prompt": "Prompt detallado para generar una imagen thumbnail llamativa que incluya elementos visuales específicos del video, colores, texto y composición"
        }}

        Responde SOLO con el JSON, sin texto adicional:
        """

        print(f"DEBUG: Regenerating suggestions with custom instructions: {bool(custom_instructions)}")

        response = self.model.generate_content(regeneration_prompt)

        # Parse response
        import json
        import re
        try:
            response_text = response.text
            print(f"DEBUG: Regeneration response length: {len(response_text)} chars")

            # Extract JSON from response
            json_str = ""

            if '```json' in response_text:
                start_marker = '```json'
                start_idx = response_text.rfind(start_marker) + len(start_marker)
                remaining_text = response_text[start_idx:]
                end_idx = remaining_text.find('```')
                if end_idx != -1:
                    json_str = remaining_text[:end_idx].strip()
                else:
                    json_str = remaining_text.strip()

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

            json_str = json_str.strip()
            last_brace = json_str.rfind('}')
            if last_brace != -1:
                json_str = json_str[:last_brace + 1]

            result = json.loads(json_str)
            print(f"DEBUG: Successfully regenerated suggestions with {len(result.get('titles', []))} titles")

        except Exception as e:
            print(f"DEBUG: JSON parsing failed in regeneration: {str(e)}")
            # Fallback
            result = {
                "titles": [
                    "Título Regenerado 1",
                    "Título Regenerado 2",
                    "Título Regenerado 3",
                    "Título Regenerado 4"
                ],
                "description": "Descripción regenerada automáticamente basada en la transcripción del video.",
                "thumbnail_prompt": "Thumbnail atractivo para video de YouTube"
            }

        return result

    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """Convert MM:SS or HH:MM:SS to seconds"""
        parts = timestamp.split(':')
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return 0.0