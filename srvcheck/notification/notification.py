class Notification:
	START_EMOJI = "\U0001F514"

	def __init__(self, name):
		self.name = name
		self.providers = []

	def addProvider(self, p):
		self.providers.append(p)

	def append(self, s):
		for x in self.providers:
			x.append(self.name + ' ' + s)

	def flush(self):
		for x in self.providers:
			x.flush()

	def send(self, st, emoji = ''):
		for x in self.providers:
			x.send(self.name + ' ' + st + '' if emoji == '' else ' ' + emoji)

	def sendPhoto(self, photo):
		for x in self.providers:
			x.sendPhoto(photo)