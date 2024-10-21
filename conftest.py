import pytest
from unittest.mock import patch
import requests

@pytest.fixture
def yandex_uploader():
    token = "AgAAAAAJtest_tokenxkUEdew"
    return YaUploader(token)

@pytest.mark.parametrize('breed', ['doberman', 'bulldog', 'collie'])
@patch('requests.get')
@patch('requests.put')
@patch('requests.post')
def test_proverka_upload_dog(mock_post, mock_put, mock_get, breed, yandex_uploader):
    """
    Тест для проверки загрузки изображений породы на Яндекс.Диск.

    :param breed: Имя породы.
    """
    if breed == 'doberman':
        mock_get.side_effect = [
            # Нет подпород
            {'message': []},  
            # Ссылка на картинку
            {'message': 'https://dog.ceo/api/img/doberman/dog1.jpg'}  
        ]
    else:
        mock_get.side_effect = [
            # Подпороды
            {'message': ['sub1', 'sub2']},
            # Картинки для каждой подпороды
            {'message': 'https://dog.ceo/api/img/bulldog/sub1_dog1.jpg'},
            {'message': 'https://dog.ceo/api/img/bulldog/sub2_dog1.jpg'}
        ]

    mock_put.return_value.status_code = 200
    mock_post.return_value.status_code = 200

    u(breed, "test_folder")

    assert mock_get.call_count > 0  # Убедимся, что mock_get был вызван
    mock_put.assert_called_once()
    mock_post.assert_called()