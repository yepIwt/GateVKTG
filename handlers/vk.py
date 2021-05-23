from vkwave.bots import DefaultRouter, SimpleBotEvent, simple_bot_message_handler
from vkwave.types.objects import MessagesMessageAttachmentType
from vkwave.bots.core.dispatching import filters
from loguru import logger
import random
import requests

vk_msg_from_chat = DefaultRouter()

tg_bot = None
CONFIG_OBJ = None

def config_vk_hand(c = None):
    global CONFIG_OBJ
    if not c:
        return CONFIG_OBJ
    CONFIG_OBJ = c

def setup_tg_bot_to_vk_handler(new_global):
    global tg_bot
    tg_bot = new_global

def check_if_chat_in_config(peer_id: int) -> None:
    global CONFIG_OBJ
    if peer_id not in CONFIG_OBJ['vk']['chats']:
        CONFIG_OBJ['vk']['chats'].append(peer_id)

async def first_and_last_names_sender(event: SimpleBotEvent) -> tuple:
    usr_id = event.object.object.message.from_id
    answer = await event.api_ctx.users.get(user_ids=usr_id,fields='first_name,last_name')
    f,l = answer.response[0].first_name, answer.response[0].last_name 
    return f,l

async def chat_title(event: SimpleBotEvent) -> str:
    api_answer = await event.api_ctx.messages.get_conversations_by_id(peer_ids=event.object.object.message.peer_id)
    chat_title = api_answer.response.items[0].chat_settings.title
    return chat_title

async def send_notification_into_telegram(fl: tuple, message_text: str, chat_title = None, attachments = None):
    global tg_bot
    if attachments:
        for catched in attachments:
            if catched['type'] == 'voice':
                await tg_bot.send_voice(
                    chat_id = CONFIG_OBJ['tg']['notificate_to'],
                    voice = open(catched['filename'],'rb'),
                    caption = f"{fl[0]} {fl[1]}@{chat_title or 'localhost'}: {catched['caption'] or ' '}"
                )
            elif catched['type'] == 'photo':
                await tg_bot.send_photo(
                    chat_id = CONFIG_OBJ['tg']['notificate_to'],
                    photo = open(catched['filename'],'rb'),
                    caption = f"{fl[0]} {fl[1]}@{chat_title or 'localhost'}: {catched['caption'] or ' '}"
                )
    else:
        notification_text = f"{fl[0]} {fl[1]}@{chat_title or 'localhost'}: {message_text}"
        await tg_bot.send_message(CONFIG_OBJ['tg']['notificate_to'], notification_text)
    logger.debug('Отправлено уведомление')

def download_voice_message(attachment: SimpleBotEvent):
    link_to_voice_msg = attachment.audio_message.link_ogg
    r = requests.get(link_to_voice_msg)
    with open('voice.ogg','wb') as f:
        f.write(r.content)
    return 'voice.ogg'

async def download_photo(attachment: SimpleBotEvent):
    link_to_photo = attachment.photo.sizes[-1].url
    r = requests.get(link_to_photo)
    filename = str(random.randint(0,9999)) + '.jpg'
    with open(filename,'wb') as f:
        f.write(r.content)
    return filename

async def download_doc(attachment: SimpleBotEvent):
    link_to_file = attachment.doc.url
    r = requests.get(link_to_file)
    filename = attachment.doc.title
    with open(filename,'wb') as f:
        f.write(r.content)
    return filename

async def catch_attachments(event: SimpleBotEvent):
    catched_attachs = []
    if event.object.object.message.attachments:
        for attach in event.object.object.message.attachments:
            if attach.type == MessagesMessageAttachmentType.AUDIO_MESSAGE:
                catched_attachs.append({
                        'type':'voice',
                        'caption': None,
                        'filename': download_voice_message(attach)
                })

            elif attach.type == MessagesMessageAttachmentType.PHOTO:
                catched_attachs.append({
                        'type':'photo',
                        'caption': event.object.object.message.text,
                        'filename': await download_photo(attach)
                })
            elif attach.type == MessagesMessageAttachmentType.DOC:
                catched_attachs.append({
                        'type': 'doc',
                        'caption': event.object.object.message.text,
                        'filename': await download_doc(attach)
                })
    return catched_attachs

async def send_tg_voice(filename: str, chat_id: int, caption = None):
    global tg_bot
    await tg_bot.send_voice(
        chat_id = chat_id,
        voice = open(filename,'rb'),
    )

async def send_tg_photo(filename: str, chat_id: int, caption = None):
    global tg_bot
    await tg_bot.send_photo(
        chat_id = chat_id,
        photo = open(filename,'rb'),
        caption = caption
    )

async def send_tg_doc(filename: str, chat_id: int, caption = None):
    global tg_bot
    info = await tg_bot.send_document(
        chat_id = chat_id,
        document = open(filename,'rb')
    )
    if caption:
        await tg_bot.edit_message_caption(
            chat_id = chat_id,
            message_id = info.message_id,
            caption = caption
        )

async def send_catched_attachments(attachments, send_to):
    for catched in attachments:
        if catched['type'] == 'voice':
            await send_tg_voice(catched['filename'], send_to) # CONFIG_OBJ['tg']['chat_id']
        elif catched['type'] == 'photo':
            await send_tg_photo(catched['filename'], send_to, catched['caption'])
        elif catched['type'] == 'doc':
            await send_tg_doc(catched['filename'], send_to, catched['caption'])

@simple_bot_message_handler(vk_msg_from_chat,filters.MessageFromConversationTypeFilter("from_chat"))
async def answer_chat(event: SimpleBotEvent):
    global tg_bot, CONFIG_OBJ

    check_if_chat_in_config(event.object.object.message.peer_id)

    first_last_names = await first_and_last_names_sender(event)

    attachments = await catch_attachments(event)

    if event.object.object.message.peer_id != CONFIG_OBJ['currentChat']:
        await send_notification_into_telegram(
            fl = first_last_names,
            message_text = event.object.object.message.text,
            chat_title = await chat_title(event),
            attachments = attachments
        )
    else: # Я отправил в курент чат и он активен
        if attachments:
            await send_catched_attachments(attachments, CONFIG_OBJ['tg']['chat_id'])
        else:
            await tg_bot.send_message(
                chat_id = CONFIG_OBJ['tg']['chat_id'],
                text = f'{first_last_names[0]} {first_last_names[1]}:\n{event.object.object.message.text}'
            )

@simple_bot_message_handler(vk_msg_from_chat,filters.MessageFromConversationTypeFilter("from_pm"))
async def answer_conv(event: SimpleBotEvent):
    global tg_bot, CONFIG_OBJ

    first_last_names = await first_and_last_names_sender(event)

    attachments = await catch_attachments(event)

    if (type(CONFIG_OBJ['currentConv']) == list) and (event.object.object.message.peer_id == CONFIG_OBJ['currentConv'][0]):
        if attachments:
            await send_catched_attachments(attachments, CONFIG_OBJ['tg']['conv_id'])
        else:
            await tg_bot.send_message(
                chat_id = CONFIG_OBJ['tg']['conv_id'],
                text = f'{event.object.object.message.text}'
            )
    else: # Сообщение отправлено не в текущий диалог
        await send_notification_into_telegram(
            fl = first_last_names,
            message_text = event.object.object.message.text,
            attachments=attachments,
        )