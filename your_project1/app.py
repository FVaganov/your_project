from flask import Flask, request, render_template, send_file
import requests
import boto3
import os
from concurrent.futures import ThreadPoolExecutor

# Создаем экземпляр приложения Flask
app = Flask(__name__)

# Настройки для подключения к S3
S3_BUCKET = 'test-pablic-bucket1'  # Имя вашего S3 бакета
S3_URL = 'https://s3.storage.selcloud.ru'  # URL для доступа к вашему S3
S3_ACCESS_KEY = '3b4494d9547d4a52aebaa498e0df9304'  # Ваш ключ доступа к S3
S3_SECRET_KEY = 'd8d897d6cab14800996ae69f16869609'  # Ваш секретный ключ доступа к S3

# Создаем клиент для работы с S3
s3_client = boto3.client('s3',
                         endpoint_url=S3_URL,
                         aws_access_key_id=S3_ACCESS_KEY,
                         aws_secret_access_key=S3_SECRET_KEY)

# Ссылка на файл в S3 для скачивания
S3_FILE_URL = "https://7d9ce43c-2ef8-40a5-8094-16b6a42ae260.selstorage.ru/user-agreement.pdf"


@app.route('/')
def index():
    # Отображаем главную страницу с формой загрузки
    return render_template('index.html')


@app.route('/download')
def download_file():
    # Обработка запроса на скачивание файла
    response = requests.get(S3_FILE_URL)  # Отправляем GET-запрос на скачивание файла
    if response.status_code == 200:  # Проверяем успешность запроса
        with open('user-agreement.pdf', 'wb') as f:  # Открываем файл для записи в бинарном режиме
            f.write(response.content)  # Записываем содержимое ответа в файл
        return send_file('user-agreement.pdf', as_attachment=True)  # Отправляем файл пользователю как вложение
    else:
        return "Ошибка при скачивании файла", 404  # Если произошла ошибка, возвращаем 404


@app.route('/upload_file', methods=['POST'])
def upload_file():
    # Обработка запроса на загрузку одного файла
    file = request.files['file']  # Получаем файл из формы по имени 'file'
    s3_client.upload_fileobj(file, S3_BUCKET, file.filename)  # Загружаем файл в S3
    return 'File uploaded successfully!'  # Возвращаем сообщение об успешной загрузке


@app.route('/upload_folder', methods=['POST'])
def upload_folder():
    # Обработка запроса на загрузку нескольких файлов (папки)
    files = request.files.getlist('folder')  # Получаем список файлов из формы по имени 'folder'

    def upload_to_s3(file):
        # Функция для загрузки одного файла в S3
        s3_client.upload_fileobj(file, S3_BUCKET, file.filename)  # Загружаем файл в S3

    # Используем ThreadPoolExecutor для параллельной загрузки файлов
    with ThreadPoolExecutor() as executor:
        executor.map(upload_to_s3, files)  # Загружаем все файлы параллельно

    return 'Folder uploaded successfully!'  # Возвращаем сообщение об успешной загрузке папки


if __name__ == '__main__':
    app.run(debug=True)  # Запускаем приложение в режиме отладки
