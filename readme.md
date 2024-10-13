Документация API

1. Telegram-бот

1.1. Команды
/weather <город>
Описание: Получает текущую погоду в указанном городе.

Параметры:
город (строка): Название города для запроса погоды.

Ответ:
Текущая температура, ощущаемая температура, описание погоды, влажность и скорость ветра.

Пример использования:
/weather Москва

Ответ:
Погода в городе Москва:
Температура: 15°C
Ощущается как: 13°C
Описание: Ясно
Влажность: 60%
Скорость ветра: 5 м/с

/logs
Описание: Получает историю запросов текущего пользователя.

Ответ:
Список логов, связанных с пользователем, содержащий команду и ответ бота.

Пример использования:
/logs

Ответ:
2024-10-10 12:00:00: /weather Москва
2024-10-10 12:05:00: /weather Минск

2. REST API

2.1. Получение логов

GET /logs
Описание: Возвращает список всех запросов.

Ответ:
JSON-объект с массивом записей логов.

Пример запроса:
GET http://localhost:8000/logs

Ответ:
json
{
  "logs": [
    {
      "id": 1,
      "user_id": 123456,
      "command": "/weather Москва",
      "response": "Погода в городе Москва...",
      "created_at": "2024-10-10T12:00:00"
    },
    ...
  ]
}

GET /logs/{user_id}
Описание: Возвращает запросы конкретного пользователя.

Параметры:
user_id (integer): ID пользователя.

Ответ:
JSON-объект с массивом записей логов для конкретного пользователя.

Пример запроса:
GET http://localhost:8000/logs/123456

Ответ:
json
{
  "logs": [
    {
      "id": 1,
      "user_id": 123456,
      "command": "/weather Москва",
      "response": "Погода в городе Москва...",
      "created_at": "2024-10-10T12:00:00"
    }
  ]
}

2.2. Примечания
Все API запросы к серверу FastAPI должны возвращать соответствующий статус код HTTP.
В случае ошибок (например, 404 или 500) должны возвращаться сообщения об ошибках.

3. Установка и запуск

3.1. Установка зависимостей
Убедитесь, что установлены все необходимые зависимости:
pip install -r requirements.txt

3.2. Запуск Telegram-бота
Запустите Telegram-бота с помощью:
python main.py

3.3. Запуск FastAPI
Запустите FastAPI сервер с помощью:
uvicorn main:app --reload