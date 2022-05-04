#!/usr/bin/python3
import sys 
import time
import configparser

from .notification import Notification, DummyNotification, TelegramNotification, NOTIFICATION_SERVICES
from .tasks import *
from .utils import System
from .chains import CHAINS


EXAMPLE_CONF = """
name = srvcheck-emoney-1

[notification.telegram]
enabled = true
apiToken = 
chatIds = 

[notification.dummy]
enabled = true

[chain]
name = tendermint
endpoint = localhost:9933

[tasks]
disabled = name_of_a_task_to_disable
"""

if sys.version_info[0] < 3:
	print ('python2 not supported, please use python3')
	sys.exit (0)

try:
	import requests
except:
	print ('please install requests library (pip3 install requests)')
	sys.exit (0)


def main():
	# Parse configuration
	config = configparser.ConfigParser()
	config.read_string(EXAMPLE_CONF)

	# Initialization
	notification = Notification (config['name'])

	for x in NOTIFICATION_SERVICES:
		if ('notification.' + x) in config and config['notification.' + x]['enabled'] == 'true':
			notification.addProvider (NOTIFICATION_SERVICES[x](config))

	system = System()
	print (system.getUsage())

	# Get the chain by name or by detect
	for x in CHAINS:
		if 'chain' in config:
			if config['chain']['name'] == x.NAME:
				chain = x(config)
				break

		elif x.detect(config):
			chain = x(config)
			print ("Detected chain %s", chain.NAME)
			break

	# Create the list of tasks
	tasks = []

	for x in TASKS + chain.TASKS:
		if 'disabled' in config['tasks'] and config['tasks']['disabled'].index(x.NAME) != -1:
			continue

		tasks.append (x(notification, system, chain))


	# Mainloop
	TTS = 60

	while True:
		for t in tasks:
			if t.shouldBeChecked():
				try:
					t.run()
				except Exception as e:
					print ('Error in task %s: %s' % (t.name, e))

		notification.flush()
		time.sleep(TTS)

if __name__ == "__main__":
	main()