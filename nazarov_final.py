import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


class TaskManager:
    def __init__(self, filename="tasks.txt"):
        self.filename = filename
        self.tasks = []
        self.next_id = 1
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                if self.tasks:
                    max_id = max(task['id'] for task in self.tasks)
                    self.next_id = max_id + 1
            except Exception:
                self.tasks = []

    def save_tasks(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def create_task(self, title, priority):
        valid_priorities = ["low", "normal", "high"]
        if priority not in valid_priorities:
            priority = "normal"

        task = {
            "id": self.next_id,
            "title": title,
            "priority": priority,
            "isDone": False
        }

        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return task

    def get_all_tasks(self):
        return self.tasks

    def get_task_by_id(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None

    def mark_as_complete(self, task_id):
        task = self.get_task_by_id(task_id)
        if task is None:
            return False

        task['isDone'] = True
        self.save_tasks()
        return True


class TodoServerHandler(BaseHTTPRequestHandler):
    task_manager = TaskManager()

    def _set_response(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_response(200)

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/tasks':
            tasks = self.task_manager.get_all_tasks()
            response = json.dumps(tasks, ensure_ascii=False)

            self._set_response(200)
            self.wfile.write(response.encode('utf-8'))
        else:
            self._set_response(404)
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''

        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')

        if parsed_path.path == '/tasks' and len(path_parts) == 1:
            try:
                data = json.loads(post_data.decode('utf-8'))
                title = data.get('title', '').strip()
                priority = data.get('priority', 'normal').strip().lower()

                if not title:
                    self._set_response(400)
                    self.wfile.write(b'{"error": "Title is required"}')
                    return

                task = self.task_manager.create_task(title, priority)
                response = json.dumps(task, ensure_ascii=False)

                self._set_response(201)
                self.wfile.write(response.encode('utf-8'))
            except json.JSONDecodeError:
                self._set_response(400)
                self.wfile.write(b'{"error": "Invalid JSON"}')

        elif len(path_parts) == 3 and path_parts[1].isdigit() and path_parts[2] == 'complete':
            task_id = int(path_parts[1])

            if self.task_manager.mark_as_complete(task_id):
                self._set_response(200)
                self.wfile.write(b'')
            else:
                self._set_response(404)
                self.wfile.write(b'')

        else:
            self._set_response(404)
            self.wfile.write(b'{"error": "Not found"}')

    def log_message(self, format, *args):
        # Отключаем стандартное логирование
        pass


def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, TodoServerHandler)

    print(f"Сервер запущен на порту {port}")
    print("Доступные эндпоинты:")
    print("  GET  /tasks - получить все задачи")
    print("  POST /tasks - создать новую задачу")
    print("  POST /tasks/<id>/complete - отметить задачу как выполненную")
    print("Нажмите Ctrl+C для остановки сервера")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
        httpd.server_close()


if __name__ == '__main__':
    run_server(8080)