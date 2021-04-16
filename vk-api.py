from vkwave.bots import SimpleLongPollBot
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from loguru import logger
import tgfuncs
import asyncio

# 1779702753:AAFPtwDg98ir8CK6f-2HVOky0rcSTeDtheE
# 9e8b113868e44cd7ea23716f7b4e4bc1d2f90a33c953d22c49a828995a6b95b196190c5588ea3b31f
# 198731493

logger.info('Started')

bot = Bot(token='1779702753:AAFPtwDg98ir8CK6f-2HVOky0rcSTeDtheE')
logger.debug('Telegram: got api')

dp = Dispatcher(bot)
tgfuncs.setup_handlers(dp)
logger.debug('Telegram: dispachers ready')

bot = SimpleLongPollBot(tokens="9e8b113868e44cd7ea23716f7b4e4bc1d2f90a33c953d22c49a828995a6b95b196190c5588ea3b31fd074", group_id=198731493)
logger.debug('VKAPI: registered bot')

@bot.message_handler()
async def handle(event: bot.SimpleBotEvent):
    await event.answer("hello world!")

logger.debug('VKAPI: handlers ready')

def start():
    executor.start_polling(dp)
    logger.debug('Polling Telegram')
    bot.run_forever()
    logger.debug('Polling vk')
start()
