@echo off
echo ========================================
echo  Instalador de Descargador de YouTube
echo ========================================
echo.

echo [1/3] Instalando dependencias de Python...
pip install -r requirements.txt

echo.
echo [2/3] Verificando yt-dlp...
yt-dlp --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: yt-dlp no esta instalado correctamente
    echo Por favor instala yt-dlp manualmente
    pause
    exit /b 1
)

echo.
echo [3/3] Verificando FFmpeg...
ffmpeg -version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ADVERTENCIA: FFmpeg no esta instalado
    echo La conversion de audio a MP3 no funcionara sin FFmpeg
    echo Por favor instala FFmpeg desde: https://www.gyan.dev/ffmpeg/builds/
    echo.
)

echo.
echo ========================================
echo  Instalacion completada!
echo ========================================
echo.
echo Para iniciar la aplicacion, ejecuta: python app.py
echo.
pause
