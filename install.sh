#!/bin/bash

echo "========================================"
echo " Instalador de Descargador de YouTube"
echo "========================================"
echo ""

echo "[1/3] Instalando dependencias de Python..."
pip install -r requirements.txt

echo ""
echo "[2/3] Verificando yt-dlp..."
if command -v yt-dlp &> /dev/null; then
    yt-dlp --version
else
    echo "ERROR: yt-dlp no está instalado correctamente"
    echo "Por favor instala yt-dlp manualmente con: pip install yt-dlp"
    exit 1
fi

echo ""
echo "[3/3] Verificando FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg -version | head -n 1
else
    echo "ADVERTENCIA: FFmpeg no está instalado"
    echo "La conversión de audio a MP3 no funcionará sin FFmpeg"
    echo ""
    echo "Para instalar FFmpeg:"
    echo "  - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  - Mac: brew install ffmpeg"
    echo "  - Fedora: sudo dnf install ffmpeg"
    echo ""
fi

echo ""
echo "========================================"
echo " Instalación completada!"
echo "========================================"
echo ""
echo "Para iniciar la aplicación, ejecuta: python app.py"
echo ""
