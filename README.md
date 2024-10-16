# dog-image-uploader

## Результаты Pylint

(.venv) C:\Users\a.panteleev\Documents\GitHub\dog-image-uploader>pylint test_dogs.py

Your code has been rated at 10.00/10 (previous run: 9.88/10, +0.12)

---



### 1. **Отсутствие обработки ошибок при HTTP-запросах (Критичность: Высокая)**

* Проблема: Если сетевой запрос не удался (например, сервер недоступен или вернулся неуспешный статус-код), это может привести к неожиданному завершению программы.
* Решение: Добавлены блоки `try/except` для обработки ошибок запросов с использованием `requests.exceptions.RequestException`. Это позволяет предотвратить внезапные падения программы и корректно обрабатывать ошибки.

---

### 2. **Асинхронные операции не дожидаются завершения (Критичность: Высокая)**

* Проблема: Код запускает асинхронные операции (например, создание папки и загрузку файлов) без ожидания завершения предыдущих шагов. Это может привести к непредсказуемым результатам.
* Решение: Код был структурирован так, чтобы функции дожидались завершения запросов перед выполнением последующих шагов.

---

### 3. **Необработанные исключения в функциях загрузки файлов (Критичность: Высокая)**

* Проблема: Если во время загрузки файла на Яндекс.Диск произойдёт ошибка, она не будет обработана, что может привести к неожиданному завершению программы.
* Решение: Добавлены блоки `try/except` для обработки исключений в методах `upload_photos_to_yd` класса `YaUploader`.

---

### 4. **Отсутствие возврата значений из методов `YaUploader` (Критичность: Средняя)**

* Проблема: Методы `create_folder` и `upload_photos_to_yd` не возвращают результат выполнения операций, что затрудняет проверку успешности действий.
* Решение: Методы теперь возвращают `True` или `False` в зависимости от успешности выполнения операции. Это даёт возможность контролировать выполнение программы.

---

### 5. **Неверная проверка в тесте загрузки файлов (Критичность: Средняя)**

* Проблема: Тест проверяет содержимое папки на Яндекс.Диске сразу после выполнения асинхронных операций, что может приводить к ложным результатам, если операции не успели завершиться.
* Решение: Проверка теперь проводится после завершения всех операций, что гарантирует корректность тестов.

---

### 6. **Неоптимальная работа с URL картинок (Критичность: Низкая)**

* Проблема: В коде использовался метод `split('/')` для работы с URL, что не является надёжным подходом, так как структура URL может измениться.
* Решение: Использован модуль `urllib.parse` и его функция `urlsplit` для безопасного разбора URL и получения имени файла.

---

### 7. **Жёстко заданный токен в коде (Критичность: Средняя)**

* Проблема: Токен доступа к Яндекс.Диску захардкожен в коде, что небезопасно. Если токен попадёт в чужие руки, это может привести к утечке данных.
* Решение: Рекомендуется получать токен через переменные окружения или конфигурационные файлы для повышения безопасности.

---

### 8. **Отсутствие обратной связи при завершении создания папки (Критичность: Низкая)**

* Проблема: Метод `create_folder` не возвращает результат операции, что затрудняет понимание, была ли папка успешно создана.
* Решение: Метод теперь возвращает `True` или `False`, что позволяет проверить успешность создания папки и при необходимости остановить выполнение программы.

---

### 9. **Избыточные запросы к API для картинок (Критичность: Средняя)**

* Проблема: В коде выполняются лишние запросы к API для получения случайных картинок, что увеличивает нагрузку на сеть и API.
* Решение: Убран лишний вызов, теперь для каждой породы или подпороды запрашивается только одна случайная картинка.

---

### 10. **Случайный выбор породы в тестах (Критичность: Низкая)**

* Проблема: Тесты зависели от случайного выбора породы, что делает их недетерминированными. Это может привести к сложностям в отладке, так как каждый запуск теста может давать разные результаты.
* Решение: Убран случайный выбор породы, теперь тест проверяет все породы последовательно, что делает тесты предсказуемыми и повторяемыми.

---

### 11. **Отсутствие логирования (Критичность: Средняя)**

* Проблема: В коде отсутствует логирование важных операций (создание папки, загрузка файла, ошибки). Это затрудняет отладку и отслеживание выполнения программы.
* Решение: Добавлено логирование для основных операций, таких как создание папки, загрузка файлов и обработка ошибок. Это улучшает читаемость кода и упрощает диагностику проблем.
