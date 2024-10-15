"""
Модуль для загрузки изображений собак на Яндекс.Диск с использованием API Dog CEO.
"""

import logging
from urllib.parse import urlsplit
import pytest
import requests
from requests.exceptions import RequestException


# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class YaUploader:
    """
    Класс для взаимодействия с Яндекс.Диском.
    Позволяет создавать папки и загружать файлы по URL.
    """

    def __init__(self, token):
        """
        Инициализирует объект YaUploader с токеном для доступа к API Яндекс.Диска.

        :param token: OAuth-токен для аутентификации.
        """
        self.token = token
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def create_folder(self, path):
        """
        Создает папку на Яндекс.Диске по указанному пути.

        :param path: Путь для создания папки.
        :return: Возвращает True, если папка успешно создана, иначе False.
        """
        url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
        try:
            response = requests.put(f'{url_create}?path={path}', headers=self.headers, timeout=10)
            response.raise_for_status()
            logging.info("Folder '%s' created successfully.", path)
            return True
        except RequestException as e:
            logging.error("Error creating folder '%s': %s", path, e)
            return False

    def upload_photos_to_yd(self, path, url_file, name):
        """
        Загружает фото на Яндекс.Диск по URL.

        :param path: Путь для сохранения файла.
        :param url_file: URL файла для загрузки.
        :param name: Имя файла.
        :return: True, если файл успешно загружен, иначе False.
        """
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        params = {"path": f'/{path}/{name}', 'url': url_file, "overwrite": "true"}
        try:
            resp = requests.post(url, headers=self.headers, params=params, timeout=10)
            resp.raise_for_status()
            logging.info("File '%s' uploaded successfully.", name)
            return True
        except RequestException as e:
            logging.error("Error uploading file '%s': %s", name, e)
            return False


def get_sub_breeds(breed):
    """
    Получает подвиды породы собаки по ее имени.

    :param breed: Имя породы.
    :return: Список подвидов породы.
    """
    try:
        res = requests.get(
            f'https://dog.ceo/api/breed/{breed}/list',
            timeout=10
        )
        res.raise_for_status()
        return res.json().get('message', [])
    except RequestException as e:
        logging.error("Error fetching sub-breeds for '%s': %s", breed, e)
        return []


def get_urls(breed, sub_breeds):
    """
    Получает URL изображений для породы и подвидов.

    :param breed: Имя породы.
    :param sub_breeds: Список подвидов породы.
    :return: Список URL изображений.
    """
    url_images = []
    try:
        if sub_breeds:
            for sub_breed in sub_breeds:
                res = requests.get(
                    f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random",
                                   timeout=10
                )
                res.raise_for_status()
                sub_breed_urls = res.json().get('message')
                url_images.append(sub_breed_urls)
        else:
            res = requests.get(f"https://dog.ceo/api/breed/{breed}/images/random", timeout=10)
            res.raise_for_status()
            url_images.append(res.json().get('message'))
        return url_images
    except RequestException as e:
        logging.error("Error fetching images for breed '%s': %s", breed, e)
        return []


def upload_dog_images(breed, folder_name):
    """
    Основная функция для загрузки изображений породы на Яндекс.Диск.

    :param breed: Имя породы.
    :param folder_name: Имя папки для сохранения изображений.
    """
    token = "AgAAAAAJtest_tokenxkUEdew"
    sub_breeds = get_sub_breeds(breed)
    urls = get_urls(breed, sub_breeds)
    yandex_client = YaUploader(token)

    if not yandex_client.create_folder(folder_name):
        logging.error("Failed to create folder '%s'.", folder_name)
        return

    for url in urls:
        parsed_url = urlsplit(url)
        file_name = parsed_url.path.split('/')[-1]

        if yandex_client.upload_photos_to_yd(folder_name, url, file_name) is None:
            logging.error("Failed to upload file '%s'.", file_name)


@pytest.mark.parametrize('breed', ['doberman', 'bulldog', 'collie'])
def test_proverka_upload_dog(breed):
    """
    Тест для проверки загрузки изображений породы на Яндекс.Диск.

    :param breed: Имя породы.
    """
    upload_dog_images(breed, "test_folder")

    url_create = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'OAuth AgAAAAAJtest_tokenxkUEdew'
    }
    try:
        response = requests.get(f'{url_create}?path=/test_folder', headers=headers, timeout=10)
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
        logging.error("Error fetching folder contents: %s", e)
