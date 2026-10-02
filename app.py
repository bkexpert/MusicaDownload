import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MAX_BYTES = 500 * 1024 * 1024
TIMEOUT = 30
ALLOWED_FORMATS = {"mp3", "mp4"}

def safe_name(value: str) -> str:
    value = unquote(value or "arquivo")
    value = Path(value).name
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value)
    return value[:120] or "arquivo"

def validate_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("A URL deve começar com http:// ou https://.")
    return value

def inspect_url(url: str):
    response = requests.head(url, allow_redirects=True, timeout=TIMEOUT, stream=True)
    response.raise_for_status()
    size = int(response.headers.get("Content-Length", "0") or 0)
    if size and size > MAX_BYTES:
        raise ValueError("O arquivo excede o limite de 500 MB.")
    content_type = response.headers.get("Content-Type", "")
    filename = safe_name(Path(urlparse(response.url).path).name or "arquivo")
    return filename, content_type, size

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/api/inspect")
def inspect():
    try:
        data = request.get_json(silent=True) or {}
        url = validate_url(str(data.get("url", "")).strip())
        filename, content_type, size = inspect_url(url)
        return jsonify({
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "size_human": f"{size / 1024 / 1024:.1f} MB" if size else "desconhecido"
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@app.post("/api/download")
def download():
    temp_dir = Path(tempfile.mkdtemp(prefix="musiflow_"))
    try:
        data = request.get_json(silent=True) or {}
        url = validate_url(str(data.get("url", "")).strip())
        fmt = str(data.get("format", "mp3")).lower()
        quality = str(data.get("quality", "192k"))

        if fmt not in ALLOWED_FORMATS:
            raise ValueError("Formato inválido.")

        # Baixa somente a URL direta fornecida pelo usuário.
        source = temp_dir / "source"
        with requests.get(url, stream=True, timeout=TIMEOUT) as response:
            response.raise_for_status()
            total = 0
            with source.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise ValueError("O arquivo excede o limite de 500 MB.")
                    file.write(chunk)

        output = temp_dir / f"musiflow.{fmt}"

        if fmt == "mp3":
            bitrate = quality if re.fullmatch(r"(128|192|256|320)k", quality) else "192k"
            cmd = [
                "ffmpeg", "-y", "-i", str(source),
                "-vn", "-codec:a", "libmp3lame", "-b:a", bitrate,
                str(output)
            ]
        else:
            # MP4 mantém o vídeo e tenta produzir áudio compatível com MP4.
            cmd = [
                "ffmpeg", "-y", "-i", str(source),
                "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart",
                str(output)
            ]

        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return send_file(
            output,
            as_attachment=True,
            download_name=output.name,
            mimetype="audio/mpeg" if fmt == "mp3" else "video/mp4"
        )
    except subprocess.CalledProcessError:
        return jsonify({"error": "O FFmpeg não conseguiu processar este arquivo."}), 422
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
