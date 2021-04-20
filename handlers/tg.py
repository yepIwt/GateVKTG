import confs
from loguru import logger
from aiogram.types import Message
from aiogram import Dispatcher

async def start_cmd(msg: Message):
	logger.info(f"{msg.from_user.full_name} send /start")
	await msg.answer("Basic reply")

async def help(msg: Message):
	logger.info(f"{msg.from_user.full_name} send /help")
	await msg.answer('This is gate')

async def notif(msg: Message):
	args = msg.text.split(' ') # args = ['/notif', 'id']
	if len(args) != 1:
		if args[1] == 'me':
			await msg.answer('you? ok')
		else:
			try:
				new_notif = int(args[1])
			except:
				await msg.answer('bad syntax')
			else:
				await msg.answer(f'new notifer - {new_notif}')
	else:
		await msg.answer('tekushii')

async def anything(msg: Message):
	logger.info(f"{msg.from_user.full_name} send something. {msg['from']['id']} idk")
	await msg.answer(msg.text)

def setup_tg_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(help, commands=['help'])
    dp.register_message_handler(notif, commands=['notif'])
    dp.register_message_handler(anything)
