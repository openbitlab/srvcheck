from ..utils.confset import ConfItem, ConfSet
from .notificationprovider import NotificationProvider

ConfSet.addItem(ConfItem('notification.dummy.enabled', True, bool, 'enable dummy notification'))

class DummyNotification(NotificationProvider):
	LOG_LEVEL = 0

	def send(self, st):
		print (st)

	def sendPhoto(self, photo):
		print (f'Sending photo: {photo}')
