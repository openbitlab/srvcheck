from srvcheck.notification.notificationprovider import NotificationProvider

class MockNotification(NotificationProvider):
	START_EMOJI = "\U0001F514"
	DISK_EMOJI = "\U0001F4BE"
	STUCK_EMOJI = "\U000026D4"
	REL_EMOJI = "\U0000E126"
	PEERS_EMOJI = "\U0001F198"
	SYNC_EMOJI = "\U00002757"
	SYNC_OK_EMOJI = "\U000FEB4A"
	POS_UP_EMOJI = "\U0001F53C"
	POS_DOWN_EMOJI = "\U0001F53D"
	BLOCK_MISS_EMOJI = "\U0000E333"
	HEALTH_EMOJI = "\U0001F6A8"
	CPU_EMOJI = "\U000026A0"

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
		self.events.append('Sending photo: %s' % photo)
		self.onNotify('Sending photo: %s' % photo)

	def append(self, s):
		super().append(s)

