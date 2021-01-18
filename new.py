from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = ''
PEER_CONST = 2000000000
GROUP_ID = 198731493

session = VkApi(token = TOKEN)

longpoll = VkBotLongPoll(session, GROUP_ID)

api = session.get_api()

def id_to_name(id):
	answ = api.users.get(user_ids=id,fields='first_name,last_name')
	return answ[0]['first_name'],answ[0]['last_name']

def chat_id_to_name(id):
	answ = api.messages.getConversationsById(peer_ids=id,group_id=GROUP_ID)
	return answ['items'][0]['chat_settings']['title']

def message_handler(object):
	if object.type == VkBotEventType.MESSAGE_NEW:
		print(dir(object))
		if object.message['action']: #todo: action == chat_invite_user
			print('[ADD] inChat')
		else:
			print('[NEW] Private message')
			f,l = id_to_name(object.message.from_id)
			print('[FROM] {} {}'.format(f,l))
			print('[TEXT] {}'.format(object.message.text))
	elif object.type == VkBotEventType.MESSAGE_NEW and object.from_chat:
		print('[NEW] Message inChat')
		f,l = id_to_name(object.message.from_id)
		print('[FROM] {} {}'.format(f,l))
		print('[CHAT] ID {}'.format(event.chat_id))
		print('[TEXT] {}'.format(event.text))

def chat_message_handler(object):
	print('[NEW] Chat message: {}'.format(chat_id_to_name(object.message.peer_id)))
	f,l = id_to_name(object.message.from_id)
	print('[FROM] {} {}'.format(f,l))
	print('[TEXT] {}'.format(event.message.text))

def private_message_handler(object):
	print('[NEW] Private message')
	f,l = id_to_name(object.message.from_id)
	print('[FROM] {} {}'.format(f,l))
	print('[TEXT] {}'.format(event.message.text))

def leave_join_handler(object):
	if object.type == VkBotEventType.GROUP_JOIN:
		print('Smone joined')

if __name__ == '__main__':
	for event in longpoll.listen():
		if event.type == VkBotEventType.MESSAGE_NEW:
			if event.message.peer_id > 2000000000:
				chat_message_handler(event)
			else:
				private_message_handler(event)
		elif event.type == VkBotEventType.GROUP_JOIN or VkBotEventType.GROUP_LEAVE:
			leave_join_handler(event)
		else:
			print(event.type)
			print('unknow handler')