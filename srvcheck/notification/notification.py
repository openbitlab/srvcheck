class Notification:
	def __init__(self):
		self.providers = []

	def addProvider(self, p):
		self.providers.append(p)

	def append(self, s):
		for x in self.providers:
			x.append(s)

	def flush(self):
		for x in self.providers:
			x.flush()

	def send(self, st):
		for x in self.providers:
			x.send(st)

	def sendPhoto(self, photo):
		for x in self.providers:
			x.sendPhoto(photo)