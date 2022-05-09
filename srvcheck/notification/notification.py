
class Emoji:
	Start 		= "\U0001F514"
	Disk 		= "\U0001F4BE"
	Stuck 		= "\U000026D4"
	Rel 		= "\U0000E126"
	Peers 		= "\U0001F198"
	Sync 		= "\U00002757"
	SyncOk 		= "\U000FEB4A"
	PosUp 		= "\U0001F53C"
	PosDown 	= "\U0001F53D"
	BlockMiss 	= "\U0000E333"
	Health 		= "\U0001F6A8"
	Cpu 		= "\U000026A0"


class Notification:
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