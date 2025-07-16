import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from config.app_config import API_TOKEN
from config.logging_config import logger
from app.parser.parser_script import get_json_house
from app.google_sheets_app.sheets_script import write_row_sheets
# Создаем экземпляры бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Привет!\n Присылай мне ссылку на квартиру в авито или циан, а я запишу ее в google таблицу😘\nСреднее время ответа 5-10сек.")

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply("Пришли ссылку и я запишу ее в таблицу.")

@dp.message()
async def handle_message(message: Message):
    text = message.text or ""
    # парсим данные
    try:
        house_json = get_json_house(text)
    except Exception as e:
        await message.reply(f"Произошла ошибка:\n\n{e}")
        logger.error(f"Произошла ошибка: {e}")
        return None

    if type(house_json) == str:
        await message.reply(house_json)
        logger.info(house_json)
        return None
    logger.info(f"Данные сайта {text} спаршены")
    row = [
        house_json['url'],
        house_json['site'],
        house_json['rooms'],
        house_json['area'],
        house_json['price'],
        house_json['floor'],
        house_json['repair'],
        house_json['bilding_year'],
        house_json['addres']
    ]
    await message.reply(f"Вот что удалось собрать👀:\n\n{row}")
    sheet_answer = write_row_sheets(row)
    await message.reply(f"{sheet_answer}✅")
    logger.info(f"Данные сайта {house_json['site']} сохранены в таблицу")
    logger.debug(f"Processed message from {message.chat.id}, short URL: {house_json['url']}")

# Основная функция запуска бота
async def main():
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())