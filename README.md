# 🔐 Hotmail Checker & Inbox Scanner

Herramienta para verificar cuentas de Hotmail/Outlook y buscar palabras clave en los correos. Basada en el script original de **@PROO_IS_BACK**.

## ✨ Características

- ✅ Verificación rápida de cuentas Hotmail/Outlook
- 🔍 Búsqueda de palabras clave en el inbox
- 📊 Resultados organizados (válidas, hits, inválidas)
- 🎨 Interfaz colorida en terminal
- 🚀 Sin necesidad de proxies
- 📱 Compatible con Termux (Android)

## 📋 Requisitos

- Python 3.7 o superior
- Conexión a Internet

## 🔧 Instalación en Termux

### 1. Instalar Termux
Descarga Termux desde [F-Droid](https://f-droid.org/packages/com.termux/) o Google Play Store.

### 2. Actualizar paquetes
```bash
pkg update && pkg upgrade -y
```

### 3. Instalar Python y Git
```bash
pkg install python git -y
```

### 4. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/hotmail-checker.git
cd hotmail-checker
```

### 5. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 🚀 Uso

### 1. Preparar archivo de combos
Crea un archivo de texto (por ejemplo `combos.txt`) con el formato:
```
email@hotmail.com:password123
otro@outlook.com:pass456
cuenta@live.com:mipassword
```

### 2. Ejecutar el checker
```bash
python hotmail_checker.py
```

### 3. Seguir las instrucciones
- Ingresa el nombre del archivo de combos
- Opcionalmente, ingresa una palabra clave para buscar en el inbox
- Espera los resultados

## 📁 Archivos de salida

- **valid.txt**: Cuentas válidas encontradas
- **hits.txt**: Cuentas que contienen la palabra clave buscada

## 📝 Ejemplo de uso

```bash
$ python hotmail_checker.py

╔═══════════════════════════════════════════════════════╗
║         HOTMAIL CHECKER & INBOX SCANNER               ║
║              Basado en script de @PROO_IS_BACK        ║
╚═══════════════════════════════════════════════════════╝

[?] Ingresa el nombre del archivo de combos (ej: combos.txt): combos.txt
[?] Ingresa palabra clave para buscar en inbox (Enter para omitir): paypal

[INFO] Cargados 100 combos
[INFO] Iniciando verificación...

[1/100] Verificando: test@hotmail.com ✓ VÁLIDA
[2/100] Verificando: user@outlook.com ★ HIT! (5 resultados)
[3/100] Verificando: fake@live.com ✗ INVÁLIDA
...
```

## ⚙️ Funcionamiento

La herramienta replica exactamente la lógica del archivo .opk original:

1. **Verificación de cuenta**: Utiliza las APIs oficiales de Microsoft para verificar si la cuenta existe
2. **Autenticación**: Realiza el login usando el flujo OAuth de Microsoft
3. **Búsqueda en inbox**: Si se proporciona una palabra clave, busca en el correo usando la API de búsqueda de Outlook

## 🔒 Seguridad

- No almacena credenciales en servidores externos
- Todo el procesamiento es local
- Usa las APIs oficiales de Microsoft
- No requiere proxies

## ⚠️ Advertencias

- Esta herramienta es solo para fines educativos y de prueba
- No uses esta herramienta para acceder a cuentas sin autorización
- El uso indebido puede violar los términos de servicio de Microsoft
- El autor no se hace responsable del mal uso de esta herramienta

## 🐛 Solución de problemas

### Error: "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### Error: "Permission denied"
```bash
chmod +x hotmail_checker.py
```

### Problemas de conexión
- Verifica tu conexión a Internet
- Algunos ISPs pueden bloquear ciertos endpoints
- Intenta usar una red diferente

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👤 Créditos

- Script original: **@PROO_IS_BACK**
- Adaptación a Python: Comunidad

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Soporte

Si tienes problemas o preguntas, abre un issue en GitHub.

---

**Nota**: Esta herramienta replica la funcionalidad del archivo .opk original sin modificaciones en la lógica de verificación. Usa las mismas APIs y endpoints de Microsoft.
