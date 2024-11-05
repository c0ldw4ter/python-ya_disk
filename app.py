from flask import Flask, render_template, request, send_file, redirect, url_for
import requests

app = Flask(__name__)
YANDEX_API_URL = "https://cloud-api.yandex.net/v1/disk/public/resources"

# Получение списка файлов
def get_files(public_key):
    params = {"public_key": public_key}
    response = requests.get(YANDEX_API_URL, params=params)
    if response.status_code == 200:
        items = response.json().get("_embedded", {}).get("items", [])
        return [{"name": item["name"], "file": item["file"]} for item in items if item["type"] == "file"]
    else:
        return None

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
    response = requests.get(file_url, stream=True)
    filename = file_url.split('/')[-1]
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
