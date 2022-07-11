import unittest
import urllib.parse
from srvcheck.notification import Notification
from srvcheck.utils import ConfSet
from .mocks import MockNotification

class TestNotification(unittest.TestCase):
	def test_send(self):
		n = Notification('Test')
		mn = MockNotification(ConfSet({}))
		n.addProvider(mn)
		n.send('Hello WorldS!')
		self.assertEqual(mn.events[0], urllib.parse.quote('#Test Hello WorldS!'))

	def test_sendPhoto(self):
		n = Notification('Test')
		mn = MockNotification(ConfSet({}))
		n.addProvider(mn)
		n.sendPhoto('/tmp/test.jpg')
		self.assertEqual(mn.events[0], 'Sending photo: /tmp/test.jpg')

	def test_append(self):
		n = Notification('Test')
		mn = MockNotification(ConfSet({}))
		n.addProvider(mn)
		n.append('Hello WorldA!')
		n.append('Hello WorldB!')
		n.flush()
		self.assertEqual(mn.events[0], urllib.parse.quote('#Test Hello WorldA!\nTest Hello WorldB! '))
