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

async def register():
	await msg.answer()

async def anything(msg: Message):
	logger.info(f"{msg.from_user.full_name} send something. idk")
	await msg.answer(msg.text)

def setup_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(help, commands=['help'])
    dp.register_message_handler(register, commands=['register'])
    dp.register_message_handler(anything)
