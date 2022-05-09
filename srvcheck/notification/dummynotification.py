from .notificationprovider import NotificationProvider

class DummyNotification(NotificationProvider):
	LOG_LEVEL = 0
	
	def send(self, st):
		print (st)

	def sendPhoto(self, photo):
		print ('Sending photo: %s' % photo)
