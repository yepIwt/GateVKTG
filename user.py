#   FakeDude01
#   Это база.
#   (Оно даже запускается)

from vk_api import VkApi
import random

kate_mobile_token = ""
bot_token = ""

ses = VkApi(token=kate_mobile_token)
#ses.auth()
vk = ses.get_api()
convs = vk.messages.getConversations(count=20)
def get_random_id():
    return random.getrandbits(31) * random.choice([-1, 1])
for conv in convs['items']:
    if conv["conversation"]["peer"]["type"] == "chat":
        bid = conv['conversation']['peer']['local_id']
        tit = conv['conversation']['chat_settings']['title']
        print([bid,tit])
print("Введите номер беседы:")
im_id = int(input())

ses_bot = VkApi(token=bot_token)
vk = ses_bot.get_api()

while True:
    message_text = input()
    vk.messages.send(chat_id = im_id,random_id=get_random_id(),message=message_text)