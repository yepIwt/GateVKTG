#   FakeDude01
#   Это база.
#   (Оно даже запускается)

bot_token = ""
my_id = "" 

from vk_api import audio
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

WALL_LINK = "https://vk.com/wall"

class Bot:

    __slots__ = ('api', 'session',"convs")
    
    def __init__(self, token):
        self.session = vk_api.VkApi(token=token,api_version='5.126')
        self.api = self.session.get_api()

    def get_fulname(self,id):
        name = self.api.users.get(user_ids=id)
        fulname = name[0]['first_name'] + ' ' + name[0]['last_name']
        return fulname

    def attachments_handler(self,obj):
        for attachment in obj:
            if attachment['type'] == "photo":
                file_url = attachment['photo']['sizes'][-1]['url']
                print("Фотка: {}".format(file_url))
            elif attachment['type'] == "wall":
                if attachment['wall']['from_id'] > 0: #Пост от человека
                    user = self.get_fulname(attachment['wall']['from_id'])
                    wall_url = WALL_LINK + str(attachment['wall']['from_id']) + '_' + str(attachment['wall']['id'])
                    print("Это РЭП-пост от пользователя: {}".format(user))
                    print("Сылка на пост: {}".format(wall_url))
                else:
                    public_name = attachment['wall']['from']['name']
                    wall_url = WALL_LINK + str(attachment['wall']['from_id']) + '_' + str(attachment['wall']['id'])
                    print("Это РЭП-ПОСТ из паблика {}".format(public_name))
                    print("Ссылка на пост: {}".format(wall_url))
            elif attachment['type'] == "audio":    #Ticket 1: "Нет получения аудио из сообщений"
                print("Аудио: {} - {}".format(attachment['audio']['artist'],attachment['audio']['title']))
            elif attachment['type'] == 'video': #Ticket 2: "Нет получения видео из сообщений"
                print("Видео - {}".format(attachment['video']['title']))
            elif attachment['type'] == 'doc':
                print("Файл: {}".format(attachment['doc']['title']))
                print("Link - {}".format(attachment['doc']['url']))

    def poll(self):
        longpoll = VkBotLongPoll(self.session, 198731493)
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and int(event.message.from_id) != int(my_id):
                man = self.get_fulname( event.message.from_id)
                print( "Новое сообщение от {}:".format(man))
                if event.message.text:
                    print("Сообщение: {}".format(event.message.text))
                if event.message.attachments:
                    self.attachments_handler(event.message.attachments)
                    
b = Bot(bot_token)
b.poll()