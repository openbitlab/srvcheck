import os
import json
import requests
from ..utils.confset import ConfItem, ConfSet
from .notificationprovider import NotificationProvider
import urllib.parse

ConfSet.addItem(ConfItem('notification.telegram.enabled', None, bool, 'enable telegram notification'))
ConfSet.addItem(ConfItem('notification.telegram.apiToken', None, str, 'telegram api token'))
ConfSet.addItem(ConfItem('notification.telegram.chatIds', None, str, 'telegram chat ids'))

class TelegramNotification(NotificationProvider):
	LOG_LEVEL = 0

	def __init__(self, conf):
		super().__init__(conf)
		try:
			self.apiToken = conf.getOrDefault('notification.telegram.apiToken').strip('\"')
			self.chatIds = json.loads(conf.getOrDefault('notification.telegram.chatIds'))

		except:
			self.apiToken = ""
			self.chatIds = ""

	def sendPhoto(self, photo):
		for ci in self.chatIds:
			os.system('curl -F photo=@"./%s" https://api.telegram.org/bot%s/sendPhoto?chat_id=%s' % (photo, self.apiToken, ci))

	def send(self, st):
		print(st.encode('utf-8'))
		for x in self.chatIds:
			requests.get(f'https://api.telegram.org/bot{self.apiToken}/sendMessage?text={st}&chat_id={x}').json()

	def format(self, name, string):
		return urllib.parse.quote('#' + name + ' ' + string)