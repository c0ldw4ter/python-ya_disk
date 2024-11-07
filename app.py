from flask import Flask, render_template, request, send_file
from urllib.parse import urlparse, parse_qs
import requests

app = Flask(__name__)
YANDEX_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"

# Функция для получения файлов и папок
def get_files(public_key, path=''):
    params = {"public_key": public_key, "path": path, "limit": 100}
    files = []
    response = requests.get(YANDEX_API_URL, params=params)
    if response.status_code == 200:
        items = response.json().get("_embedded", {}).get("items", [])
        for item in items:
            if item["type"] == "dir":
                # Если элемент - папка, добавляем её с пустым списком вложенных файлов
                files.append({"name": item["name"], "type": "folder", "path": item["path"], "items": []})
            elif item["type"] == "file":
                # Если элемент - файл, добавляем ссылку для скачивания
                files.append({"name": item["name"], "type": "file", "file": item["file"]})
    return files

@app.route('/', methods=['GET', 'POST'])
def index():
    files = None
    if request.method == 'POST':
        public_key = request.form['public_key']
        files = get_files(public_key)
    return render_template('index.html', files=files)

@app.route('/download', methods=['POST'])
def download():
    file_url = request.form['file_url']
    parsed_url = urlparse(file_url)
    filename = parse_qs(parsed_url.query).get('filename', ['downloaded_file'])[0]
    
    response = requests.get(file_url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)
    
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
