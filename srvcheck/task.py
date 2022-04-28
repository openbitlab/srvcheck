import time 

class Task:
	def __init__(self, name, notification, checkEvery = 15, notifyEvery = 15):
		self.name = name
		self.checkEvery = checkEvery
		self.notifyEvery = notifyEvery
		self.notification = notification

		self.lastCheck = 0
		self.lastNotify = 0

	def shouldBeChecked(self):
		return self.lastCheck + self.checkEvery < time.time()

	def shouldBeNotified(self):
		return self.lastNotify + self.notifyEvery < time.time()

	def markChecked(self):
		self.lastCheck = time.time()

	def notify(self, nstr):
		if self.shouldBeNotified():
			self.lastNotify = time.time()
			self.notification.append(nstr)
			return True

	def run(self):
		raise Exception('Abstract run()')


class TaskSystemUsage:
	def __init__(self, notification, system):
		super().__init__('TaskSystemUsage', notification, 15, 120)
		self.system = system

	def run(self):
		usage = self.system.getUsage()

		if usage['cpu'] > 90:
			self.notify('CPU usage is above %d%%' % usage['cpu'])

		self.markChecked()