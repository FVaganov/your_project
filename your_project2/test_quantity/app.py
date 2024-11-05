from flask import Flask, render_template, send_file, abort, request, redirect, url_for
import boto3
from botocore.exceptions import ClientError
import io

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

# Количество разрешенных скачиваний
download_limit = 1

# Словарь для хранения количества скачиваний для каждого файла
download_count = {}

@app.route('/')
def index():
    # Получаем список файлов из S3
    bucket_name = 'test-pablic-bucket2'  # Замените на имя вашего бакета
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        files = [item['Key'] for item in response.get('Contents', [])]
    except ClientError as e:
        print(e)
        files = []

    return render_template('index.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    # Проверяем, было ли уже скачано максимальное количество раз
    if filename in download_count and download_count[filename] >= download_limit:
        return abort(403)  # Доступ запрещен

    try:
        # Получаем файл из S3
        file_object = s3_client.get_object(Bucket='test-pablic-bucket2', Key=filename)
        file_data = file_object['Body'].read()

        # Увеличиваем счетчик скачиваний
        if filename in download_count:
            download_count[filename] += 1
        else:
            download_count[filename] = 1

        # Возвращаем файл в виде ответа
        return send_file(io.BytesIO(file_data), download_name=filename, as_attachment=True)

    except ClientError as e:
        print(e)
        return abort(404)  # Файл не найден

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
