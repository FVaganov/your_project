document.getElementById('uploadButton').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        alert("Пожалуйста, выберите файл для загрузки.");
        return;
    }

    // Здесь вам нужно получить предподписанную ссылку с вашего бэкенда
    const response = await fetch('URL_ДЛЯ_ПРЕДПОДПИСАННОЙ_ССЫЛКИ');
    const { url } = await response.json();

    // Загрузка файла на S3
    const options = {
        method: 'PUT',
        body: file,
        headers: {
            'Content-Type': file.type
        }
    };

    const uploadResponse = await fetch(url, options);
    
    if (uploadResponse.ok) {
        alert("Файл успешно загружен на S3!");
    } else {
        alert("Ошибка загрузки файла на S3.");
    }
});
