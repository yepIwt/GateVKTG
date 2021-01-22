#!/usr/bin/env python
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.

import logging

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi!')

def get_name(obj):
    f = obj.message.to_dict()['from']['first_name']
    l = ''
    if 'last_name' in obj.message.to_dict()['from']:
        l = obj.message.to_dict()['from']['last_name']
    return f,l


def echo(update: Update, context: CallbackContext) -> None:
    print(update.message.to_dict())
    title = update['message']['chat']['title']
    f,l = get_name(update)
    msg_text = update.message.text
    print('[NEW] Message from chat: {}'.format(msg_text))
    print('[FROM] {} {}'.format(f,l))
    print('[TEXT] {}'.format(msg_text))
    update.message.reply_text(update.message.text)

def main():
    updater = Updater('', use_context=True)
 
   # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
