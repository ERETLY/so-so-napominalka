import logging
import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)

API_TOKEN = 'TOKEN' # сюда конечно же

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_reminders = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Бот запущен! Используйте команду /text для установки текста напоминания.")

@dp.message(Command("text"))
async def set_text_command(message: types.Message):
    if message.text:
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            user_text = parts[1]
            try:
                with open('text.js', 'w', encoding='utf-8') as f:
                    json.dump({"text": user_text}, f)
                
                await message.answer(f"Текст '{user_text}' установлен! Я буду отправлять его каждые 10 минут.")
                user_reminders[message.from_user.id] = user_text
                asyncio.create_task(send_reminders(message.from_user.id))
            except Exception as e:
                logging.error(f"Ошибка при сохранении текста: {e}")
                await message.answer("Произошла ошибка при сохранении текста. Пожалуйста, попробуйте еще раз.")
        else:
            await message.answer("Пожалуйста, введите текст после команды /text.")
    else:
        await message.answer("Пожалуйста, введите текст после команды /text.")

async def send_reminders(user_id):
    while user_id in user_reminders:
        try:
            await bot.send_message(user_id, user_reminders[user_id])
            await asyncio.sleep(600)  # ВРЕМЯ В СЕКУНДАХ ПЕРЕД ПОВТОРНОЙ ОТПРАВКОЙ
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения: {e}")
            break

@dp.message(Command("stop"))
async def stop_command(message: types.Message):
    if message.from_user.id in user_reminders:
        del user_reminders[message.from_user.id]
        await message.answer("Напоминалка остановлена.")
    else:
        await message.answer("У вас нет активной напоминалки.")

@dp.message()
async def handle_text(message: types.Message):
    await message.answer("абоба, /start для начала или /text для установки текста.")

async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

if __name__ == '__main__':
    asyncio.run(main())