import requests
import json

telegram_bot_token = ""

class TelegramApi(object):

    __slots__ = ("link_api")

    def __init__(self,token):
        self.link_api = "https://api.telegram.org/bot{}/".format(token)
    
    def getMe(self):
        method = "getMe"
        r = requests.get(self.link_api + method)
        return json.loads(r.text)
    
    def getChat(self, chat_id):
        method = "getChat"
        args = {'chat_id': chat_id}
        r = requests.get(self.link_api + method, params = args)
        return json.loads(r.text)

t = TelegramApi(telegram_bot_token)
#print(t.getMe())