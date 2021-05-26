import confs
import requests
import vkwave.bots
from loguru import logger
import moviepy.editor as mp
from aiogram import Dispatcher, types
from aiogram.types import Message

START_MSG = 'Привет!\nЯ нужен для отправки сообщений из Вконтакте и Телеграма.\n*Связист*, проще говоря :)'
HELP_MSG = 'Прежде чем задавать свой вопрос прочтите [документацию](https://github.com/yepIwt/GateVKTG/blob/master/README), меня можно найти [здесь](https://t.me/morphine4life)'

CONFIG_OBJ = None
VK_BOT = None
TG_API = None

def config_tg_hand(c: confs.Config = None):
	global CONFIG_OBJ
	if not c:
		return CONFIG_OBJ
	CONFIG_OBJ = c

def setup_tg_api(tg_bot):
	global TG_API
	TG_API = tg_bot

def setup_vk_bot_to_tg_handler(bot):
	global VK_BOT
	VK_BOT = bot

def current_shen(is_conv: bool): # Текущий конверсейшен или чатейшен
	global CONFIG_OBJ
	if is_conv:
		conv = CONFIG_OBJ['currentConv']
		if not conv:
			return None
		return conv
	chat = CONFIG_OBJ['currentChat']
	if not chat:
		return None
	return chat

async def start_cmd(msg: Message):
	CONFIG_OBJ['tg']['notificate_to'] = msg.from_user.id
	await msg.answer(START_MSG, parse_mode = 'Markdown')

async def help_cmd(msg: Message):
	await msg.answer(HELP_MSG, parse_mode = 'Markdown', disable_web_page_preview=1)

async def current_cmd(msg: Message):
	current_conv = current_shen(is_conv = True)
	if current_conv:
		current_conv = f'{current_conv[1]} {current_conv[2]}'
	current_chat = current_shen(is_conv = False)
	if current_chat:
		current_chat = await get_vk_chat_title(current_chat)
	message = f"Текущий диалог: *{current_chat or 'Нет текущего'}*\nТекущий чат: *{current_conv or 'Нет текущего'}*"
	await msg.answer(message, parse_mode = 'Markdown')

async def get_vk_convs(): # Получить Вконтакте диалоги
	global CONFIG_OBJ, VK_BOT
	n = []
	result = await VK_BOT.api_context.messages.get_conversations()
	for conv in result.response.items:
		result2 = await VK_BOT.api_context.users.get(user_ids=conv.conversation.peer.id, fields='first_name,last_name')
		f,l = result2.response[0].first_name,result2.response[0].last_name
		n.append([conv.conversation.peer.id,f,l])
	return n

async def get_vk_chat_title(peer):
	global VK_BOT
	result = await VK_BOT.api_context.messages.get_conversations_by_id(peer_ids=peer) #разумнее делать один апи запрос на миллиард peer
	return result.response.items[0].dict()['chat_settings']['title']

async def change_current_title(chat: bool, title: str):
	global TG_API,CONFIG_OBJ
	if chat:
		await TG_API.set_chat_title(CONFIG_OBJ['tg']['chat_id'],title)
	else:
		await TG_API.set_chat_title(CONFIG_OBJ['tg']['conv_id'],title)

async def vk_chats(msg: Message):
	global CONFIG_OBJ, VK_BOT
	keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
	text_and_data = await prepare_data_for_inline(is_conv = False)
	row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
	keyboard_markup.row(*row_btns)
	msg_text = 'Выберите чат'
	if not text_and_data:
		msg_text = 'У вас нет чатов'
	await msg.reply(msg_text, reply_markup=keyboard_markup)

async def vk_convs(msg: Message):
	keyboard_markup = types.InlineKeyboardMarkup(row_width=3)
	text_and_data = await prepare_data_for_inline(is_conv = True)
	row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
	keyboard_markup.row(*row_btns)
	msg_text = 'Выберите диалог'
	if not text_and_data:
		msg_text = 'У вас нет диалогов'
	await msg.reply(msg_text, reply_markup=keyboard_markup)

async def chat_register(msg: Message):
	if msg.chat.type != 'private':
		await msg.answer(f'{msg.chat.title} зарегистрирован как чатейшен')
		CONFIG_OBJ['tg']['chat_id'] = msg.chat.id
	else:
		await msg.answer('Для этой команды поддерживается только чат')

async def conv_register(msg: Message):
	print(msg.chat.type)
	if msg.chat.type != 'private':
		await msg.answer(f'{msg.chat.title} зарегистрирован как конверсейшен')
		CONFIG_OBJ['tg']['conv_id'] = msg.chat.id
	else:
		await msg.answer('Для этой команды поддерживается только чат')

async def catch_attachments(msg,peer_id):
	global TG_API,VK_BOT
	if msg.photo:
		file_id = msg.photo[-1].file_id
		file_name = 'photo.jpg'
		uploader = vkwave.bots.PhotoUploader(VK_BOT.api_context)
	elif msg.animation:
		await TG_API.download_file_by_id(msg.animation.file_id,'animation.mp4')
		clip = mp.VideoFileClip('animation.mp4')
		clip.write_gif('animation.gif',logger=None)
		uploader = vkwave.bots.DocUploader(VK_BOT.api_context)
		return await uploader.get_attachment_from_path(peer_id, 'animation.gif')
	elif msg.document:
		file_id = msg.document.file_id
		file_name = msg.document.file_name
		uploader = vkwave.bots.DocUploader(VK_BOT.api_context)
	else:
		return None
	await TG_API.download_file_by_id(file_id, file_name) #ticket: https://bit.ly/3tsrbp6
	return await uploader.get_attachment_from_path(peer_id, file_name)

