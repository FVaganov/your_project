from flask import Flask, render_template, send_file, abort, request, redirect, url_for
import boto3
from botocore.exceptions import ClientError
import io
import datetime

app = Flask(__name__)

# Настройки подключения к S3
s3_client = boto3.client(
    's3',
    endpoint_url='https://s3.ru-1.storage.selcloud.ru',
    region_name='ru-1',
    aws_access_key_id='638f6aea9b6240e5be852c8105a92dbf',  # Замените на ваш Access Key ID
    aws_secret_access_key='e3fb707ba53745a180c5de18b77485a2',  # Замените на ваш Secret Access Key
    verify=False
)

# Время ожидания между скачиваниями в секундах
download_wait_time = 10  # 10 секунд

# Словарь для хранения времени последнего скачивания файлов
last_download_times = {}

@app.route('/')
def index():
    # Получаем список файлов из S3
    try:
        response = s3_client.list_objects_v2(Bucket='test-pablic-bucket2')
        files = [obj['Key'] for obj in response.get('Contents', [])]
        return render_template('index.html', files=files)
    except ClientError as e:
        print(e)
        return "Ошибка при получении файлов", 500

@app.route('/download/<filename>')
def download_file(filename):
    current_time = datetime.datetime.now()

    # Проверяем время последнего скачивания файла
    last_download_time = last_download_times.get(filename)

    # Проверяем, прошло ли достаточно времени с последнего скачивания
    if last_download_time is None or (current_time - last_download_time).total_seconds() >= download_wait_time:
        try:
            # Получаем файл из S3
            file_object = s3_client.get_object(Bucket='test-pablic-bucket2', Key=filename)
            file_data = file_object['Body'].read()

            # Обновляем время последнего скачивания
            last_download_times[filename] = current_time

            # Возвращаем файл в виде ответа
            return send_file(io.BytesIO(file_data), download_name=filename, as_attachment=True)

        except ClientError as e:
            print(e)
            return abort(404)  # Файл не найден
    else:
        return abort(403)  # Доступ запрещен, еще не прошло времени для повторного скачивания

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                # Загружаем файл в S3
                s3_client.upload_fileobj(file, 'test-pablic-bucket2', file.filename)
                return redirect(url_for('index'))  # Перенаправляем на главную страницу после загрузки
            except ClientError as e:
                print(e)
                return "Ошибка при загрузке файла", 500
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
