import confs
import requests
import vkwave.bots
from loguru import logger
import moviepy.editor as mp
from aiogram import Dispatcher
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

async def notif(msg: Message):
	global CONFIG_OBJ
	args = msg.text.split(' ') # args = ['/notif', 'id']
	if len(args) == 1:	
		await msg.answer(f"Сейчас я уведомляю сюда - {CONFIG_OBJ['tg']['notificate_to'] or 'никуда блин'}")
	else:
		if args[1] == 'me':
			CONFIG_OBJ['tg']['notificate_to'] = msg.from_user.id
			answer = "Я уведомлю вас!"
			logger.debug(answer)
			await msg.answer(answer)
		else:
			try:
				new_notif = int(args[1])
			except:
				await msg.answer('Как я тебе строчку в число переведу?')
			else:
				CONFIG_OBJ['tg']['notificate_to'] = new_notif
				await msg.answer(f"Я буду отсылать уведомления на этот адрес - {new_notif}!")

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

def get_conv_or_chat_by_id(is_conv: bool, id: int):
	if is_conv:
		try:
			conv = CONFIG_OBJ['vk']['conversations'][id]
		except KeyError:
			return None
		else:
			return conv
	else:
		try:
			chat = CONFIG_OBJ['vk']['chats'][id]
		except KeyError:
			return None
		else:
			return chat

def right_args_syntax(args: list):
	try:
		arg = int(args[2])
	except KeyError:
		return None
	else:
		return arg

async def vk_hand(msg: Message): # Обработчик команд для Вконтакте
	global CONFIG_OBJ, VK_BOT

	args = msg.text.split(' ') # /v conv 1 OR /v chats
	if len(args) == 1:
		await msg.answer('Неправильный синтаксис')

	elif args[1] == 'chats':
		string = ''
		for n, peer in enumerate(CONFIG_OBJ['vk']['chats']):
			chat_title = await get_vk_chat_title(peer)
			string += f'{n+1}: {chat_title}\n'
		await msg.answer(string or 'Нет чатов') 

	elif args[1] == 'convs':
		CONFIG_OBJ['vk']['conversations'] = await get_vk_convs()
		string = ""
		for i, man in enumerate(CONFIG_OBJ['vk']['conversations']):
			string += f'{i+1}: {man[1]} {man[2]}\n'
		await msg.answer(string or 'Нет диалогов')

	elif args[1] == 'conv':
		if not right_args_syntax(args):
			await msg.answer('Неправильный синтаксис')
		else:
			conv = get_conv_or_chat_by_id(is_conv = True, id = int(args[2]) - 1) # /v conv 1 ## 1 is args[2]
			if not conv:
				await msg.answer('Текущий диалог не найден')
			else:
				CONFIG_OBJ['currentConv'] = conv # Установлен новый текущий чат
				current_conv = current_shen(is_conv = True) 
				f,l = current_conv[1], current_conv[2] # Имя, Фамилия = Текущий конверсейшен
				await change_current_title(chat = False, title = f'{f} {l}')
				await set_tg_pic(conv[0]) # Поставить аватарку
				logger.debug(f'Текущий конверсейшен: {f} {l}')

	elif args[1] == 'chat':
		if not right_args_syntax(args):
			await msg.answer('Неправильный синтаксис')
		else:
			chat = get_conv_or_chat_by_id(is_conv = False, id = int(args[2]) - 1) # /v chat 1 ## 1 is args[2]
			if not chat:
				await msg.answer('Такой чат не найден')
			else:
				CONFIG_OBJ['currentChat'] = chat
				chat_title = await get_vk_chat_title(chat)
				await change_current_title(chat = True, title = chat_title)
				logger.debug(f'Текущий чатейшен: {chat_title}')

	else:
		await msg.answer('Упс.. Что-то пошло не так')

async def tg_register(msg: Message):
	global CONFIG_OBJ

	args = msg.text.split(' ') # /tg_reg chat OR /tg_reg conv
	if len(args) == 1:
		await msg.answer('Неправильный синтаксис')
	else:
		if msg.chat.type == 'group' or 'supergroup':
			if args[1] == 'chat':
				await msg.answer(f'{msg.chat.title} зарегистрирован как чатейшен')
				CONFIG_OBJ['tg']['chat_id'] = msg.chat.id
			elif args[1] == 'conv':
				await msg.answer(f'{msg.chat.title} зарегистрирован как конверсейшен')
				CONFIG_OBJ['tg']['conv_id'] = msg.chat.id
			else:
				msg.answer('Неправильный синтаксис')
		else:
			msg.answer('Для регистрации необходим ЧАТ')

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

def setup_tg_handlers(dp: Dispatcher):
	dp.register_message_handler(start_cmd, commands=['start'])
	dp.register_message_handler(help_cmd, commands=['help'])
	dp.register_message_handler(current_cmd, commands=['current'])
	dp.register_message_handler(notif, commands=['notif'])
	dp.register_message_handler(vk_hand, commands=['v'])
	dp.register_message_handler(tg_register, commands=['tg_reg'])
	dp.register_message_handler(anything, content_types=['photo','document','animation','text'])