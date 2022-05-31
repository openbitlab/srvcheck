import json
from ..utils.confset import ConfItem, ConfSet
import requests
from .notificationprovider import NotificationProvider

ConfSet.addItem(ConfItem('notification.telegram.enabled', None, bool, 'enable telegram notification'))
ConfSet.addItem(ConfItem('notification.telegram.apiToken', None, str, 'telegram api token'))
ConfSet.addItem(ConfItem('notification.telegram.chatIds', None, str, 'telegram chat ids'))

class TelegramNotification(NotificationProvider):
	LOG_LEVEL = 0

	def __init__(self, conf):
		try:
			self.apiToken = conf.getOrDefault('notification.telegram.apiToken').strip('\"')
			self.chatIds = json.loads(conf.getOrDefault('notification.telegram.chatIds'))

		except:
			self.apiToken = ""
			self.chatIds = ""

		super().__init__(conf)

	def sendPhoto(self, photo):
		# os.system('curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s' % (file, apiToken, chat_id))
		pass

	def send(self, st):
		print(st.encode('utf-8'))
		for x in self.chatIds:
			requests.get(f'https://api.telegram.org/bot{self.apiToken}/sendMessage?text={st}&chat_id={x}').json()
