from flask import Flask, render_template, request, jsonify, send_file
import os
import subprocess
import json
from pathlib import Path
import re
import unicodedata
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configuración de Rate Limiting
def get_user_identifier():
    # Prioridad: Email de Cloudflare Access > IP de Cloudflare > IP remota
    return request.headers.get('Cf-Access-Authenticated-User-Email') or \
           request.headers.get('CF-Connecting-IP') or \
           get_remote_address()

limiter = Limiter(
    key_func=get_user_identifier,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

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
    user_email = request.headers.get('Cf-Access-Authenticated-User-Email', 'Invitado')
    return render_template('index.html', user_email=user_email)

@app.route('/get_info', methods=['POST'])
@limiter.limit("10 per minute")
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
        
        # Obtener formatos disponibles
        formats = video_info.get('formats', [])
        available_qualities = set()
        
        for fmt in formats:
            height = fmt.get('height')
            if height:
                if height >= 2160:
                    available_qualities.add('4k')
                elif height >= 1440:
                    available_qualities.add('2k')
                elif height >= 1080:
                    available_qualities.add('1080p')
                elif height >= 720:
                    available_qualities.add('720p')
                elif height >= 480:
                    available_qualities.add('480p')
                else:
                    available_qualities.add('360p')
        
        # Mapear a nuestras categorías de calidad
        quality_mapping = {
            'best': False,
            'high': False,
            'medium': False,
            'low': False
        }
        
        if '4k' in available_qualities or '2k' in available_qualities or '1080p' in available_qualities:
            quality_mapping['best'] = True
        if '1080p' in available_qualities:
            quality_mapping['high'] = True
        if '720p' in available_qualities:
            quality_mapping['medium'] = True
        if '480p' in available_qualities or '360p' in available_qualities:
            quality_mapping['low'] = True
        
        # Si no hay calidades específicas, habilitar todas (para audio o videos sin info)
        if not any(quality_mapping.values()):
            quality_mapping = {k: True for k in quality_mapping}
        
        return jsonify({
            'title': video_info.get('title', 'Sin título'),
            'duration': video_info.get('duration', 0),
            'thumbnail': video_info.get('thumbnail', ''),
            'uploader': video_info.get('uploader', 'Desconocido'),
            'platform': platform,
            'available_qualities': quality_mapping,
            'max_resolution': max(available_qualities) if available_qualities else 'desconocida'
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Tiempo de espera agotado'}), 408
    except json.JSONDecodeError:
        return jsonify({'error': 'Error al procesar la información del video'}), 400
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/download', methods=['POST'])
@limiter.limit("5 per minute")
def download():
    """Descarga el video o audio según la opción seleccionada"""
    try:
        data = request.get_json()
        url = data.get('url')
        format_type = data.get('format', 'video')  # 'video' o 'audio'
        quality = data.get('quality', 'best')  # 'best', 'high', 'medium', 'low'
        
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
            # Calidad de audio: 0 = mejor, 9 = peor
            audio_quality_map = {
                'best': '0',
                'high': '2',
                'medium': '5',
                'low': '9'
            }
            audio_quality = audio_quality_map.get(quality, '0')
            
            cmd = base_cmd + [
                '-x',  # Extraer audio
                '--audio-format', 'mp3',  # Convertir a MP3
                '--audio-quality', audio_quality,
                url
            ]
        else:
            # Descargar video con audio
            if platform == 'tiktok':
                # TikTok - usar formato específico
                cmd = base_cmd + [
                    '-f', 'best',
                    '--merge-output-format', 'mp4',
                    url
                ]
            else:
                # YouTube y otras plataformas
                # Definir formatos según calidad
                quality_formats = {
                    'best': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'high': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
                    'medium': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
                    'low': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
                }
                video_format = quality_formats.get(quality, quality_formats['best'])
                
                cmd = base_cmd + [
                    '-f', video_format,
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
            'platform': platform,
            'quality': quality
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

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Límite de velocidad excedido",
        "message": "Has realizado demasiadas solicitudes. Por favor, espera un momento.",
        "retry_after": e.description
    }), 429

if __name__ == '__main__':
    print("🚀 Servidor iniciado en http://localhost:5000")
    print("📁 Archivos se guardarán en:", DOWNLOAD_FOLDER.absolute())
    print("✅ Compatible con YouTube y TikTok")
    app.run(debug=True, host='0.0.0.0', port=5000)