from flask import Flask, render_template, request, jsonify, send_file
import os
import subprocess
import json
from pathlib import Path
import re
import unicodedata
import uuid

app = Flask(__name__)

# Directorio para guardar las descargas
DOWNLOAD_FOLDER = Path('descargas')
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

def detect_platform(url):
    """Detecta si la URL es de YouTube, TikTok u otra plataforma"""
    if 'youtube.com' in url or 'youtu.be' in url:
        return 'youtube'
    elif 'tiktok.com' in url:
        return 'tiktok'
    else:
        return 'other'

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
        
        platform = detect_platform(url)
        
        # Obtener información del video usando yt-dlp
        # Para TikTok, agregamos cookies y user-agent
        cmd = ['yt-dlp', '--dump-json', '--no-playlist']
        
        if platform == 'tiktok':
            # TikTok necesita headers adicionales
            cmd.extend([
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '--referer', 'https://www.tiktok.com/'
            ])
        
        cmd.append(url)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return jsonify({'error': 'No se pudo obtener información del video'}), 400
        
        video_info = json.loads(result.stdout)
        
        return jsonify({
            'title': video_info.get('title', 'Sin título'),
            'duration': video_info.get('duration', 0),
            'thumbnail': video_info.get('thumbnail', ''),
            'uploader': video_info.get('uploader', 'Desconocido'),
            'platform': platform
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Tiempo de espera agotado'}), 408
    except json.JSONDecodeError:
        return jsonify({'error': 'Error al procesar la información del video'}), 400
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
        
        platform = detect_platform(url)
        
        # Generar nombre único con UUID
        unique_id = str(uuid.uuid4())[:8]  # Usar solo los primeros 8 caracteres
        
        # Configurar nombre de archivo con UUID
        if format_type == 'audio':
            output_filename = f"{unique_id}.mp3"
        else:
            output_filename = f"{unique_id}.mp4"
        
        output_path = str(DOWNLOAD_FOLDER / output_filename)
        
        # Configurar opciones base
        base_cmd = ['yt-dlp', '-o', output_path, '--no-playlist']
        
        # Agregar headers para TikTok
        if platform == 'tiktok':
            base_cmd.extend([
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '--referer', 'https://www.tiktok.com/'
            ])
        
        # Configurar opciones de descarga según el formato
        if format_type == 'audio':
            # Descargar solo audio en formato MP3
            cmd = base_cmd + [
                '-x',  # Extraer audio
                '--audio-format', 'mp3',  # Convertir a MP3
                '--audio-quality', '0',  # Mejor calidad
                url
            ]
        else:
            # Descargar video con audio
            if platform == 'tiktok':
                # TikTok usa formato específico
                cmd = base_cmd + [
                    '-f', 'best',  # Mejor calidad disponible
                    '--merge-output-format', 'mp4',
                    url
                ]
            else:
                # YouTube y otros
                cmd = base_cmd + [
                    '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    '--merge-output-format', 'mp4',
                    url
                ]
        
        # Ejecutar descarga
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return jsonify({'error': f'Error en la descarga: {result.stderr}'}), 400
        
        # Verificar que el archivo existe
        file_path = DOWNLOAD_FOLDER / output_filename
        if not file_path.exists():
            return jsonify({'error': 'No se encontró el archivo descargado'}), 404
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'message': f'Descarga completada',
            'platform': platform
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
            return jsonify({'error': f'Archivo no encontrado: {filename}'}), 404
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
    print("✅ Compatible con YouTube y TikTok")
    app.run(debug=True, host='0.0.0.0', port=5000)