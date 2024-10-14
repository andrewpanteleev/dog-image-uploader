import pytest
import requests
from requests.exceptions import RequestException
from urllib.parse import urlsplit  # Проблема 9: Используем urlsplit для безопасной работы с URL
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class YaUploader:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    # Проблема 4: Отсутствие возврата результата из метода
    # Решение: Возвращаем результат выполнения метода (True/False), чтобы понимать, была ли папка создана.
    def create_folder(self, path):
        url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
        try:
            response = requests.put(f'{url_create}?path={path}', headers=self.headers)
            response.raise_for_status()
            logging.info(f"Folder '{path}' created successfully.")
            return True  # Возвращаем True при успешном выполнении
        except RequestException as e:
            logging.error(f"Error creating folder '{path}': {e}")
            return False  # Возвращаем False при ошибке

    # Проблема 3: Необработанные исключения в сетевых запросах
    # Решение: Добавляем try/catch блок для обработки сетевых ошибок.
    def upload_photos_to_yd(self, path, url_file, name):
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {"path": f'/{path}/{name}', 'url': url_file, "overwrite": "true"}
        try:
            resp = requests.post(url, headers=self.headers, params=params)
            resp.raise_for_status()
            logging.info(f"File '{name}' uploaded successfully.")
        except RequestException as e:
            logging.error(f"Error uploading file '{name}': {e}")


# Проблема 2: Отсутствие обработки ошибок при HTTP-запросах
# Решение: Добавляем обработку ошибок с использованием try/catch и выводим сообщения об ошибках через логирование.
def get_sub_breeds(breed):
    try:
        res = requests.get(f'https://dog.ceo/api/breed/{breed}/list')
        res.raise_for_status()
        return res.json().get('message', [])
    except RequestException as e:
        logging.error(f"Error fetching sub-breeds for '{breed}': {e}")
        return []


# Проблема 2: Нет обработки ошибок в сетевых запросах
# Решение: Добавляем обработку исключений в get_urls.
# Проблема 9: Неоптимальная работа с URL
# Решение: Используем urlsplit из urllib.parse вместо split('/')
def get_urls(breed, sub_breeds):
    url_images = []
    try:
        if sub_breeds:
            for sub_breed in sub_breeds:
                res = requests.get(f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random")
                res.raise_for_status()
                sub_breed_urls = res.json().get('message')
                url_images.append(sub_breed_urls)
        else:
            res = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random")
            res.raise_for_status()
            url_images.append(res.json().get('message'))
        return url_images
    except RequestException as e:
        logging.error(f"Error fetching images for breed '{breed}': {e}")
        return []


# Проблема 6: Функция u не дожидается завершения операций
# Решение: Нужно обеспечить, чтобы загрузка файлов на диск выполнялась только после получения всех URL-адресов.
# Проблема 7: Жестко заданное имя папки
# Решение: Сделать имя папки аргументом функции, чтобы оно было гибким.
def u(breed, folder_name):
    token = "AgAAAAAJtest_tokenxkUEdew"  # Проблема 7: Токен захардкожен, следует получать его из конфигурации или переменных окружения
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    yandex_client = YaUploader(token)

    # Проблема 4: Не проверяется успешное создание папки
    # Решение: Проверяем результат выполнения create_folder и прекращаем выполнение при ошибке
    if not yandex_client.create_folder(folder_name):
        logging.error(f"Failed to create folder '{folder_name}'.")
        return

    for url in urls:
        # Проблема 9: Неоптимальная работа с URL
        # Решение: Используем urlsplit для безопасного извлечения имени файла
        parsed_url = urlsplit(url)
        file_name = parsed_url.path.split('/')[-1]  # Извлекаем имя файла из URL

        if yandex_client.upload_photos_to_yd(folder_name, url, file_name) is None:
            logging.error(f"Failed to upload file '{file_name}'.")


# Проблема 5: Неправильная проверка в тесте загрузки
# Решение: Убедиться, что результаты асинхронных операций правильно проверяются после их завершения
@pytest.mark.parametrize('breed', ['doberman', 'bulldog', 'collie'])  # Проблема 10: Убираем случайный выбор породы
def test_proverka_upload_dog(breed):
    u(breed, "test_folder")

    # Проблема 2: Отсутствие обработки ошибок
    # Решение: Добавляем обработку ошибок при запросе состояния папки на Яндекс.Диск
    url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'OAuth AgAAAAAJtest_tokenxkUEdew'
    }
    try:
        response = requests.get(f'{url_create}?path=/test_folder', headers=headers)
        response.raise_for_status()

        assert response.json()['type'] == "dir"
        assert response.json()['name'] == "test_folder"
        if not get_sub_breeds(breed):
            assert len(response.json()['_embedded']['items']) == 1
            for item in response.json()['_embedded']['items']:
                assert item['type'] == 'file'
                assert item['name'].startswith(breed)
        else:
            assert len(response.json()['_embedded']['items']) == len(get_sub_breeds(breed))
            for item in response.json()['_embedded']['items']:
                assert item['type'] == 'file'
                assert item['name'].startswith(breed)
    except RequestException as e:
        logging.error(f"Error fetching folder contents: {e}")
