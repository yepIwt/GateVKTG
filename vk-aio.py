from vkwave.bots import SimpleLongPollBot

bot = SimpleLongPollBot(tokens="9e8b113868e44cd7ea23716f7b4e4bc1d2f90a33c953d22c49a828995a6b95b196190c5588ea3b31fd074", group_id=198731493)

@bot.message_handler(bot.text_filter("bye"))
def handle(_) -> str:
    return "bye world"

@bot.message_handler(bot.text_filter ("hello"))
async def handle(event: bot.SimpleBotEvent):
    await event.answer("hello world!")

bot.run_forever()
