import confs
from loguru import logger
from aiogram.types import Message
from aiogram import Dispatcher

CONFIG_OBJ = None

def config_tg_hand(c = None):
	global CONFIG_OBJ
	if not c:
		return CONFIG_OBJ
	CONFIG_OBJ = c

async def start_cmd(msg: Message):
	logger.info(f"{msg.from_user.full_name} send /start")
	await msg.answer("Basic reply")

async def help(msg: Message):
	logger.info(f"{msg.from_user.full_name} send /help")
	await msg.answer('This is gate')

async def notif(msg: Message):
	global CONFIG_OBJ
	args = msg.text.split(' ') # args = ['/notif', 'id']
	if len(args) != 1:
		if args[1] == 'me':
			answer = f"Changed notificator id: {str(CONFIG_OBJ['tg']['notificate_to'])} ---> {msg.from_user.id}"
			logger.debug(f'{msg.from_user.id}: {answer}')
			CONFIG_OBJ['tg']['notificate_to'] = msg.from_user.id
			await msg.answer(answer)
		else:
			try:
				new_notif = int(args[1])
			except:
				await msg.answer('bad syntax')
			else:
				answer = f"Changed: {str(CONFIG_OBJ['tg']['notificate_to'])} ---> {new_notif}"
				await msg.answer(answer)
				logger.debug(f'{msg.from_user.id}: {answer}')
				CONFIG_OBJ['tg']['notificate_to'] = new_notif
	else:
		await msg.answer(str(CONFIG_OBJ['tg']['notificate_to']))

async def anything(msg: Message):
	logger.info(f"{msg.from_user.full_name} send something. {msg['from']['id']} idk")
	await msg.answer(msg.text)

def setup_tg_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(help, commands=['help'])
    dp.register_message_handler(notif, commands=['notif'])
    dp.register_message_handler(anything)
