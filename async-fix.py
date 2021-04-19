from vkwave.bots import SimpleLongPollBot
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from loguru import logger
import asyncio
import tgfuncs

import confs
c = confs.Config()
c.unlock_file('')

logger.info('Started')

bot = Bot(token=c.data['tg']['token'])
logger.debug('Telegram: got api')

dp = Dispatcher(bot)
tgfuncs.setup_handlers(dp)

logger.debug('Telegram: dispachers ready')
bot2 = SimpleLongPollBot(tokens=c.data['vk']['public_token'], group_id=c.data['vk']['public_id'])
logger.debug('VKAPI: registered bot')

@bot2.message_handler()
async def handle(event: bot2.SimpleBotEvent):
    usr_id = event.object.object.message.from_id #event.object.object.message.from_id
    answer = await event.api_ctx.users.get(user_ids=usr_id,fields='first_name,last_name')
    f,l = answer.response[0].first_name, answer.response[0].last_name
    notification_text = f'Новое сообщение ВКонтакте от пользователя {f} {l}\nТекст сообщения: {event.object.object.message.text}'
    logger.debug(f'New message from VK: {f} {l}')
    await bot.send_message(tg_id, notification_text)

logger.debug('VKAPI: handlers ready')

async def start_polling_vk():
    await bot2.run()
    logger.debug('Polling Vk')

dp.loop.create_task(start_polling_vk())
logger.debug('Polling Telegram')
executor.start_polling(dp, skip_updates=True)
