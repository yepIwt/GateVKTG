import os
import ast
from .crypt import LetItCrypt
from vk_api import VkApi
import vk_api.exceptions
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

PEER_CONST = 2000000000

class Config(object):

    __slots__ = ('crypter','data','vk_api','tg_api','tg_dispatcher','longpoll')

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

    def get_vk_convs(self, convs: list, offset: int) -> list:
        api_answ = self.vk_api.messages.getConversations(offset=offset,count=200,filter='all',group_id=self.data['vk']['public_id'])
        if api_answ['items']:
            for it in answ['items']:
                convs.append(it['conversation']['peer']['id'])
            self.get_vk_convs(convs,200)
        self.data['vk']['conversations'] = convs
        return convs

    def get_tg_api(self, token = None, tg_handler_func_name = None):
        if not token:
            token = self.data['tg']['token']
        up = Updater(token, use_context = True)
        self.tg_dispatcher = up.dispatcher
        self.tg_dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, tg_handler_func_name))
        return up

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
