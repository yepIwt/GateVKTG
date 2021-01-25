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

class TgObject(object):

    __slots__ = ('config','funcs','api_messages')

    def tg_hangler(self,update: Update, context: CallbackContext):
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
        self.funcs.send_message(0,message_text)
        #update.message.reply_text(message_text)

    def __init__(self):
        self.config = confs.Config('password')
        self.funcs = Functions()
        self.funcs.get_api_messages(self.config.data['tg']['tg_token'])
        print(self.config.data)
        
        self.config.tg_api = self.config.get_api_tg(self.config.data['tg']['tg_token'],self.tg_hangler)
        self.config.tg_dispatcher.add_handler(CommandHandler("admin", self.get_admin))
        self.config.tg_api.start_polling()
        self.config.tg_api.idle()

TgObject()