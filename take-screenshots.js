const { chromium } = require('playwright');

async function takeScreenshots() {
  console.log('🚀 Starting screenshot capture...');

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();

  try {
    // Screenshot 1: Home page with upload area
    console.log('📸 Taking screenshot 1: Upload interface');
    await page.goto('http://localhost:5173');
    await page.waitForTimeout(3000); // Wait for app to load

    await page.screenshot({
      path: 'screenshots/01-upload-interface.png',
      fullPage: true
    });
    console.log('✅ Screenshot 1 complete');

    // Screenshot 2: Mock results page
    console.log('📸 Taking screenshot 2: Results interface');
    await page.evaluate(() => {
      document.body.innerHTML = `
        <div style="min-height: 100vh; background: #f8fafc; font-family: system-ui, -apple-system, sans-serif;">
          <div style="max-width: 1200px; margin: 0 auto; padding: 2rem;">
            <h1 style="text-align: center; color: #1f2937; margin-bottom: 2rem; font-size: 2rem; font-weight: 700;">
              🎬 Análisis de Video Completado
            </h1>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
              <!-- Transcription -->
              <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h2 style="color: #374151; margin-bottom: 1rem; font-size: 1.25rem; font-weight: 600; display: flex; align-items: center;">
                  📝 Transcripción
                </h2>
                <div style="max-height: 400px; overflow-y: auto; font-size: 0.9rem;">
                  <div style="margin-bottom: 0.75rem; padding: 0.75rem; background: #f9fafb; border-radius: 6px; border-left: 3px solid #3b82f6;">
                    <span style="color: #6b7280; font-weight: 600; font-family: monospace;">00:00</span>
                    <span style="margin-left: 0.5rem; color: #374151;">Buenas a todos, soy Javi, especialista en IA y hoy vamos a crear herramientas para optimizar YouTube con inteligencia artificial.</span>
                  </div>
                  <div style="margin-bottom: 0.75rem; padding: 0.75rem; background: #f9fafb; border-radius: 6px; border-left: 3px solid #3b82f6;">
                    <span style="color: #6b7280; font-weight: 600; font-family: monospace;">00:18</span>
                    <span style="margin-left: 0.5rem; color: #374151;">Vamos a implementar Whisper para transcripción automática y Gemini para generar títulos optimizados.</span>
                  </div>
                  <div style="margin-bottom: 0.75rem; padding: 0.75rem; background: #f9fafb; border-radius: 6px; border-left: 3px solid #3b82f6;">
                    <span style="color: #6b7280; font-weight: 600; font-family: monospace;">00:45</span>
                    <span style="margin-left: 0.5rem; color: #374151;">La transcripción automática es clave para el SEO y nos ayuda a generar contenido optimizado.</span>
                  </div>
                  <div style="margin-bottom: 0.75rem; padding: 0.75rem; background: #f9fafb; border-radius: 6px; border-left: 3px solid #3b82f6;">
                    <span style="color: #6b7280; font-weight: 600; font-family: monospace;">02:30</span>
                    <span style="margin-left: 0.5rem; color: #374151;">Configuramos el entorno con FastAPI para el backend y React para el frontend.</span>
                  </div>
                  <div style="margin-bottom: 0.75rem; padding: 0.75rem; background: #f9fafb; border-radius: 6px; border-left: 3px solid #3b82f6;">
                    <span style="color: #6b7280; font-weight: 600; font-family: monospace;">05:20</span>
                    <span style="margin-left: 0.5rem; color: #374151;">El sistema procesa videos largos de 30+ minutos con alta precisión usando el modelo small de Whisper.</span>
                  </div>
                </div>
              </div>

              <!-- Suggestions -->
              <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h2 style="color: #374151; margin-bottom: 1rem; font-size: 1.25rem; font-weight: 600;">💡 Sugerencias para YouTube</h2>

                <div style="margin-bottom: 1.5rem;">
                  <h3 style="color: #4b5563; margin-bottom: 0.5rem; font-weight: 600;">🎯 Título</h3>
                  <div style="background: #eff6ff; padding: 0.75rem; border-radius: 6px; border-left: 4px solid #3b82f6; font-weight: 500;">
                    Cómo crear herramientas de IA para YouTube | Tutorial completo
                  </div>
                </div>

                <div style="margin-bottom: 1.5rem;">
                  <h3 style="color: #4b5563; margin-bottom: 0.5rem; font-weight: 600;">📄 Descripción</h3>
                  <div style="background: #f0fdf4; padding: 0.75rem; border-radius: 6px; border-left: 4px solid #10b981; font-size: 0.9rem; line-height: 1.5;">
                    Aprende a crear herramientas de IA para optimizar tu contenido de YouTube. Implementamos Whisper para transcripción automática y Gemini para generar títulos, descripciones y capítulos. Tutorial paso a paso con FastAPI y React.
                  </div>
                </div>

                <div style="margin-bottom: 1.5rem;">
                  <h3 style="color: #4b5563; margin-bottom: 0.5rem; font-weight: 600;">🖼️ Thumbnail</h3>
                  <div style="background: #fef3c7; padding: 0.75rem; border-radius: 6px; border-left: 4px solid #f59e0b; font-size: 0.9rem; line-height: 1.5;">
                    Imagen con Javi programando, código de IA en pantalla, logo de YouTube visible, colores azul y naranja, texto "IA + YouTube" destacado.
                  </div>
                </div>

                <div>
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <h3 style="color: #4b5563; font-weight: 600;">⭐ Capítulos / Momentos Destacados</h3>
                    <button style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border: none; border-radius: 6px; font-size: 0.9rem; font-weight: 500; cursor: pointer;">
                      🔄 Regenerar (4 títulos)
                    </button>
                  </div>
                  <div style="background: #f8fafc; padding: 1rem; border-radius: 6px; font-size: 0.9rem; line-height: 1.6;">
                    <div style="margin-bottom: 0.5rem; padding: 0.25rem 0; border-bottom: 1px solid #e2e8f0;">
                      <span style="color: #6366f1; font-weight: 600;">00:18</span> - Introducción a las herramientas de IA para YouTube
                    </div>
                    <div style="margin-bottom: 0.5rem; padding: 0.25rem 0; border-bottom: 1px solid #e2e8f0;">
                      <span style="color: #6366f1; font-weight: 600;">02:30</span> - Configuración del entorno de desarrollo (FastAPI + React)
                    </div>
                    <div style="margin-bottom: 0.5rem; padding: 0.25rem 0; border-bottom: 1px solid #e2e8f0;">
                      <span style="color: #6366f1; font-weight: 600;">05:45</span> - Implementación de Whisper para transcripción local
                    </div>
                    <div style="margin-bottom: 0.5rem; padding: 0.25rem 0; border-bottom: 1px solid #e2e8f0;">
                      <span style="color: #6366f1; font-weight: 600;">08:15</span> - Integración con Gemini AI para análisis de contenido
                    </div>
                    <div style="margin-bottom: 0.5rem; padding: 0.25rem 0; border-bottom: 1px solid #e2e8f0;">
                      <span style="color: #6366f1; font-weight: 600;">12:00</span> - Optimización para videos largos (30+ minutos)
                    </div>
                    <div style="margin-bottom: 0.5rem; padding: 0.25rem 0; border-bottom: 1px solid #e2e8f0;">
                      <span style="color: #6366f1; font-weight: 600;">15:30</span> - Sistema de guardado automático de análisis
                    </div>
                    <div style="margin-bottom: 0.5rem; padding: 0.25rem 0;">
                      <span style="color: #6366f1; font-weight: 600;">18:45</span> - Demo completa y próximos pasos
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div style="text-align: center; margin-top: 2rem; padding: 1.5rem; background: white; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
              <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 1rem;">
                🤖 Generado con IA by <strong>JavadexAI</strong> |
                <a href="https://www.youtube.com/@JavadexAI" style="color: #3b82f6; text-decoration: none;">YouTube</a> |
                <a href="https://www.skool.com/la-escuela-de-ia-9955" style="color: #3b82f6; text-decoration: none;">La Escuela de IA</a>
              </p>
            </div>
          </div>
        </div>
      `;
    });

    await page.screenshot({
      path: 'screenshots/02-results-interface.png',
      fullPage: true
    });
    console.log('✅ Screenshot 2 complete');

    // Screenshot 3: Regeneration modal
    console.log('📸 Taking screenshot 3: Regeneration modal');
    await page.evaluate(() => {
      // Add regeneration modal
      const modal = document.createElement('div');
      modal.innerHTML = `
        <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; backdrop-filter: blur(4px);">
          <div style="background: white; border-radius: 16px; padding: 2rem; max-width: 600px; width: 90%; box-shadow: 0 25px 50px rgba(0,0,0,0.25); transform: translateY(0); animation: slideIn 0.3s ease-out;">
            <h2 style="color: #1f2937; margin-bottom: 1.5rem; text-align: center; font-size: 1.5rem; font-weight: 700;">🔄 Regenerar Sugerencias</h2>

            <div style="margin-bottom: 1.5rem;">
              <label style="display: block; color: #374151; margin-bottom: 0.5rem; font-weight: 600;">
                💬 Instrucciones personalizadas
              </label>
              <textarea style="width: 100%; padding: 0.75rem; border: 2px solid #d1d5db; border-radius: 8px; font-size: 0.9rem; min-height: 100px; font-family: system-ui; resize: vertical; focus: outline-none; focus: border-color: #3b82f6;" placeholder="Ej: Enfócate en principiantes, usa un tono casual, incluye más emojis...">Enfócate en desarrolladores que quieren aprender IA práctica. Usa un tono técnico pero accesible. Incluye emojis y hazlo atractivo para YouTube.</textarea>
            </div>

            <div style="background: #f8fafc; padding: 1.25rem; border-radius: 10px; margin-bottom: 1.5rem; border: 1px solid #e2e8f0;">
              <h3 style="color: #374151; margin-bottom: 0.75rem; font-size: 1rem; font-weight: 600;">🎯 Se generarán 4 opciones de títulos:</h3>
              <div style="font-size: 0.85rem; line-height: 1.6; color: #6b7280;">
                <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: white; border-radius: 4px; border-left: 3px solid #3b82f6;">
                  1. Crea herramientas de IA para YouTube (Tutorial paso a paso)
                </div>
                <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: white; border-radius: 4px; border-left: 3px solid #10b981;">
                  2. De cero a experto: Automatiza tu canal con IA | Whisper + Gemini
                </div>
                <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: white; border-radius: 4px; border-left: 3px solid #f59e0b;">
                  3. Tutorial completo: Herramientas de IA para creators 🚀
                </div>
                <div style="margin-bottom: 0.5rem; padding: 0.5rem; background: white; border-radius: 4px; border-left: 3px solid #ef4444;">
                  4. Programando el futuro: IA para optimizar YouTube ⚡
                </div>
              </div>
            </div>

            <div style="display: flex; gap: 1rem; justify-content: end;">
              <button style="padding: 0.75rem 1.5rem; border: 2px solid #d1d5db; background: white; border-radius: 8px; color: #374151; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                Cancelar
              </button>
              <button style="padding: 0.75rem 1.5rem; background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);">
                ✨ Regenerar Sugerencias
              </button>
            </div>
          </div>
        </div>
      `;
      document.body.appendChild(modal);
    });

    await page.screenshot({
      path: 'screenshots/03-regeneration-modal.png',
      fullPage: true
    });
    console.log('✅ Screenshot 3 complete');

    console.log('✅ All screenshots captured successfully!');
    console.log('📁 Screenshots saved in: screenshots/');

  } catch (error) {
    console.error('❌ Error taking screenshots:', error);
  } finally {
    await browser.close();
  }
}

takeScreenshots();