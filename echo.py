import logging
import confs
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

class Functions(object):

    def get_name(self,obj):
        f = obj.message.to_dict()['from']['first_name']
        l = ''
        if 'last_name' in obj.message.to_dict()['from']:
            l = obj.message.to_dict()['from']['last_name']
        return f,l

class TgObject(object):

    __slots__ = ('config','funcs')

    def tg_hangler(self,update: Update, context: CallbackContext):
        #print(update.message.to_dict())
        title = update['message']['chat']['title']
        f,l = self.funcs.get_name(update)
        msg_text = update.message.text
        print('[NEW] Message from chat: {}'.format(title))
        print('[FROM] {} {}'.format(f,l))
        print('[TEXT] {}'.format(msg_text))
        update.message.reply_text(update.message.text)

    def __init__(self):
        self.config = confs.Config('password')
        self.funcs = Functions()
        self.config.tg_api = self.config.get_api_tg(self.config.data['tg']['tg_token'],self.tg_hangler)
        self.config.tg_api.start_polling()
        self.config.tg_api.idle()

TgObject()