from flask import Flask, request, redirect, url_for, render_template, jsonify
import boto3
from botocore.exceptions import NoCredentialsError
import datetime

app = Flask(__name__)

# Настройки S3
s3 = boto3.client(
    "s3",
    endpoint_url='https://s3.ru-1.storage.selcloud.ru',
    aws_access_key_id='283177b6eaf7425a9a91dafa21345fa8',
    aws_secret_access_key='f363af277db84f12a1528ea68f8dde1d'
)

BUCKET_NAME = 'test-pablic-bucket2'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'Нет файла для загрузки'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'Нет выбранного файла'
    
    try:
        s3.upload_fileobj(file, BUCKET_NAME, file.filename)
        return 'Файл успешно загружен'
    except NoCredentialsError:
        return 'Ошибка: Неверные учетные данные для доступа к S3'
    except Exception as e:
        return f'Ошибка при загрузке файла: {str(e)}'

@app.route('/generate-signed-url', methods=['GET'])
def generate_signed_url():
    file_name = request.args.get('file_name')
    
    try:
        # Генерация предварительно подписанного URL
        url = s3.generate_presigned_url('put_object',
                                          Params={'Bucket': BUCKET_NAME, 'Key': file_name},
                                          ExpiresIn=3600)  # URL будет действителен 1 час
        return jsonify({'url': url})
    except Exception as e:
        return jsonify({'error': str(e)})



if __name__ == '__main__':
    app.run(debug=True)
