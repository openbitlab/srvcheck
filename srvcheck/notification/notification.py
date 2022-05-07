class Notification:
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

	def __init__(self, name):
		self.name = name
		self.providers = []

	def addProvider(self, p):
		self.providers.append(p)

	def append(self, s, emoji = ''):
		for x in self.providers:
			x.append(self.name + ' ' + s + ('' if emoji == '' else ' ' + emoji))

	def flush(self):
		for x in self.providers:
			x.flush()

	def send(self, st, emoji = ''):
		for x in self.providers:
			x.send(self.name + ' ' + st + ('' if emoji == '' else ' ' + emoji))

	def sendPhoto(self, photo):
		for x in self.providers:
			x.sendPhoto(photo)