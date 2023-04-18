from flask import Flask, render_template, request, redirect
import os
import datetime
import requests
import time
import socket
import urllib.parse
from geopy.distance import geodesic

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Координаты сервера
my_latitude = 48.61899948120117
my_longitude = 34.64149856567383

# Ключ API сервиса гео-DNS (для примера)
ipstack_api_key = '09d0a8b1fbbd0e9f446badef2886ae0b'

# Функция для определения IP-адреса сервера
def get_server_ip():
    return request.host_url

# Функция для проверки допустимых расширений файлов
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Функция для получения текущей даты и времени
def get_current_datetime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Функция для получения размера файла в человекочитаемом формате
def get_file_size(file_path):
    size = os.path.getsize(file_path)
    # Преобразование размера в MB с округлением до 2 знаков после запятой
    return "{:.2f} MB".format(size / (1024 * 1024))

# Функция для получения потраченного времени на загрузку файла
def get_download_time(start_time):
    end_time = time.time()
    download_time = end_time - start_time
    return "{:.2f} сек.".format(download_time)

# Функция для расчета расстояния между серверами на основе координат.
def calculate_distance(server_ip, my_latitude, my_longitude, ipstack_api_key):
    # Отправка запроса к сервису IPStack для получения информации о местоположении сервера загрузки файла
    ipstack_url = f'http://api.ipstack.com/{server_ip}'
    params = {'access_key': ipstack_api_key}
    response = requests.get(ipstack_url, params=params)
    location_data = response.json()

    # Извлечение координат сервера загрузки файла из информации о местоположении
    latitude = location_data['latitude']
    longitude = location_data['longitude']

    # Расчет расстояния между координатами сервера загрузки файла и вашим сервером (например, по координатам вашего сервера)
    distance = geodesic((my_latitude, my_longitude), (latitude, longitude)).km

    # Округление расстояния до 2 знаков после запятой и добавление единицы измерения
    distance_rounded = round(distance, 2)
    distance_with_unit = f'{distance_rounded} км'

    return distance_with_unit

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        # Загрузка файла через форму
        file = request.files['file']
        if file.filename == '':
            return "Ошибка: файл не выбран."
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    elif 'file_link' in request.form:
        # Загрузка файла по ссылке
        file_link = request.form['file_link']
        if file_link == '':
            return "Ошибка: ссылка на файл не указана."
        try:
            # Загрузка файла по ссылке
            start_time = time.time()
            file = requests.get(file_link, stream=True)
            filename = file_link.split('/')[-1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(file_path, 'wb') as f:
                for chunk in file.iter_content(1024):
                    f.write(chunk)
            download_time = get_download_time(start_time)
        except requests.exceptions.RequestException as e:
            return f"Ошибка при загрузке файла по ссылке: {str(e)}"
    else:
        return "Ошибка: файл не выбран."

    # Получение информации о файле
    file_size = get_file_size(file_path)
    upload_time = get_current_datetime()
    parsed_url = urllib.parse.urlparse(file_link)
    server_ip = socket.gethostbyname(parsed_url.netloc)
    distance = calculate_distance(server_ip, my_latitude, my_longitude, ipstack_api_key)

    # Возврат информации о загруженном файле на страницу
    return render_template("upload.html", server_ip=server_ip, filename=filename, file_size=file_size,
                           upload_time=upload_time, download_time=download_time, distance=distance)

if __name__ == '__main__':
    app.run(debug=True)
