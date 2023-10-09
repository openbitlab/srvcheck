import json
import os
import urllib.parse

import requests

from ..utils.confset import ConfItem, ConfSet
from .notification import NotificationLevel
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
    ConfItem(
        "notification.telegram.infoLevelChatId",
        None,
        str,
        "telegram chat id for info notifications",
    )
)
ConfSet.addItem(
    ConfItem(
        "notification.telegram.warningLevelChatId",
        None,
        str,
        "telegram chat id for warning notifications",
    )
)
ConfSet.addItem(
    ConfItem(
        "notification.telegram.errorLevelChatId",
        None,
        str,
        "telegram chat id for error notifications",
    )
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
            self.chatIds = []

        self.errorLevelChatId = conf.getOrDefault(
            "notification.telegram.errorLevelChatId"
        )
        self.warningLevelChatId = conf.getOrDefault(
            "notification.telegram.warningLevelChatId"
        )
        self.infoLevelChatId = conf.getOrDefault(
            "notification.telegram.infoLevelChatId"
        )

    def _getChatIdsForLevel(self, level):
        if level == NotificationLevel.Error and self.errorLevelChatId:
            return [self.errorLevelChatId]
        elif (
            level == NotificationLevel.Warning
            or (level == NotificationLevel.Error and not self.errorLevelChatId)
        ) and self.warningLevelChatId:
            return [self.warningLevelChatId]
        elif (
            level == NotificationLevel.Info
            or (level == NotificationLevel.Error and not self.errorLevelChatId)
            or (level == NotificationLevel.Warning and not self.warningLevelChatId)
        ) and self.warningLevelChatId:
            return [self.infoLevelChatId]

        return self.chatIds

    def sendPhoto(self, photo, level):
        cids = self._getChatIdsForLevel(level)
        for ci in cids:
            os.system(
                'curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s'
                % (photo, self.apiToken, ci)
            )

    def send(self, st, level):
        print(level, st.encode("utf-8"))
        cids = self._getChatIdsForLevel(level)

        for x in cids:
            requests.get(
                f"https://api.telegram.org/bot{self.apiToken}/sendMessage?text={st}&chat_id={x}"
            ).json()

    def format(self, name, string):
        return urllib.parse.quote("#" + name + " " + string)
