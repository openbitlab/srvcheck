import requests
import json
from .notificationprovider import NotificationProvider

class TelegramNotification(NotificationProvider):
	def __init__(self, conf):
		self.apiToken = conf['notification.telegram']['apiToken']
		self.chatIds = conf['notification.telegram']['chatIds']

	def sendPhoto(self, photo):
		# os.system('curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s' % (file, apiToken, chat_id))
		pass 

	def send(self, st):
		print(st.encode('utf-8'))
		for x in self.chatIds:
			d = requests.get('https://api.telegram.org/bot%s/sendMessage?text=%s&chat_id=%s' %
							(self.apiToken, st, x)).json()

