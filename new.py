from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = ''

session = VkApi(token = TOKEN)

longpoll = VkBotLongPoll(session, 198731493)

api = session.get_api()

def id_to_name(id):
	answ = api.users.get(user_ids=id,fields='first_name,last_name')
	return answ[0]['first_name'],answ[0]['last_name']

def message_handler(object):
	if object.type == VkBotEventType.MESSAGE_NEW:
		if object.message['action']: #todo: action == chat_invite_user
			print('[ADD] Added to a chat')
		else:
			print('[NEW] Message')
			f,l = id_to_name(object.message.from_id)
			print('[FROM] {} {}'.format(f,l))
			print('[TEXT] {}'.format(object.message.text))

def leave_join_handler(object):
	if object.type == VkBotEventType.GROUP_JOIN:
		print('Smone joined')

for event in longpoll.listen():
	if event.type == VkBotEventType.MESSAGE_NEW or VkBotEventType.MESSAGE_REPLY or VkBotEventType.MESSAGE_TYPING_STATE:
		message_handler(event)
	elif event.type == VkBotEventType.GROUP_JOIN or VkBotEventType.GROUP_LEAVE:
		leave_join_handler(event)
	else:
		print(event.type)
		print('unknow handler')