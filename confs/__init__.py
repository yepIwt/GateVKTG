import os
import ast
from .crypt import LetItCrypt
from vk_api import VkApi
from Crypto.Cipher import DES
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

PEER_CONST = 2000000000

class Config(object):

    __slots__ = ('crypter','data','vk_api','tg_token','longpoll')

    def __init__(self,passw):
        self.crypter = LetItCrypt(passw)
        if not os.path.exists('data'):
            self.new_cfg()
        config_as_str = self.crypter.dec()
        self.data = ast.literal_eval(config_as_str)
        self.__get_api_vk(self.data['vk']['vk_token'], self.data['vk']['group_id'])
        self.data['vk']['convers'] = self.__get_vk_conversations(self.data['vk']['group_id'],[],0)
        print(self.data)

    def __get_api_vk(self,token: str,group_id: int) -> None:
        session = VkApi(token=token)
        self.longpoll = VkBotLongPoll(session,group_id)
        self.vk_api = session.get_api()
    
    def __get_vk_conversations(self, gid: int, convs: list, offset: int):
        answ = self.vk_api.messages.getConversations(offset=offset,count=200,filter='all',group_id=gid)
        if answ['items']:
            for it in answ['items']:
                convs.append(it['conversation']['peer']['id'])
            self.__get_vk_conversations(gid,convs,200)
        return convs

    def new_cfg(self):
        vk_token = input('Введите токен для vk_api (vk admin token): ')
        group_id = input('Введите id группы: ')
        tg_token = input('Введите токен от телеграмм бота: ')
        new_config = {
            'vk':{
                'vk_token': vk_token,
                'group_id': group_id,
                'convers':[],
                'chats':[],
            },
            'tg':{
                'tg_token': tg_token,
            }
        }
        self.crypter.enc(str(new_config))

    def save_in_file(self) -> None:
        self.crypter.enc(str(self.data))
        config_as_str = self.crypter.dec()
        self.data = ast.literal_eval(config_as_str)