import json
import os
import urllib.parse

import requests

from ..utils.confset import ConfItem, ConfSet
from .notificationprovider import NotificationProvider

ConfSet.addItem(
    ConfItem(
        "notification.telegram.enabled", None, bool, "enable telegram notification"
    )
)
ConfSet.addItem(
    ConfItem("notification.telegram.apiToken", None, str, "telegram api token")
)
ConfSet.addItem(
    ConfItem("notification.telegram.chatIds", None, str, "telegram chat ids")
)
ConfSet.addItem(
    ConfItem("notification.telegram.infoLevelChatIds", None, str, "telegram chat ids for info notifications")
)
ConfSet.addItem(
    ConfItem("notification.telegram.warningLevelChatIds", None, str, "telegram chat ids for warning notifications")
)
ConfSet.addItem(
    ConfItem("notification.telegram.errorLevelChatIds", None, str, "telegram chat ids for error notifications")
)


class TelegramNotification(NotificationProvider):
    def __init__(self, conf):
        super().__init__(conf)
        try:
            self.apiToken = conf.getOrDefault("notification.telegram.apiToken").strip(
                '"'
            )
            self.chatIds = json.loads(
                conf.getOrDefault("notification.telegram.chatIds")
            )

        except:
            self.apiToken = ""
            self.chatIds = ""

    def sendPhoto(self, photo, level):
        for ci in self.chatIds:
            os.system(
                'curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s'
                % (photo, self.apiToken, ci)
            )

    def send(self, st, level):
        print(st.encode("utf-8"))
        for x in self.chatIds:
            requests.get(
                f"https://api.telegram.org/bot{self.apiToken}/sendMessage?text={st}&chat_id={x}"
            ).json()

    def format(self, name, string):
        return urllib.parse.quote("#" + name + " " + string)
