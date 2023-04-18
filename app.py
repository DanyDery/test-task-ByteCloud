from flask import Flask, render_template, request, send_from_directory
import os
import datetime
import time
import socket

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    start_time = time.time()  # Запоминаем время начала загрузки файла
    file = request.files['file']
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        server_ip = get_server_ip()
        file_url = request.url_root + 'download/' + filename
        file_size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        upload_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elapsed_time = time.time() - start_time  # Вычисляем время, затраченное на загрузку файла
        return render_template('upload.html', server_ip=server_ip, filename=filename, file_url=file_url, file_size=file_size, upload_time=upload_time, elapsed_time=elapsed_time)
    else:
        return "Файл не выбран"

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

def get_server_ip():
    # Получаем IP-адрес сервера
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

if __name__ == '__main__':
    app.run(debug=True)
