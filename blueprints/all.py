from vkwave.bots import DefaultRouter, SimpleBotEvent, simple_bot_message_handler

from loguru import logger

all = DefaultRouter()

TG_BOT = None

@simple_bot_message_handler(all)
async def games(event: SimpleBotEvent):
    usr_id = event.object.object.message.from_id #event.object.object.message.from_id
    answer = await event.api_ctx.users.get(user_ids=usr_id,fields='first_name,last_name')
    f,l = answer.response[0].first_name, answer.response[0].last_name
    notification_text = f'Новое сообщение ВКонтакте от пользователя {f} {l}\nТекст сообщения: {event.object.object.message.text}'
    logger.debug(f'New message from VK: {f} {l}')
    #await bot.send_message(334298435, notification_text
