from vk_api import VkApi
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

def get_api_not_async(token, group_id) -> tuple:
	session = VkApi(token=token)
	longpoll = VkBotLongPoll(session,group_id)
	api = session.get_api()
	return (longpoll, api)

def get_api(token, group_id):
	pass

def id_to_name(api: VkApi, id: int, is_pub: bool):
	if is_pub:
		answ = api.groups.getById(group_id=id)
		return answ[0]['name']
	answ = api.users.get(user_ids=id,fields='first_name,last_name')
	return (answ[0]['first_name'], answ[0]['last_name'])

def peer_id_to_title(api,id,group_id):
	answ = api.messages.getConversationsById(peer_ids=id,group_id=group_id)
	return answ['items'][0]['chat_settings']['title']

def get_vk_convs(api: VkApi, group_id: int): # TICKET1: Max 200 convs
	answ = api.messages.getConversations(count=200, group_id=group_id)['items']
	list = []
	for conv in answ:
		typ = conv['conversation']['peer']['type']
		id = conv['conversation']['peer']['id']
		list.append((0 if typ == 'user' else 1,id))
	return list
