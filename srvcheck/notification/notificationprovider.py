class NotificationProvider:
	notifies = []

	def send(self, st):
		raise Exception('Abstract send()')

	def sendPhoto(self, photo):
		pass

	def append(self, s):
		self.notifies.append(s)

	def flush(self):
		if len(self.notifies) > 0:
			st = '\n'.join(self.notifies)
			self.send(st)
			self.notifies = []

