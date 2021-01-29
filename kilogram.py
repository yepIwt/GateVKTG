import logging
import confs
from telegram import Bot
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

class Functions(object):

    __slots__ = ('admin_id','api_messages')

    def get_name(self,obj):
        f = obj.message.to_dict()['from']['first_name']
        l = ''
        if 'last_name' in obj.message.to_dict()['from']:
            l = obj.message.to_dict()['from']['last_name']
        return f,l

    def send_message(self,chat_id, text):
        self.api_messages.send_message(chat_id, text)
        print('[NEW] Message sent.')

    def get_api_messages(self,token):
        self.api_messages = Bot(token)

    def changeTitle(self, chat_id, new_title):
        self.api_messages.setChatTitle(chat_id, new_title)

class TgObject(object):

    __slots__ = ('config','funcs','api_messages')

    def tg_hangler(self, update: Update, context: CallbackContext):
        print(update.message.to_dict())
        if update.message.to_dict()['chat']['type'] == 'private':
            print('[NEW] Private message')
        else:
            title = update['message']['chat']['title']
            print('[NEW] Message from chat: {}'.format(title))
        f,l = self.funcs.get_name(update)
        msg_text = update.message.text
        print('[FROM] {} {}'.format(f,l))
        print('[TEXT] {}'.format(msg_text))

        self.config.save_in_file()
        update.message.reply_text(update.message.text)

    def get_admin(self,update: Update, context: CallbackContext) -> None:
        self.config.data['tg']['admin'] = update.to_dict()['message']['from']['username']
        self.config.save_in_file()
        message_text = '@{} зарагестрирован админом'.format(update.to_dict()['message']['from']['username'])
        update.message.reply_text(message_text)

    def authorize_tg(self, update: Update, context: CallbackContext):
        # /authorize chat 
        # >> TG-CHAT NAME authorized as VK_CHAT_NAME
        # /authorize conv
        # >> TG-CHAT NAME authorized as VK_CONV_NAME
        if not update.message['chat']['type'] == 'group':
            update.message.reply_text('Эту команду нужно писать в  ТГ-ЧАТ')
        else:
            msg = update.message['text'].split(' ')[-1]
            if msg == 'chat':
                update.message.reply_text('Этот чат определен как tg-conv')
                self.config.data['tg']['currChat'][0] = update.message['chat']['id']
            elif msg == 'conv':
                update.message.reply_text('Этот чат определен как tg-chat')
                self.config.data['tg']['currConv'][0] = update.message['chat']['id']
            else:
                update.message.reply_text('Недостаточно аргументов')
        self.config.save_in_file()

    def vk_handler(self, update: Update, context: CallbackContext):
        args = update.message['text'].split(' ')
        if len(args) == 1:
            update.message.reply_text("Недостаточно аргументов")
        else:
            if args[1] == 'chats':
                msg = ""
                for a, chat_id in list(enumerate(self.config.data['vk']['chats'])):
                    chat_title = self.config.vk_api.messages.getConversationsById(peer_ids=chat_id)['items'][0]['chat_settings']['title']
                    msg += '{} - {}\n'.format(a, chat_title)
                update.message.reply_text(msg)
            elif args[1] == 'convs':
                msg = ""
                for a, conv_id in list(enumerate(self.config.data['vk']['convers'])):
                    answ = self.config.vk_api.users.get(user_ids=conv_id, fields='first_name,last_name')
                    conv_title = "{} {}".format(answ[0]['first_name'], answ[0]['last_name'])
                    msg += '{} - {}\n'.format(a, conv_title)
                update.message.reply_text(msg)
            elif args[1] == 'chat':
                if len(args) == 2:
                    update.message.reply_text('Недостаточно аргументов')
                else:
                    self.config.data['tg']['currChat'][1] = self.config.data['vk']['chats'][int(args[2])] # TODO: Выход за пределы массива
                    chat_title = self.config.vk_api.messages.getConversationsById(peer_ids = self.config.data['vk']['chats'][int(args[2])] )['items'][0]['chat_settings']['title']
                    update.message.reply_text('Текущий (настроенный) тг-чат стал {}'.format(chat_title))
            elif args[1] == 'conv':
                if len(args) == 2:
                    update.message.reply_text('Недостаточно аргументов')
                else:
                    self.config.data['tg']['currConv'][1] = self.config.data['vk']['convers'][int(args[2])] # TODO: Выход за пределы массива
                    answ = self.config.vk_api.users.get(user_ids=self.config.data['vk']['convers'][int(args[2])], fields='first_name,last_name')
                    conv_title = "{} {}".format(answ[0]['first_name'], answ[0]['last_name'])
                    update.message.reply_text('Текущий (настроенный) тг-чат стал {}'.format(conv_title))
            self.config.save_in_file()            

    def __init__(self):
        self.config = confs.Config('password')
        self.funcs = Functions()
        self.funcs.get_api_messages(self.config.data['tg']['tg_token'])
        print(self.config.data)
        if not self.config.data['tg']['currConv']:
            print('[WARNING] Не выбран чат для текущего вк-диалога')
        if not self.config.data['tg']['currChat']:
            print('[WARNING] Не выбран чат для текущего вк-чата')
        # TODO: Вынести диспатчеры в отдельный файл
        self.config.tg_api = self.config.get_api_tg(self.config.data['tg']['tg_token'],self.tg_hangler)
        self.config.tg_dispatcher.add_handler(CommandHandler("admin", self.get_admin))
        self.config.tg_dispatcher.add_handler(CommandHandler("authorize", self.authorize_tg))
        self.config.tg_dispatcher.add_handler(CommandHandler("v", self.vk_handler))
        self.config.tg_api.start_polling()
        self.config.tg_api.idle()

TgObject()