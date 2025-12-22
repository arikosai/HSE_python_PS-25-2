#!/usr/bin/env python3
# ya.py
import os
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path

import requests

YADISK_API = "https://cloud-api.yandex.net/v1/disk"
UPLOADED_FILE = Path("uploaded.json")

# функции для сохранения
def load_uploaded():
    if UPLOADED_FILE.exists():
        try:
            return json.loads(UPLOADED_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def save_uploaded(items):
    UPLOADED_FILE.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_ext_from_url(url: str) -> str:
    """
    Достаём расширение из пути URL (последняя часть после точки).
    Если не получается — вернём 'bin'.
    """
    try:
        path = urllib.parse.urlparse(url).path
    except Exception:
        return "bin"

    filename = path.rsplit("/", 1)[-1]
    if "." in filename and not filename.endswith("."):
        ext = filename.rsplit(".", 1)[-1].lower()
        # чуть-чуть фильтруем, чтобы не получилось странных расширений
        if ext and all(ch.isalnum() for ch in ext) and len(ext) <= 10:
            return ext
    return "bin"


def upload_by_url(token: str, file_url: str, disk_path: str):
    """
    Запуск загрузки по URL на Яндекс.Диск.
    Возвращает (status_code, text_response).
    """
    endpoint = f"{YADISK_API}/resources/upload"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"url": file_url, "path": disk_path}

    resp = requests.post(endpoint, headers=headers, params=params, timeout=20)
    return resp.status_code, resp.text


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, body: str, content_type: str = "text/plain; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path != "/":
            self._send(404, "not found")
            return

        uploaded = load_uploaded()
        uploaded_json = json.dumps(uploaded, ensure_ascii=False)

        # Нестилизованная форма. POST отправит url как application/x-www-form-urlencoded.
        html = f"""<!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>Yandex Disk uploader</title>
          <style>
            body {{
              font-family: sans-serif;
              padding: 20px;
            }}
            button {{
              padding: 8px 16px;
              margin-bottom: 20px;
            }}
            ul {{
              padding: 0;
            }}
            li {{
              list-style: none;
              padding: 6px;
              margin-bottom: 6px;
              border: 1px solid #ccc;
            }}
            .uploaded {{
              background: rgba(0, 200, 0, 0.25);
            }}
          </style>
        </head>
        <body>

          <button id="btn">Загрузить по URL</button>

          <ul id="files"></ul>

          <script>
            const uploaded = {uploaded_json};
            const ul = document.getElementById("files");

            uploaded.forEach(item => {{
              const li = document.createElement("li");
              li.className = "uploaded";
              li.textContent = item.disk_path + " ← " + item.url;
              ul.appendChild(li);
            }});

            document.getElementById("btn").addEventListener("click", async () => {{
              const url = prompt("Введите URL файла:");
              if (!url) return;

              try {{
                const resp = await fetch("/download", {{
                  method: "POST",
                  headers: {{ "Content-Type": "text/plain; charset=utf-8" }},
                  body: url
                }});

                const text = await resp.text();
                alert(text);
                location.reload();
              }} catch (e) {{
                alert("Ошибка: " + e);
              }}
            }});
          </script>

        </body>
        </html>
        """
        self._send(200, html, "text/html; charset=utf-8")

    def do_POST(self):
        if self.path != "/download":
            self._send(404, "not found")
            return

        token = ''
        if not token:
            self._send(500, "YADISK_TOKEN is not set")
            return

        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length)

        # Требование: "в теле запроса урл" — значит если пришёл чистый текст, берём его.
        body_text = raw.decode("utf-8", errors="replace").strip()

        file_url = body_text

        if not file_url:
            self._send(400, "empty url")
            return
        if not (file_url.startswith("http://") or file_url.startswith("https://")):
            self._send(400, "url must start with http:// or https://")
            return

        ext = get_ext_from_url(file_url)
        ts = int(time.time())
        disk_path = f"/Uploads/{ts}.{ext}"

        status, yadisk_resp_text = upload_by_url(token, file_url, disk_path)

        if status in (200, 201, 202):
            uploaded = load_uploaded()
            uploaded.append({
                "url": file_url,
                "disk_path": disk_path,
            })
            save_uploaded(uploaded)

        # Вернём максимально простой текстовый ответ
        self._send(
            status,
            f"disk_path={disk_path}\nstatus={status}\nresponse={yadisk_resp_text}\n",
        )

    def log_message(self, fmt, *args):
        return


def main():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8080"))
    httpd = HTTPServer((host, port), Handler)
    print(f"Open: http://{host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
