from .notification import Notification
from .telegramnotification import TelegramNotification
from .dummynotification import DummyNotification

NOTIFICATION_SERVICES = {
    'telegram': TelegramNotification,
    'dummy': DummyNotification
}