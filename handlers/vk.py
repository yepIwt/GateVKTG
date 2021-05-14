from vkwave.bots import DefaultRouter, SimpleBotEvent, simple_bot_message_handler
from vkwave.bots.core.dispatching import filters
from loguru import logger

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

async def send_notification_into_telegram(fl: tuple, message_text: str, chat_title=None):
    global tg_bot
    notification_text = f"{fl[0]} {fl[1]}@{chat_title or 'localhost'}: {message_text}"
    await tg_bot.send_message(CONFIG_OBJ['tg']['notificate_to'], notification_text)
    logger.debug(notification_text)

@simple_bot_message_handler(vk_msg_from_chat,filters.MessageFromConversationTypeFilter("from_chat"))
async def answer_chat(event: SimpleBotEvent):
    global tg_bot, CONFIG_OBJ
    check_if_chat_in_config(event.object.object.message.peer_id)

    first_last_names = await first_and_last_names_sender(event)

    if event.object.object.message.peer_id != CONFIG_OBJ['currentChat']:
        await send_notification_into_telegram(
            fl = first_last_names,
            message_text = event.object.object.message.text,
            chat_title = await chat_title(event)
        )
    else:
        await tg_bot.send_message(
            CONFIG_OBJ['tg']['chat_id'], 
            f'{first_last_names[0]} {first_last_names[1]}:\n{event.object.object.message.text}'
        )

@simple_bot_message_handler(vk_msg_from_chat,filters.MessageFromConversationTypeFilter("from_pm"))
async def answer_conv(event: SimpleBotEvent):
    global tg_bot, CONFIG_OBJ

    first_last_names = await first_and_last_names_sender(event)

    if (type(CONFIG_OBJ['currentConv']) == list) and (event.object.object.message.peer_id == CONFIG_OBJ['currentConv'][0]):
        await tg_bot.send_message(
            CONFIG_OBJ['tg']['conv_id'],
            f"{event.object.object.message.text}"
        )
    else:
        await send_notification_into_telegram(
            fl = first_last_names,
            message_text = event.object.object.message.text
        )
        
