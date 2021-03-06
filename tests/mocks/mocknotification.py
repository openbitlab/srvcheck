from srvcheck.notification.notificationprovider import NotificationProvider

class MockNotification(NotificationProvider):
	def __init__(self, conf):
		self.events = [] 
		self.onNotifyHandler = lambda x: None
		super().__init__(conf)

	def onNotify(self, l):
		self.onNotifyHandler = l

	def send(self, st):
		self.events.append(st)
		self.onNotify(st)

	def sendPhoto(self, photo):
		f = f'Sending photo: {photo}'
		self.events.append(f)
		self.onNotify(f)

	def append(self, s):
		super().append(s)
