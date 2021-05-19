import os
import ast
from .crypt import LetItCrypt

PEER_CONST = 2000000000

class Config(object):

    __slots__ = ('crypter','data')

    def __init__(self):
        self.crypter = None
        if not os.path.exists('data'):
            self.data = False
        else:
            self.data = True

    def unlock_file(self, passw: str) -> bool:
        self.crypter = LetItCrypt(passw)
        try:
            self.data = self.crypter.dec_cfg()
        except:
            print('Bad password for config')

        if not self.data:
            return False
        else:
            self.data = ast.literal_eval(self.data.decode())
            return True

    def new_cfg(self, passw: int, vk_public_token: int, vk_public_id: int, tg_token: int) -> None:
        #vk_group_token = input('Введите токен для группы vk_api (vk admin token): ')
        #vk_group_id = input('Введите id группы: ')
        #tg_token = input('Введите токен от телеграмм бота: ')
        new_config = {
            'tg':{
                'token' : tg_token,
                'chat_id': None,
                'conv_id': None ,
                'bot_is_admin_in_chats': [0,0], # chat, conv
                'notificate_to': None, #tg id to push from vk
            },
            'vk':{
                'public_token': vk_public_token,
                'public_id': vk_public_id,
                'conversations': [],
                'chats': [],
            },
            'currentChat': None,
            'currentConv': None,
        }
        self.crypter = LetItCrypt(passw)
        self.data = new_config
        self.save_in_file()

    def save_in_file(self) -> None:
        self.crypter.enc_cfg(str(self.data))
        config_as_str = self.crypter.dec_cfg().decode()
        self.data = ast.literal_eval(config_as_str)
