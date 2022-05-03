import requests
import json


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


class DummyNotification(NotificationProvider):
	def send(self, st):
		print (st)

	def sendPhoto(self, photo):
		print ('Sending photo: %s' % photo)


class TelegramNotification(NotificationProvider):
	def __init__(self, apiToken, chatIds):
		self.apiToken = apiToken
		self.chatIds = chatIds

	def sendPhoto(self, photo):
		# os.system('curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s' % (file, apiToken, chat_id))
		pass 
	
	def send(self, st):
		print(st.encode('utf-8'))
		for x in self.chatIds:
			d = requests.get('https://api.telegram.org/bot%s/sendMessage?text=%s&chat_id=%s' %
							(self.apiToken, st, x)).json()
