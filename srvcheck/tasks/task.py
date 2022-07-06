import time

def seconds(m):
	return m

def minutes(m):
	return m * 60

def hours(h):
	return h * 60 * 60

class Task:
	def __init__(self, name, conf, notification, system, chain, checkEvery = minutes(15), notifyEvery = minutes(15), recoverEvery = hours(2)):
		self.name = name
		self.conf = conf
		self.system = system
		self.chain = chain
		self.checkEvery = checkEvery
		self.notifyEvery = notifyEvery
		self.recoverEvery = recoverEvery
		self.notification = notification

		self.lastCheck = 0
		self.lastNotify = 0
		self.lastRecover = 0

	@staticmethod
	def isPluggable(conf):
		""" Returns true if the task can be plugged in """
		raise Exception('Abstract isPluggable()')

	def shouldBeChecked(self):
		return (self.lastCheck + self.checkEvery) < time.time()

	def shouldBeNotified(self):
		return (self.lastNotify + self.notifyEvery) < time.time()

	def markChecked(self):
		self.lastCheck = time.time()

	def notify(self, nstr, noCheck = False):
		if self.shouldBeNotified() or noCheck:
			self.lastNotify = time.time()
			self.notification.append(nstr)
			return True
		return False

	def run(self):
		raise Exception('Abstract run()')

	def shouldBeRecovered(self):
		return (self.lastRecover + self.recoverEvery) < time.time()

	def canRecover(self):
		return False

	def recover(self):
		return None

	def markRecovered(self):
		self.lastRecover = time.time()
