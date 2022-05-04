class NotificationProvider:
	notifies = []

	def __init__(self, conf):
		pass 			

	def __del__(self):
		self.flush()

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

