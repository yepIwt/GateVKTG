import os
import confs
import vkfuncs
import tgfuncs
from loguru import logger
from vk_api import VkApi
from threading import Thread
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

PEER_CONST = 2000000000

logger.info('Program started')

config = confs.Config()
logger.debug('Init config')

config.unlock_file('123')
logger.debug('Config unlocked')

token = config.data['vk']['public_token']
group_id = config.data['vk']['public_id']

longpoll, api = vkfuncs.get_api(token, group_id)
logger.debug('Got vk_api')

config.data['vk']['conversations'] = vkfuncs.get_vk_convs(api,group_id)
logger.debug('Updated VK conversations')

bot = Bot(token=config.data['tg']['token'])
logger.debug('Telegram: got api')

dp = Dispatcher(bot)
tgfuncs.setup_handlers(dp)
logger.debug('Telegram: dispachers ready')

def start_polling_tg():
	logger.debug('Polling Telegram')
	executor.start_polling(dp)

def start_polling_vk():
	logger.debug('Polling VK (longpoll)')
	for event in longpoll.listen():
		if event.type is VkBotEventType.MESSAGE_NEW:
			if event.message.peer_id > PEER_CONST:
				chat_name = vkfuncs.peer_id_to_title(api, event.message.peer_id, group_id)
				logger.info(f'[New message] from chat: {chat_name}')

				if event.message.peer_id not in config.data['vk']['chats']:
					config.data['vk']['chats'].append(event.message.peer_id)
					config.save_in_file()
					logger.debug('There is no chat like this in config. Added.')
			else:
				f,l = vkfuncs.id_to_name(api, event.message.peer_id, 0)
				logger.info(f'New message from conv: {f,l}')

if __name__ == '__main__':
	Thread(target = start_polling_vk).start()
	start_polling_tg()
