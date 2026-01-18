from flask import Flask, render_template, request, jsonify, send_file
import os
import subprocess
import json
from pathlib import Path

app = Flask(__name__)

# Directorio para guardar las descargas
DOWNLOAD_FOLDER = Path('descargas')
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

@app.route('/')
def index():
    """Renderiza la página principal"""
    return render_template('index.html')

@app.route('/get_info', methods=['POST'])
def get_info():
    """Obtiene información del video sin descargarlo"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL no proporcionada'}), 400
        
        # Obtener información del video usando yt-dlp
        cmd = ['yt-dlp', '--dump-json', '--no-playlist', url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return jsonify({'error': 'No se pudo obtener información del video'}), 400
        
        video_info = json.loads(result.stdout)
        
        return jsonify({
            'title': video_info.get('title', 'Sin título'),
            'duration': video_info.get('duration', 0),
            'thumbnail': video_info.get('thumbnail', ''),
            'uploader': video_info.get('uploader', 'Desconocido')
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Tiempo de espera agotado'}), 408
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/download', methods=['POST'])
def download():
    """Descarga el video o audio según la opción seleccionada"""
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format', 'video')  # 'video' o 'audio'
        
        if not url:
            return jsonify({'error': 'URL no proporcionada'}), 400
        
        # Configurar opciones de descarga
        if format_type == 'audio':
            # Descargar solo audio en formato MP3
            output_template = str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s')
            cmd = [
                'yt-dlp',
                '-x',  # Extraer audio
                '--audio-format', 'mp3',  # Convertir a MP3
                '--audio-quality', '0',  # Mejor calidad
                '-o', output_template,
                '--no-playlist',
                url
            ]
        else:
            # Descargar video con audio
            output_template = str(DOWNLOAD_FOLDER / '%(title)s.%(ext)s')
            cmd = [
                'yt-dlp',
                '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                '--merge-output-format', 'mp4',
                '-o', output_template,
                '--no-playlist',
                url
            ]
        
        # Ejecutar descarga
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return jsonify({'error': f'Error en la descarga: {result.stderr}'}), 400
        
        # Buscar el archivo descargado
        files = list(DOWNLOAD_FOLDER.glob('*'))
        if not files:
            return jsonify({'error': 'No se encontró el archivo descargado'}), 404
        
        # Obtener el archivo más reciente
        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        
        return jsonify({
            'success': True,
            'filename': latest_file.name,
            'message': f'Descarga completada: {latest_file.name}'
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Tiempo de espera agotado. El archivo puede ser muy grande.'}), 408
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/download_file/<filename>')
def download_file(filename):
    """Envía el archivo descargado al usuario"""
    try:
        file_path = DOWNLOAD_FOLDER / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Limpia los archivos descargados"""
    try:
        for file in DOWNLOAD_FOLDER.glob('*'):
            file.unlink()
        return jsonify({'success': True, 'message': 'Archivos eliminados'})
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Servidor iniciado en http://localhost:5000")
    print("📁 Archivos se guardarán en:", DOWNLOAD_FOLDER.absolute())
    app.run(debug=True, host='0.0.0.0', port=5000)
