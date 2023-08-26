from ..utils.confset import ConfItem, ConfSet
from .notificationprovider import NotificationProvider

ConfSet.addItem(
    ConfItem("notification.dummy.enabled", True, bool, "enable dummy notification")
)


class DummyNotification(NotificationProvider):
    def send(self, st, level):
        print(st)

    def sendPhoto(self, photo, level):
        print(f"Sending photo: {photo}")
