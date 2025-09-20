# 🎬 YouTube Video Tools Suite | JavadexAI

[![JavadexAI YouTube](https://img.shields.io/badge/YouTube-JavadexAI-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/@JavadexAI)
[![Únete a la Comunidad](https://img.shields.io/badge/Comunidad-La%20Escuela%20de%20IA-blue?style=for-the-badge)](https://www.skool.com/la-escuela-de-ia-9955)
[![Tutorial Completo](https://img.shields.io/badge/Tutorial-Ver%20Video-green?style=for-the-badge&logo=youtube)](https://www.youtube.com/watch?v=v5Dh_zwxu7E)

> **🤖 Herramientas de IA desarrolladas por [JavadexAI](https://www.youtube.com/@JavadexAI)** - Optimiza tu contenido de YouTube con transcripción automática y sugerencias inteligentes.

---

## 🚀 ¿Qué es esto?

Suite completa de herramientas para **optimizar tu contenido de YouTube** usando Inteligencia Artificial. Transcribe videos, genera títulos optimizados, descripciones SEO y sugerencias de thumbnails - todo automático.

### 📺 **Tutorial Completo**
👉 **[Ver el tutorial paso a paso](https://www.youtube.com/watch?v=v5Dh_zwxu7E)** en el canal de [JavadexAI](https://www.youtube.com/@JavadexAI)

### 🎓 **Únete a la Comunidad**
🔥 **[La Escuela de IA](https://www.skool.com/la-escuela-de-ia-9955)** - Aprende IA práctica con proyectos reales

---

## ✨ Características Principales

### 🎯 **Transcripción Inteligente**
- **Local Whisper** + **Gemini AI** para máxima precisión
- Timestamps automáticos cada 15-30 segundos
- Soporte para videos largos (30+ minutos)
- Sin límites de cache - cada video se procesa individualmente

### 📝 **Optimización de Contenido**
- **Títulos atractivos** (máx. 60 caracteres)
- **Descripciones SEO** optimizadas (150-200 palabras)
- **Prompts para thumbnails** detallados
- **15-30 capítulos/highlights** para videos largos

### 🔄 **Regeneración Inteligente**
- **4 opciones de títulos** diferentes
- **Instrucciones personalizadas** para sugerencias
- Transcripción estática - solo regenera sugerencias

### 💾 **Gestión Automática**
- **Guardado automático** de todos los análisis
- Archivos JSON con timestamp
- Historial completo de procesamiento

---

## 🛠️ Instalación Rápida

### **Requisitos**
- Python 3.8+
- Node.js 18+
- FFmpeg (se instala automáticamente en macOS)
- API Key de Google Gemini

### **1. Clonar y Configurar**

```bash
git clone <tu-repositorio>
cd video-tools
```

### **2. Backend (FastAPI + Python)**

```bash
cd backend
pip install -r requirements.txt

# Crear archivo .env con tu API key
echo "GEMINI_API_KEY=tu_api_key_aqui" > .env
```

### **3. Frontend (React + TypeScript)**

```bash
cd frontend
npm install
```

---

## 🚀 Ejecutar la Aplicación

### **Terminal 1: Backend**
```bash
cd backend
python -m uvicorn app.main:app --reload
```
📍 **Backend**: http://localhost:8000
📚 **API Docs**: http://localhost:8000/docs

### **Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```
📍 **Aplicación**: http://localhost:5173

---

## 📖 Cómo Usar

### **🎬 Paso 1: Subir Video**
1. Abre http://localhost:5173
2. Arrastra tu video o selecciona archivo
3. Formatos: MP4, AVI, MOV, MKV, WebM, MPEG
4. Tamaño máximo: 5 GB

### **⚡ Paso 2: Procesamiento Automático**
- **Whisper Local**: Transcribe el audio completo
- **Gemini AI**: Analiza y genera sugerencias
- **Tiempo**: 1-3 minutos (depende del video)

### **📋 Paso 3: Resultados**
- ✅ **Transcripción completa** con timestamps
- ✅ **Título optimizado** para YouTube
- ✅ **Descripción SEO** lista para copiar
- ✅ **Prompt de thumbnail** detallado
- ✅ **15-30 capítulos** distribuidos por el video

### **🔄 Paso 4: Regenerar (Opcional)**
- Añade **instrucciones personalizadas**
- Genera **4 títulos diferentes**
- La transcripción permanece igual

---

## 🏗️ Arquitectura Técnica

### **Backend Stack**
- **FastAPI**: API REST moderna y rápida
- **OpenAI Whisper**: Transcripción local de alta calidad
- **Google Gemini**: Análisis de contenido y sugerencias
- **Pydantic**: Validación de datos y tipos

### **Frontend Stack**
- **React 18**: Interfaz moderna y reactiva
- **TypeScript**: Tipado fuerte y mejor desarrollo
- **Vite**: Build tool rápido y eficiente
- **Tailwind CSS**: Estilos utilitarios

### **Flujo de Procesamiento**
```
Video Upload → Whisper Transcription → Gemini Analysis → Results
```

---

## 📁 Estructura del Proyecto

```
video-tools/
├── 🔧 backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── whisper_service.py    # Transcripción local
│   │   │   ├── gemini.py            # Análisis IA (2 pasos)
│   │   │   └── suggestions_service.py # Regeneración
│   │   ├── routers/videos.py        # API endpoints
│   │   └── models/video.py          # Modelos de datos
│   └── analysis_results/            # Análisis guardados
├── 🎨 frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoUploader.tsx    # Subida de archivos
│   │   │   ├── TranscriptionViewer.tsx # Mostrar transcripción
│   │   │   └── SuggestionsPanel.tsx # Sugerencias + regenerar
│   │   └── services/api.ts          # Cliente HTTP
└── 📊 analysis_results/             # Historial JSON
```

---

## 🔗 Links y Recursos

### 📺 **Canal JavadexAI**
- **YouTube**: https://www.youtube.com/@JavadexAI
- **Tutorial completo**: https://www.youtube.com/watch?v=v5Dh_zwxu7E
- **Más tutoriales de IA práctica**

### 🎓 **Comunidad**
- **La Escuela de IA**: https://www.skool.com/la-escuela-de-ia-9955
- **Comunidad creciente** de desarrolladores IA
- **Proyectos prácticos** como este
- **Soporte de la comunidad**

### 🛠️ **API y Endpoints**
- `POST /api/videos/process` - Procesar video completo
- `POST /api/videos/regenerate-suggestions` - Regenerar sugerencias
- `GET /api/videos/health` - Estado del servicio

---

## 🆕 Próximas Características

- [ ] **Múltiples idiomas** (inglés, francés, etc.)
- [ ] **Procesamiento por lotes** (múltiples videos)
- [ ] **Exportar SRT** (subtítulos)
- [ ] **Integración YouTube API** (subida directa)
- [ ] **Análisis de tendencias** (palabras clave populares)
- [ ] **Templates personalizados** (estilos de título/descripción)

---

## 🤝 Créditos

**Desarrollado por [JavadexAI](https://www.youtube.com/@JavadexAI)**
🤖 *Con la ayuda de Claude Code para el desarrollo*

### 🙏 **Agradecimientos**
- **OpenAI Whisper** - Transcripción de audio
- **Google Gemini** - Análisis de contenido
- **FastAPI** - Framework backend
- **React** - Framework frontend

---

## 📄 Licencia

Proyecto educativo desarrollado para la comunidad de [La Escuela de IA](https://www.skool.com/la-escuela-de-ia-9955).

**¿Te gustó el proyecto?**
👍 **Like al [video tutorial](https://www.youtube.com/watch?v=v5Dh_zwxu7E)**
🔔 **Suscríbete a [JavadexAI](https://www.youtube.com/@JavadexAI)**
🎓 **Únete a [La Escuela de IA](https://www.skool.com/la-escuela-de-ia-9955)**