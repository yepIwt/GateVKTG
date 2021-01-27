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

    def register_chat(self, update: Update, context: CallbackContext):
        if not update.message['chat']['type'] == 'group':
            update.message.reply_text('Еблан, ты как лс будешь привязывать блять к системе?')
        else:
            msg = update.message['text'].split(' ')[-1]
            if msg == 'chat':
                update.message.reply_text('Ну ща зарегаю как вк-чат')
                self.config.data['tg']['currChat'][0] = update.message['chat']['id']
            elif msg == 'conv':
                update.message.reply_text('Ну ща зарегаю как вк-диалог')
                self.config.data['tg']['currConv'][0] = update.message['chat']['id']
            else:
                update.message.reply_text('/register WHAT???')
        self.config.save_in_file()

    def show_chats(self, update: Update, context: CallbackContext):
        if not self.config.data['vk']['chats']:
            update.message.reply_text("Нет вк-чатов")
        else:
            msg = ''
            for a,chat in list(enumerate(self.config.data['vk']['chats'])):
                name = self.config.vk_api.messages.getConversationsById(peer_ids=chat)['items'][0]['chat_settings']['title']
                msg += '{} - {}\n'.format(a,name)
            update.message.reply_text(msg)

    def __init__(self):
        self.config = confs.Config('password')
        self.funcs = Functions()
        self.funcs.get_api_messages(self.config.data['tg']['tg_token'])
        print(self.config.data)
        if not self.config.data['tg']['currConv']:
            print('[WARNING] Не выбран чат для текущего вк-диалога')
        if not self.config.data['tg']['currChat']:
            print('[WARNING] Не выбран чат для текущего вк-чата')
        self.config.tg_api = self.config.get_api_tg(self.config.data['tg']['tg_token'],self.tg_hangler)
        self.config.tg_dispatcher.add_handler(CommandHandler("admin", self.get_admin))
        self.config.tg_dispatcher.add_handler(CommandHandler("register", self.register_chat))
        self.config.tg_dispatcher.add_handler(CommandHandler("chats", self.show_chats))
        self.config.tg_api.start_polling()
        self.config.tg_api.idle()

TgObject()