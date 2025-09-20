# YouTube Video Tools Suite

Herramientas de procesamiento de video con IA para YouTube. Transcribe videos, genera títulos optimizados, descripciones SEO y sugerencias de thumbnails.

## Características

- **Transcripción Automática**: Convierte audio a texto con timestamps precisos usando Gemini AI
- **Sugerencias de Contenido**: Genera títulos atractivos y descripciones optimizadas para SEO
- **Prompt para Thumbnails**: Obtén prompts detallados para crear thumbnails con IA
- **Capítulos Automáticos**: Genera momentos destacados con timestamps para mejorar navegación

## Requisitos

- Python 3.8+
- Node.js 18+
- API Key de Google Gemini

## Instalación

### 1. Configurar Backend (Python + FastAPI)

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar Frontend (React + Vite)

```bash
cd frontend
npm install
```

### 3. Configurar API Key

El archivo `.env` ya está configurado con tu API key de Gemini en ambas carpetas.

## Ejecutar la Aplicación

### 1. Iniciar el Backend

```bash
cd backend
python -m uvicorn app.main:app --reload
```

El servidor estará disponible en: http://localhost:8000
Documentación API: http://localhost:8000/docs

### 2. Iniciar el Frontend

En otra terminal:

```bash
cd frontend
npm run dev
```

La aplicación estará disponible en: http://localhost:5173

## Uso

1. Abre http://localhost:5173 en tu navegador
2. Arrastra o selecciona un video local (MP4, AVI, MOV, MKV, WebM, MPEG)
3. Espera mientras se procesa (puede tomar 1-2 minutos)
4. Revisa la transcripción con timestamps
5. Copia las sugerencias generadas:
   - Título optimizado
   - Descripción con SEO
   - Prompt para thumbnail
   - Capítulos/momentos destacados

## Formatos Soportados

- **Video**: MP4, AVI, MOV, MKV, WebM, MPEG
- **Tamaño máximo**: 5 GB
- **Duración**: Hasta 2 horas
- **Idiomas**: Optimizado para español

## API Endpoints

- `POST /api/videos/process` - Sube y procesa un video
- `GET /api/videos/health` - Verifica estado del servicio

## Estructura del Proyecto

```
video-tools/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── config.py         # Configuración
│   │   ├── models/           # Modelos Pydantic
│   │   ├── services/         # Lógica de negocio
│   │   └── routers/          # Endpoints API
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.tsx           # Componente principal
    │   ├── components/       # Componentes React
    │   ├── services/         # Cliente API
    │   └── types/            # TypeScript types
    └── package.json
```

## Próximas Características

- Soporte para múltiples idiomas
- Procesamiento por lotes
- Historial de videos procesados
- Exportar transcripción en formato SRT
- Integración directa con YouTube API