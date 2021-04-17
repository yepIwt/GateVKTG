from vkwave.bots import SimpleLongPollBot
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from loguru import logger
import asyncio
import tgfuncs

logger.info('Started')

bot = Bot(token='')
logger.debug('Telegram: got api')

dp = Dispatcher(bot)
tgfuncs.setup_handlers(dp)

logger.debug('Telegram: dispachers ready')
bot2 = SimpleLongPollBot(tokens="", group_id=)
logger.debug('VKAPI: registered bot')

@bot2.message_handler()
async def handle(event: bot2.SimpleBotEvent):
    await event.answer("hello world!")

logger.debug('VKAPI: handlers ready')

def start_polling_tg():
    executor.start_polling(dp)
    logger.debug('Polling Telegram')

async def start_polling_vk():
    await bot2.run()
    logger.debug('Polling Vk')

dp.loop.create_task(start_polling_vk())
executor.start_polling(dp, skip_updates=True)