async def send_message_in_vk(is_conv: bool, message_object: Message):
	global CONFIG_OBJ, VK_BOT

	if is_conv:
		id = CONFIG_OBJ['currentConv'][0]
	else:
		id = CONFIG_OBJ['currentChat']

	attachs = await catch_attachments(message_object, id)
	if attachs:
		message_object.text = message_object.caption
	await VK_BOT.api_context.messages.send(
		peer_id=id,
		random_id=0,
		message=message_object.text or ' ',
		attachment=attachs
	)
	return attachs

async def anything(msg: Message):
	global CONFIG_OBJ,VK_BOT
	if msg.chat.type == 'private':
		await msg.answer('<i>Связист не похож на человека...</i>\nКомандуйте!',parse_mode = 'HTML')
	else:
		if msg.chat.id == CONFIG_OBJ['tg']['chat_id']:
			was_some_attachments = await send_message_in_vk(is_conv = False, message_object = msg)
			logger.info(f"Sent {msg.text or 'Вложение без подписи'} в текущую беседу. Вложения: {was_some_attachments or 'нет'}")

		elif msg.chat.id == CONFIG_OBJ['tg']['conv_id']:
			was_some_attachments = await send_message_in_vk(is_conv = True, message_object = msg)
			logger.info(f"Sent {msg.text or 'Вложение без подписи'} текущему человеку. Вложения: {was_some_attachments or 'нет'}")

		else:
			await msg.answer('<i>Не помню что бы я такой чат помнил...</i>', parse_mode = 'HTML')

async def get_vk_conv_avatar(id):
	global VK_BOT
	answer = await VK_BOT.api_context.users.get(user_ids=id,fields="photo_max_orig")
	url = answer.response[0].photo_max_orig
	r = requests.get(url)
	f = open('conv.jpg','wb')
	f.write(r.content)
	f.close()

async def set_tg_pic(id: int):
	global TG_API, CONFIG_OBJ
	await get_vk_conv_avatar(id)
	f = open('conv.jpg','rb')
	await TG_API.set_chat_photo(CONFIG_OBJ['tg']['conv_id'],f)

async def prepare_data_for_inline(is_conv: bool):
	n = []
	if is_conv:
		CONFIG_OBJ['vk']['conversations'] = await get_vk_convs()
		for i,conv_obj in enumerate(CONFIG_OBJ['vk']['conversations']):
			perfect_username = '{}. {}'.format(conv_obj[1][0], conv_obj[2])
			n.append(
				(perfect_username,i) 
			)
	else:
		for _,chat_peer in enumerate(CONFIG_OBJ['vk']['chats']):
			perfect_title = await get_vk_chat_title(chat_peer)
			n.append(
				(perfect_title,chat_peer)
			)
	return n

async def get_conv_or_chat_from_callback(is_conv: bool, data: str):
	global CONFIG_OBJ
	if is_conv:
		try:
			return CONFIG_OBJ['vk']['conversations'][int(data)]
		except:
			return False
	try:
		n =  CONFIG_OBJ['vk']['chats'].index(int(data))
		return CONFIG_OBJ['vk']['chats'][n]
	except:
		return False

async def callback_handler(qr: types.CallbackQuery):
	global TG_API, CONFIG_OBJ
	new_conv = await get_conv_or_chat_from_callback(is_conv = True, data = qr.data)
	if new_conv != False:
		msg = 'Текущий диалог - {} {}'.format(new_conv[1],new_conv[2])
		CONFIG_OBJ['currentConv'] = new_conv
		f,l = new_conv[1], new_conv[2]
		await change_current_title(chat = False, title = f'{f} {l}')
		await set_tg_pic(new_conv[0]) # Поставить аватарку
		logger.debug(f'Текущий конверсейшен: {f} {l}')

	new_chat = await get_conv_or_chat_from_callback(is_conv = False, data = qr.data)
	if new_chat != False:
		msg = 'Текущий чат - {}'.format(await get_vk_chat_title(new_chat))
		CONFIG_OBJ['currentChat'] = new_chat
		chat_title = await get_vk_chat_title(new_chat)
		await change_current_title(chat = True, title = chat_title)
		logger.debug(f'Текущий чатейшен: {chat_title}')

	await qr.answer(msg)
	await TG_API.delete_message(chat_id = qr.message.chat.id, message_id = qr.message.message_id)
	await TG_API.delete_message(chat_id = qr.message.chat.id, message_id = qr.message.reply_to_message.message_id)

def setup_tg_handlers(dp: Dispatcher):
	dp.register_message_handler(start_cmd, commands=['start'])
	dp.register_message_handler(help_cmd, commands=['help'])
	dp.register_message_handler(current_cmd, commands=['current'])
	dp.register_message_handler(vk_convs, commands = ['convs'])
	dp.register_message_handler(vk_chats, commands = ['chats'])
	dp.register_message_handler(chat_register, commands=['regchat'])
	dp.register_message_handler(conv_register, commands=['regconv'])
	dp.register_message_handler(anything, content_types=['photo','document','animation','text'])
	dp.register_callback_query_handler(callback_handler,  lambda chosen_inline_query: True)