# 🎬 Descargador de Videos de YouTube

Una aplicación web simple y moderna para descargar videos de YouTube en formato MP4 o extraer solo el audio en MP3.

## 📋 Características

- ✅ Interfaz web moderna y fácil de usar
- 🎥 Descarga videos en formato MP4
- 🎵 Extrae audio en formato MP3
- 📊 Previsualización de información del video
- ⚡ Rápido y eficiente
- 📱 Diseño responsivo

## 🔧 Requisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

## 📦 Instalación

### Paso 1: Instalar yt-dlp

yt-dlp es la herramienta que se encarga de descargar los videos. Hay varias formas de instalarlo:

**Opción A - Con pip (Recomendado):**
```bash
pip install yt-dlp
```

**Opción B - En Linux/Mac con curl:**
```bash
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp
```

**Opción C - En Windows:**
Descarga el ejecutable desde: https://github.com/yt-dlp/yt-dlp/releases
Y agrégalo a tu PATH.

### Paso 2: Instalar FFmpeg

FFmpeg es necesario para convertir audio a MP3 y procesar videos.

**En Windows:**
1. Descarga desde: https://www.gyan.dev/ffmpeg/builds/
2. Extrae el archivo
3. Agrega la carpeta `bin` al PATH de Windows

**En Mac:**
```bash
brew install ffmpeg
```

**En Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**En Linux (Fedora):**
```bash
sudo dnf install ffmpeg
```

### Paso 3: Instalar Flask

```bash
pip install flask
```

## 🚀 Uso

1. Navega al directorio del proyecto:
```bash
cd ruta/del/proyecto
```

2. Ejecuta la aplicación:
```bash
python app.py
```

3. Abre tu navegador y ve a:
```
http://localhost:5000
```

4. Ingresa la URL del video de YouTube que deseas descargar

5. Selecciona el formato (Video MP4 o Audio MP3)

6. Haz clic en "Descargar"

7. El archivo se descargará en la carpeta `descargas/`

## 📁 Estructura del Proyecto

```
proyecto/
│
├── app.py                 # Servidor Flask principal
├── templates/
│   └── index.html        # Interfaz web
├── descargas/            # Carpeta donde se guardan los archivos
└── README.md             # Este archivo
```

## 🎯 Funcionalidades

### Ver Información del Video
Antes de descargar, puedes ver:
- Título del video
- Miniatura
- Canal/Uploader
- Duración

### Opciones de Descarga

**Video (MP4):**
- Descarga el video con la mejor calidad disponible
- Combina video y audio automáticamente
- Formato compatible con todos los reproductores

**Audio (MP3):**
- Extrae solo el audio del video
- Convierte automáticamente a MP3
- Calidad óptima de audio

## ⚙️ Configuración Avanzada

### Cambiar la Calidad del Video

Edita `app.py` y modifica la línea de formato en la función `download()`:

```python
# Para máxima calidad:
'-f', 'bestvideo+bestaudio/best',

# Para 720p:
'-f', 'bestvideo[height<=720]+bestaudio/best[height<=720]',

# Para 480p:
'-f', 'bestvideo[height<=480]+bestaudio/best[height<=480]',
```

### Cambiar la Calidad del Audio

Modifica el valor de `--audio-quality`:

```python
'--audio-quality', '0',  # Mejor calidad (más pesado)
'--audio-quality', '5',  # Calidad media
'--audio-quality', '9',  # Menor calidad (más liviano)
```

## 🐛 Solución de Problemas

### Error: "yt-dlp no encontrado"
- Asegúrate de haber instalado yt-dlp correctamente
- En Windows, verifica que esté en el PATH
- Intenta ejecutar `yt-dlp --version` en la terminal

### Error: "ffmpeg no encontrado"
- Instala FFmpeg siguiendo las instrucciones de instalación
- En Windows, verifica que esté en el PATH
- Intenta ejecutar `ffmpeg -version` en la terminal

### Error: "No se pudo descargar el video"
- Verifica que la URL sea válida
- Algunos videos pueden estar restringidos por región
- Videos privados o eliminados no se pueden descargar

### El video tarda mucho en descargar
- Es normal para videos largos o de alta calidad
- Depende de tu velocidad de internet
- Puedes reducir la calidad en la configuración

## ⚖️ Consideraciones Legales

- Solo descarga contenido que tengas derecho a descargar
- Respeta los derechos de autor
- Esta herramienta es solo para uso personal y educativo
- No redistribuyas contenido protegido por derechos de autor

## 🔄 Actualizaciones

Para mantener yt-dlp actualizado:
```bash
pip install --upgrade yt-dlp
```

## 🤝 Contribuciones

Las mejoras y sugerencias son bienvenidas. Algunas ideas para mejorar:
- Agregar más formatos de salida
- Implementar cola de descargas
- Agregar historial de descargas
- Soporte para listas de reproducción
- Selección de calidad personalizada

## 📝 Notas Adicionales

- Los archivos se guardan en la carpeta `descargas/`
- Puedes limpiar los archivos descargados desde la interfaz
- La aplicación funciona con videos públicos de YouTube
- Algunos videos muy largos pueden tardar varios minutos

## 💡 Tips

1. **URLs válidas**: Asegúrate de copiar la URL completa del video
2. **Espacio en disco**: Verifica tener suficiente espacio antes de descargar
3. **Internet**: Una conexión estable mejora la velocidad de descarga
4. **Formatos**: MP4 para video, MP3 para audio
5. **Calidad**: La calidad máxima puede generar archivos muy grandes

---

**¡Disfruta descargando tus videos favoritos! 🎉**
