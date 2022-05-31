from .notification import Notification, Emoji
from .telegramnotification import TelegramNotification
from .dummynotification import DummyNotification

NOTIFICATION_SERVICES = {
    'telegram': TelegramNotification,
    'dummy': DummyNotification
}
