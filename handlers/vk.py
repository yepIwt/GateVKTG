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

@simple_bot_message_handler(vk_msg_from_chat,filters.MessageFromConversationTypeFilter("from_chat"))
async def answer_chat(event: SimpleBotEvent):
    global tg_bot, CONFIG_OBJ
    #
    if event.object.object.message.peer_id not in CONFIG_OBJ['vk']['chats']:
        CONFIG_OBJ['vk']['chats'].append(event.object.object.message.peer_id)
    usr_id = event.object.object.message.from_id #event.object.object.message.from_id
    answer = await event.api_ctx.users.get(user_ids=usr_id,fields='first_name,last_name')
    f,l = answer.response[0].first_name, answer.response[0].last_name
    api_answer = await event.api_ctx.messages.get_conversations_by_id(peer_ids=event.object.object.message.peer_id)
    chat_title = api_answer.response.items[0].chat_settings.title
    notification_text = f'Сообщение из беседы {chat_title} от {f} {l}\n> {event.object.object.message.text}'
    logger.debug(notification_text)
    await tg_bot.send_message(CONFIG_OBJ['tg']['notificate_to'], notification_text)

@simple_bot_message_handler(vk_msg_from_chat,filters.MessageFromConversationTypeFilter("from_pm"))
async def answer_conv(event: SimpleBotEvent):
    global tg_bot, CONFIG_OBJ
    usr_id = event.object.object.message.from_id #event.object.object.message.from_id
    answer = await event.api_ctx.users.get(user_ids=usr_id,fields='first_name,last_name')
    f,l = answer.response[0].first_name, answer.response[0].last_name
    notification_text = f'Личное сообщение от {f} {l}\n> {event.object.object.message.text}'
    logger.debug(notification_text)
    await tg_bot.send_message(CONFIG_OBJ['tg']['notificate_to'], notification_text)

#async tg_notification(id, )
