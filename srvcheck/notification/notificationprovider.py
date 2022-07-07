class NotificationProvider:
	LOG_LEVEL = 0

	def __init__(self, conf):
		self.conf = conf
		self.notifies = []

	def __del__(self):
		self.flush()

	def send(self, st):
		raise Exception('Abstract send()')

	def sendPhoto(self, photo):
		pass

	def append(self, s):
		self.notifies.append(s)

	def format(self, name, string):
		return name + ' ' + string

	def flush(self):
		if len(self.notifies) > 0:
			st = '\n'.join(self.notifies)
			self.send(st)
			self.notifies = []
