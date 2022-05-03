from .notificationprovider import NotificationProvider

class DummyNotification(NotificationProvider):
	def send(self, st):
		print (st)

	def sendPhoto(self, photo):
		print ('Sending photo: %s' % photo)
