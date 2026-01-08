from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile
from aiogram.client.default import DefaultBotProperties

from settings import TELEGRAM_BOT_ACCESS_TOKEN


async def main() -> None:
    # chat_id = need to be taken from bot
    # message = file
    text_file = BufferedInputFile(b"Hello, world!", filename="file.txt")

    # async with Bot(
    #     token=TELEGRAM_BOT_ACCESS_TOKEN,
    #     default=DefaultBotProperties(
    #         parse_mode=ParseMode.HTML,
    #     ),
    # ) as bot:
    #     await bot.send_message(chat_id=chat_id, text=message)