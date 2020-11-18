#   FakeDude01
#   Это база.
#   (Оно даже запускается)

bot_token = ""

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

class Bot:
    __slots__ = ('api', 'session',"convs")
    
    def __init__(self, token):
        self.session = vk_api.VkApi(token=token)
        self.api = self.session.get_api()
        self.convs = []
    
    def get_fulname(self,id):
        name = self.api.users.get(user_ids=id)
        fulname = name[0]['first_name'] + ' ' + name[0]['last_name']
        return fulname

    def poll(self):
        longpoll = VkBotLongPoll(self.session, 198731493)
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                man = self.get_fulname( event.message.from_id )
                print( "Новое сообщение от {}:".format(man))
                print(event.message.text)
b = Bot(bot_token)
b.poll()