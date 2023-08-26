from .dummynotification import DummyNotification  # noqa: F401
from .notification import Emoji, Notification, NotificationLevel  # noqa: F401
from .telegramnotification import TelegramNotification  # noqa: F401

NOTIFICATION_SERVICES = {"telegram": TelegramNotification, "dummy": DummyNotification}
