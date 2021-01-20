import confs
from vk_api.bot_longpoll import VkBotEventType
from vk_api.utils import get_random_id

PEER_CONST = 2000000000

class Functions(object):

	__slots__ = ('api')

	def __init__(self,api_object):
		self.api = api_object

	def id_to_name(self,id):
		answ = self.api.users.get(user_ids=id,fields='first_name,last_name')
		return answ[0]['first_name'],answ[0]['last_name']

	def id_to_name_group(self,id):
		answ = self.api.groups.getById(group_id=id)
		return answ[0]['name'].split(' ')

	def peer_id_to_title(self,id,group_id):
		answ = self.api.messages.getConversationsById(peer_ids=id,group_id=group_id)
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


	def get_message_history(self,peer_id: int):
		answ = self.api.messages.getHistory(peer_id=peer_id)
		objs = []
		for message in answ['items']:
			msid = message['id']
			uid = message['from_id']
			if uid < 0:
				f,l = self.id_to_name_group(uid)
			else:
				f,l = self.id_to_name(uid)
			text = message['text']
			objs.append('{}:{} | {} {}: {}'.format(msid, uid, f, l, text ))
		return objs

class VkObject(object):

	__slots__ = ('config','funcs')

	def __init__(self):
		self.config = confs.Config('password')
		self.funcs = Functions(self.config.api)

		for event in self.config.longpoll.listen():
			if event.type == VkBotEventType.MESSAGE_NEW:
				if event.message.peer_id > 2000000000:
					if event.message.peer_id not in self.config.data['chats']:
						self.config.data['chats'].append(event.message.peer_id)
						print('[LOG] Created new chat')
					self.chat_message_handler(event)
				else:
					if event.message.peer_id not in self.config.data['convers']:
						self.config.data['convers'].append(event.message.peer_id)
						print('[LOG] Created new conversation')
					self.private_message_handler(event)
					
			elif event.type == VkBotEventType.MESSAGE_TYPING_STATE:
				f,l = self.funcs.id_to_name(event.object.from_id)
				print('[LOG] {} {} typing...'.format(f,l))
			else:
				print(event.type)

	def send_message(self, message_text: str, peer_id: int):
		self.config.api.messages.send(message=message_text,peer_id=peer_id,random_id=get_random_id())

	def chat_message_handler(self,object):
		print('[NEW] Chat message: {}'.format(self.funcs.peer_id_to_title(object.message.peer_id,self.config.data['group_id'])))
		f,l = self.funcs.id_to_name(object.message.from_id)
		print('[FROM] {} {}'.format(f,l))
		if object.message['text']:
			print('[TEXT] {}'.format(object.message.text))
		if object.message['attachments']:
			for a in self.funcs.attachments_handler(object):
				print(a)
		self.send_message('Получил сообщение из беседы',object.message.peer_id)
		self.config.save_in_file()

	def private_message_handler(self,object):
		print('[NEW] Private message')
		f,l = self.funcs.id_to_name(object.message.from_id)
		print('[FROM] {} {}'.format(f,l))
		if object.message['text']:
			print('[TEXT] {}'.format(object.message.text))
		if object.message['attachments']:
			for a in self.funcs.attachments_handler(object):
				print(a)
		self.config.save_in_file()

VkObject()