from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

TOKEN = ''
PEER_CONST = 2000000000
GROUP_ID = 198731493

class Functions(object):

	__slots__ = ('api')

	def __init__(self,api_object):
		self.api = api_object

	def id_to_name(self,id):
		answ = self.api.users.get(user_ids=id,fields='first_name,last_name')
		return answ[0]['first_name'],answ[0]['last_name']

	def peer_id_to_title(self,id):
		answ = self.api.messages.getConversationsById(peer_ids=id,group_id=GROUP_ID)
		return answ['items'][0]['chat_settings']['title']

	def attachments_handler(self,event):
		ats = []
		for attach in event.message['attachments']:
			type = attach['type']
			f,l = self.id_to_name(attach[type]['owner_id'])
			owner_attachment = f + ' ' + l
			if type == 'photo':
				file_url = attach[type]['sizes'][-1]['url']
				file_name = 'photo_file'
			else:
				file_url = attach[type]['url']
				file_name = attach[type]['title']
			pkg = {
				'a_type': type,
				'a_owner': owner_attachment,
				'f_name': file_name,
				'f_url': file_url,
			}
			ats.append(pkg)
		return ats

class VkObject(object):

	__slots__ = ('longpoll','api','funcs')

	def __init__(self,token,group_id):
		ses = VkApi(token=token)
		self.longpoll = VkBotLongPoll(ses, group_id)
		self.api = ses.get_api()
		self.funcs = Functions(self.api)
		for event in self.longpoll.listen():
			if event.type == VkBotEventType.MESSAGE_NEW:
				if event.message.peer_id > 2000000000:
					self.chat_message_handler(event)
				else:
					self.private_message_handler(event)
			else:
				print(event.type)
				print('unknow handler')

	def send_message(self, message_text: str, peer_id: int):
		self.api.messages.send(message=message_text,peer_id=peer_id,random_id=get_random_id())

	def chat_message_handler(self,object):
		print('[NEW] Chat message: {}'.format(self.funcs.peer_id_to_title(object.message.peer_id)))
		f,l = self.funcs.id_to_name(object.message.from_id)
		print('[FROM] {} {}'.format(f,l))
		if object.message['text']:
			print('[TEXT] {}'.format(object.message.text))
		if object.message['attachments']:
			for a in self.funcs.attachments_handler(object):
				print(a)

	def private_message_handler(self,object):
		print('[NEW] Private message')
		f,l = self.funcs.id_to_name(object.message.from_id)
		print('[FROM] {} {}'.format(f,l))
		if object.message['text']:
			print('[TEXT] {}'.format(object.message.text))
		if object.message['attachments']:
			for a in self.funcs.attachments_handler(object):
				print(a)

VkObject(TOKEN,GROUP_ID)