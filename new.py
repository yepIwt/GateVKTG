from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

TOKEN = ''

session = VkApi(token = TOKEN)

longpoll = VkBotLongPoll(session, 198731493)

for event in longpoll.listen():
	if event.type == VkBotEventType.MESSAGE_NEW:
		pass
	elif event.type == VkBotEventType.MESSAGE_REPLY:
		pass