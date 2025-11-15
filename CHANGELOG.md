# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [2.0] - 2025-11-15

### 🔧 Corregido
- **Extracción de tokens PPFT**: Implementados múltiples métodos de búsqueda con regex mejorados
- **Error "No se pudieron extraer tokens"**: Solucionado con mejor parsing de la página de login
- **Manejo de sesiones**: Cada cuenta ahora usa una sesión limpia
- **Headers HTTP**: Actualizados para simular mejor un navegador real

### ✨ Mejorado
- **Anti-detección**: Añadidos delays aleatorios entre peticiones (1-3 segundos)
- **Flujo de login**: Método más directo usando login.live.com
- **Detección de cuentas válidas**: Verifica múltiples cookies (MSAAUTH, MSPAuth, WLSSC)
- **Detección de redirecciones**: Identifica login exitoso por URL de Outlook
- **Manejo de errores**: Mensajes de error más descriptivos y cortos

### ➕ Añadido
- **Estado CUSTOM**: Detecta cuentas que requieren verificación adicional
- **Archivo custom.txt**: Guarda cuentas que necesitan verificación
- **Mejor parsing de combos**: Ignora líneas vacías y comentarios (#)
- **Validación de datos**: Verifica que email y password no estén vacíos

### 📊 Estadísticas
- Nueva categoría: "Requieren verificación"
- Contador de cuentas CUSTOM añadido

## [1.0] - 2025-11-15

### 🎉 Lanzamiento Inicial
- Verificación de cuentas Hotmail/Outlook
- Búsqueda de palabras clave en inbox (inboxer)
- Interfaz colorida en terminal
- Compatible con Termux
- Basado en script .opk de @PROO_IS_BACK
- Usa las mismas APIs de Microsoft que el original
- Resultados guardados en valid.txt y hits.txt
