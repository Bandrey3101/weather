import logging
import requests
import aiosqlite
import asyncio
from aiogram import Bot, Dispatcher, types
#from aiogram.types import ParseMode
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import config

API_TOKEN = config.token
OPENWEATHER_API_KEY = config.weather
DB_PATH = 'weather_logs.db'
CACHE_EXPIRY = timedelta(minutes=10)

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Инициализация FastAPI
app = FastAPI()

# Логирование
logging.basicConfig(level=logging.INFO)

# Кэш для погоды
weather_cache = {}


async def create_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS logs (
                                id INTEGER PRIMARY KEY,
                                user_id INTEGER,
                                command TEXT,
                                response TEXT,
                                created_at TIMESTAMP
                            )''')
        await db.commit()


# Получение погоды
async def get_weather(city: str):
    current_time = datetime.now()

    # Проверка кэша
    if city in weather_cache:
        cached_data, timestamp = weather_cache[city]
        if current_time - timestamp < CACHE_EXPIRY:
            return cached_data

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        weather_info = {
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }
        weather_cache[city] = (weather_info, current_time)
        return weather_info
    else:
        return None


# Команда /start
async def send_welcome(message: types.Message):
    await message.reply('Данный бот был создан в качестве теста для компании BobrAi\n'
                        'Воспользуйтесь командой /weather <город> чтобы узнать погоду.')


# Команда /weather
async def send_weather(message: types.Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Пожалуйста, укажите город. Пример: /weather Москва")
        return

    city = " ".join(args[1:])
    weather_data = await get_weather(city)

    if weather_data:
        response = (f"Погода в городе {city}:\n"
                    f"Температура: {weather_data['temperature']}°C\n"
                    f"Ощущается как: {weather_data['feels_like']}°C\n"
                    f"Описание: {weather_data['description'].capitalize()}\n"
                    f"Влажность: {weather_data['humidity']}%\n"
                    f"Скорость ветра: {weather_data['wind_speed']} м/с")
    else:
        response = "Не удалось получить погоду для указанного города. Проверьте правильность названия."

    await message.reply(response)

    # Логирование запроса
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO logs (user_id, command, response, created_at) VALUES (?, ?, ?, ?)",
                         (message.from_user.id, message.text, response, datetime.now()))
        await db.commit()


# Регистрация хэндлера
dp.message.register(send_weather, Command(commands=['weather']))
dp.message.register(send_welcome, Command(commands=['start']))


# REST API для просмотра логов
@app.get("/logs")
async def get_logs():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM logs")
        logs = await cursor.fetchall()
        return JSONResponse(content={"logs": logs})


@app.get("/logs/{user_id}")
async def get_user_logs(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT * FROM logs WHERE user_id = ?", (user_id,))
        logs = await cursor.fetchall()
        return JSONResponse(content={"logs": logs})


# Запуск бота и FastAPI
async def main():
    await create_db()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())