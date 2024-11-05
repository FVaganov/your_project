from flask import Flask, request, render_template, redirect, url_for  # Импорт необходимых модулей из Flask
import boto3  # Импорт библиотеки Boto3 для работы с AWS S3
import os  # Импорт модуля os для работы с операционной системой (не используется в данном коде)

# Создание экземпляра приложения Flask
app = Flask(__name__)  # Здесь должно быть __name__, чтобы приложение знало, как его называть

# Инициализация клиента S3 с вашими параметрами
s3 = boto3.client(
    "s3",
    endpoint_url='https://s3.ru-1.storage.selcloud.ru',  # URL конечной точки S3
    region_name='ru-1',  # Регион, в котором находится ваш бакет
    aws_access_key_id='638f6aea9b6240e5be852c8105a92dbf',  # Ваш AWS Access Key ID
    aws_secret_access_key='e3fb707ba53745a180c5de18b77485a2',  # Ваш AWS Secret Access Key
    verify=False  # Отключение проверки SSL (не рекомендуется в продакшене)
)

bucket_name = 'test-pablic-bucket2'  # Имя вашего S3 бакета


@app.route('/')  # Определение маршрута для главной страницы
def index():
    # Получение списка объектов в бакете
    response = s3.list_objects_v2(Bucket=bucket_name)  # Запрос на получение объектов из S3
    files = [obj['Key'] for obj in response.get('Contents', [])]  # Извлечение имен файлов из ответа
    return render_template('index.html', files=files)  # Отправка списка файлов в шаблон для отображения


@app.route('/upload', methods=['POST'])  # Определение маршрута для загрузки файла
def upload_file():
    if 'folder' not in request.files:  # Проверка, что файл был загружен
        return redirect(url_for('index'))  # Перенаправление на главную страницу, если файл не найден

    file = request.files['folder']  # Получение файла из запроса
    if file.filename == '':  # Проверка, что имя файла не пустое
        return redirect(url_for('index'))  # Перенаправление на главную страницу

    # Загрузка файла в S3
    s3.put_object(Bucket=bucket_name, Key=file.filename, Body=file)  # Загрузка файла в указанный бакет

    return redirect(url_for('index'))  # Перенаправление на главную страницу после загрузки


@app.route('/download/<filename>')  # Определение маршрута для скачивания файла
def download_file(filename):
    # Генерация предзаполненного URL для загрузки файла
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': filename},  # Параметры для получения объекта
        ExpiresIn=3600  # Время действия ссылки в секундах (1 час)
    )
    print(presigned_url)  # Вывод предзаполненного URL в консоль для отладки
    return redirect(presigned_url)  # Перенаправление пользователя на предзаполненный URL для скачивания


if __name__ == '__main__':  # Проверка, что скрипт запущен напрямую
    app.run(debug=True)  # Запуск приложения в режиме отладки
