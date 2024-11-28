from flask import Flask, request, render_template, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

app = Flask(__name__)

# Настройка клиента S3
s3_client = boto3.client(
    "s3",
    endpoint_url='https://s3.ru-1.storage.selcloud.ru',
    aws_access_key_id='283177b6eaf7425a9a91dafa21345fa8',  # Замените на ваш Access Key
    aws_secret_access_key='f363af277db84f12a1528ea68f8dde1d'  # Замените на ваш Secret Key
)

BUCKET_NAME = 'test-pablic-bucket2'  # Замените на имя вашего бакета

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    try:
        s3_client.upload_fileobj(file, BUCKET_NAME, file.filename)
        return "File uploaded successfully"
    except NoCredentialsError:
        return "Credentials not available"
    except ClientError as e:
        return f"Failed to upload file: {e.response['Error']['Message']}"
    except Exception as e:
        return str(e)

@app.route('/generate_presigned_url', methods=['GET'])
def generate_presigned_url():
    filename = request.args.get('filename')

    try:
        response = s3_client.generate_presigned_url('put_object',
                                                      Params={'Bucket': BUCKET_NAME,
                                                              'Key': filename},
                                                      ExpiresIn=3600)  # Ссылка будет действовать 1 час
        print(f"Generated presigned URL: {response}")  # Вывод ссылки в терминал
        return jsonify({'url': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
