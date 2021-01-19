import os
import ast
from .crypt import LetItCrypt
from vk_api import VkApi
from Crypto.Cipher import DES
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

PEER_CONST = 2000000000

class Config(object):

    __slots__ = ('crypter','data','api','longpoll')

    def __init__(self,passw):
        self.crypter = LetItCrypt(passw)
        if not os.path.exists('data'):
            self.new_cfg()
        config_as_str = self.crypter.dec()
        self.data = ast.literal_eval(config_as_str)
        self.get_api(self.data['token'], self.data['group_id'])

    def get_api(self,token: str,group_id: int) -> None:
        session = VkApi(token=token)
        self.longpoll = VkBotLongPoll(session,group_id)
        self.api = session.get_api()

   
    def new_cfg(self):
        token = input('Введите токен для vk_api (vk admin token): ')
        group_id = input('Введите id группы: ')
        new_config = {
            'token': token,
            'group_id':group_id,
        }
        self.crypter.enc(str(new_config))

    def save_in_file(self) -> None:
        self.crypter.enc(str(self.data))
        config_as_str = self.crypter.dec()
        self.data = ast.literal_eval(config_as_str)