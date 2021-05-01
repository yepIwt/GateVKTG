import confs
import requests
from vkwave.bots import PhotoUploader # для отправки файлов
from loguru import logger
from aiogram.types import Message
from aiogram import Dispatcher

CONFIG_OBJ = None
VK_BOT = None
TG_API = None

def config_tg_hand(c = None):
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
async def get_vk_convs():
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

async def vk_hand(msg: Message):
	global CONFIG_OBJ, VK_BOT
	args = msg.text.split(' ')
	if len(args) == 1:
		await msg.answer('ne robit')
	elif args[1] == 'chats':
		answ = ''
		for n,peer in enumerate(CONFIG_OBJ['vk']['chats']):
			chat_title = await get_vk_chat_title(peer)
			answ += f'{n+1}: {chat_title}\n'
		await msg.answer(answ or 'no them')
	elif args[1] == 'convs':
		CONFIG_OBJ['vk']['conversations'] = await get_vk_convs()
		krasivaya_stroka = ""
		for i,man in enumerate(CONFIG_OBJ['vk']['conversations']):
			krasivaya_stroka += f'{i+1}. {man[1]} {man[2]}\n'
		await msg.answer(krasivaya_stroka or 'nothing')
	elif args[1] == 'conv':
		if len(args) == 2:
			await msg.answer('bad syntax')
		else:
			try:
				arg = int(args[2])
			except:
				await msg.answer('bad syntax')
			else:
				try:
					conv = CONFIG_OBJ['vk']['conversations'][arg-1]
				except:
					await msg.answer('net takogo conversationa. Try "/v convs"')
				else:
					nf,nl = conv[1],conv[2]
					if not CONFIG_OBJ['currentConv']:
						await msg.answer(f'Current vk conversation setted: {nf} {nl}')
					else:
						f,l = CONFIG_OBJ['currentConv'][1],CONFIG_OBJ['currentConv'][2]
						await msg.answer(f'Current vk conversation changed: {f} {l} --> {nf} {nl}')
					CONFIG_OBJ['currentConv'] = conv
					await change_current_title(0, conv[1]+' '+ conv[2])
					await set_tg_pic(conv[0])
	elif args[1] == 'chat':
		if len(args) == 2:
			await msg.answer('bad syntax')
		else:
			try:
				arg = int(args[2])
			except:
				await msg.answer('bad syntax')
			else:
				try:
					chat = CONFIG_OBJ['vk']['chats'][arg-1]
				except:
					await msg.answer('net takogo chata. Try "/v chats"')
				else:
					ntitle = await get_vk_chat_title(chat)
					if not CONFIG_OBJ['currentChat']:
						await msg.answer(f'Current vk chat now setted: {ntitle}')
					else:
						otitle = await get_vk_chat_title(CONFIG_OBJ['currentChat'])
						await msg.answer(f'Current vk chat changed: {otitle} --> {ntitle}')
					CONFIG_OBJ['currentChat'] = chat
					await change_current_title(1, await get_vk_chat_title(chat))
	else:
		await msg.answer('bad syntax')

async def tg_register(msg: Message):
	global CONFIG_OBJ
	args = msg.text.split(' ')
	if len(args) == 1:
		await msg.answer('ne robit')
	else:
		if args[1] == 'chat':
			if msg.chat.type == 'group' or 'supergroup':
				await msg.answer(f'{msg.chat.title} зарегистрирован как тг-чат')
				CONFIG_OBJ['tg']['chat_id'] = msg.chat.id
			else:
				await msg.answer('мне нужен чат1!!!!!!!!!!')
		elif args[1] == 'conv':
			if msg.chat.type == 'group' or 'supergroup':
				await msg.answer(f'{msg.chat.title} зарегистрирован как тг-конв')
				CONFIG_OBJ['tg']['conv_id'] = msg.chat.id
			else:
				await msg.answer('мне нужен чат1!!!!!!!!!!')
		else:
			await msg.answer('bad syntax')

async def catch_attachments(msg,peer_id):
	global TG_API,VK_BOT
	if msg.photo:
		logger.debug('Catched pic from tg')
		await TG_API.download_file_by_id(msg.photo[-1].file_id,'photo.jpg') #ticket: пока только одно вложение
		vk_uploader = PhotoUploader(VK_BOT.api_context)
		attachment_info = await vk_uploader.get_attachment_from_path(peer_id,'photo.jpg')
		return attachment_info
	else:
		logger.debug('Tried to catch attachments. No them.')
		return None

async def anything(msg: Message):
	global CONFIG_OBJ,VK_BOT
	if msg.chat.type == 'private':
		await msg.text('не, бро, я только по командам')
	else:
		if msg.chat.id == CONFIG_OBJ['tg']['chat_id']:
			attachs = await catch_attachments(msg,CONFIG_OBJ['currentChat'])
			if attachs:
				msg.text = msg.caption
			await VK_BOT.api_context.messages.send(peer_id=CONFIG_OBJ['currentChat'],random_id=0,message=msg.text,attachment=attachs)
			logger.info(f"{msg.from_user.full_name} send {msg.text} в текущую беседу")
		elif msg.chat.id == CONFIG_OBJ['tg']['conv_id']:
			attachs = await catch_attachments(msg,CONFIG_OBJ['currentConv'][0])
			if attachs:
				msg.text = msg.caption
			await VK_BOT.api_context.messages.send(user_ids=CONFIG_OBJ['currentConv'][0],random_id=0,message=msg.text,attachment=attachs)
			logger.info(f"{msg.from_user.full_name} send {msg.text} в текущему человеку")
		else:
			await msg.answer('ты чего тут забыл')

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
	dp.register_message_handler(help, commands=['help'])
	dp.register_message_handler(notif, commands=['notif'])
	dp.register_message_handler(vk_hand, commands=['v'])
	dp.register_message_handler(tg_register, commands=['tg_reg'])
	dp.register_message_handler(anything, content_types=['photo','text'])
