import requests
import json

class Notification:
	notifies = []

	def __init__(self, apiToken, chatIds):
		self.apiToken = apiToken
		self.chatIds = chatIds

	def send(self, st):
		print(st.encode('utf-8'))
		for x in self.chatIds:
			d = requests.get('https://api.telegram.org/bot%s/sendMessage?text=%s&chat_id=%s' %
							(self.apiToken, st, x)).json()

	def append(self, s):
		self.notifies.append(s)

	def flush(self):
		if len(self.notifies) > 0:
			st = '\n'.join(self.notifies)
			self.send(st)
			self.notifies = []