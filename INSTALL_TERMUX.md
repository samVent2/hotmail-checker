# 📱 Guía de Instalación en Termux

Esta es una guía paso a paso para instalar y usar el **Hotmail Checker** en Termux (Android).

## 🔧 Instalación Rápida

Copia y pega estos comandos uno por uno en Termux:

### Paso 1: Actualizar Termux
```bash
pkg update && pkg upgrade -y
```

### Paso 2: Instalar Python y Git
```bash
pkg install python git -y
```

### Paso 3: Clonar el repositorio
```bash
git clone https://github.com/samVent2/hotmail-checker.git
```

### Paso 4: Entrar al directorio
```bash
cd hotmail-checker
```

### Paso 5: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 6: Dar permisos de ejecución
```bash
chmod +x hotmail_checker.py
```

## 🚀 Uso

### 1. Crear archivo de combos
Crea un archivo llamado `combos.txt` con tus cuentas:

```bash
nano combos.txt
```

Escribe tus combos en formato `email:password` (uno por línea):
```
cuenta1@hotmail.com:password123
cuenta2@outlook.com:pass456
cuenta3@live.com:mipass789
```

Guarda el archivo:
- Presiona `Ctrl + X`
- Presiona `Y`
- Presiona `Enter`

### 2. Ejecutar el checker
```bash
python hotmail_checker.py
```

### 3. Seguir las instrucciones
1. Ingresa el nombre del archivo de combos: `combos.txt`
2. Opcionalmente, ingresa una palabra clave para buscar en el inbox (ej: `paypal`, `steam`, `epic games`)
3. Espera los resultados

## 📊 Resultados

Los resultados se guardan automáticamente en:
- **valid.txt**: Cuentas válidas
- **hits.txt**: Cuentas con la palabra clave encontrada

Para ver los resultados:
```bash
cat valid.txt
cat hits.txt
```

## 💡 Consejos

### Usar un editor más fácil
Si `nano` es complicado, puedes crear el archivo desde tu gestor de archivos de Android:

1. Abre tu gestor de archivos
2. Ve a: `Almacenamiento interno/Android/data/com.termux/files/home/hotmail-checker/`
3. Crea un archivo llamado `combos.txt`
4. Edítalo con cualquier editor de texto

### Copiar archivo desde tu teléfono
Si ya tienes un archivo de combos en tu teléfono:

```bash
# Dar permisos de almacenamiento a Termux
termux-setup-storage

# Copiar archivo desde Descargas
cp ~/storage/downloads/combos.txt ~/hotmail-checker/combos.txt
```

### Ver resultados en tiempo real
Para ver los archivos de resultados mientras se ejecuta:

```bash
# En otra sesión de Termux
cd hotmail-checker
tail -f valid.txt
```

## 🐛 Solución de Problemas

### Error: "No module named 'requests'"
```bash
pip install requests colorama --upgrade
```

### Error: "Permission denied"
```bash
chmod +x hotmail_checker.py
```

### El script se cierra solo
- Verifica que el archivo `combos.txt` existe
- Verifica que el formato sea correcto (email:password)
- Verifica tu conexión a Internet

### Problemas de conexión
- Asegúrate de tener Internet activo
- Intenta con WiFi en lugar de datos móviles
- Algunos ISPs pueden bloquear ciertas conexiones

## 🔄 Actualizar la herramienta

Para obtener la última versión:

```bash
cd hotmail-checker
git pull
pip install -r requirements.txt --upgrade
```

## 📱 Comandos Útiles en Termux

```bash
# Ver archivos en el directorio actual
ls -la

# Ver contenido de un archivo
cat archivo.txt

# Editar un archivo
nano archivo.txt

# Limpiar la pantalla
clear

# Salir de Termux
exit
```

## ⚡ Script de Instalación Automática

Puedes usar este comando único para instalar todo:

```bash
pkg update -y && pkg install python git -y && git clone https://github.com/samVent2/hotmail-checker.git && cd hotmail-checker && pip install -r requirements.txt && chmod +x hotmail_checker.py && echo "✅ Instalación completada! Ejecuta: python hotmail_checker.py"
```

## 📞 Soporte

Si tienes problemas, abre un issue en: https://github.com/samVent2/hotmail-checker/issues

---

**¡Listo!** Ahora puedes verificar cuentas de Hotmail directamente desde tu teléfono Android con Termux.
