#!/usr/bin/python3
import sys 
import time
import configparser

from .notification import Notification, DummyNotification, TelegramNotification, NOTIFICATION_SERVICES
from .tasks import *
from .utils import System
from .chains import CHAINS

if sys.version_info[0] < 3:
	print ('python2 not supported, please use python3')
	sys.exit (0)

try:
	import requests
except:
	print ('please install requests library (pip3 install requests)')
	sys.exit (0)

def addTasks(chain, notification, system, config):
	# Create the list of tasks
	tasks = []

	for x in TASKS + chain.TASKS:
		if 'disabled' in config['tasks'] and config['tasks']['disabled'].index(x.TYPE) != -1:
			continue

		if x.isPluggable():
			tasks.append (x(config, notification, system, chain))
	return tasks

def main():
	# Parse configuration
	config = configparser.ConfigParser()
	config.read('/etc/srvcheck.conf')

	# Initialization
	notification = Notification (config['chain']['name'])

	for x in NOTIFICATION_SERVICES:
		if ('notification.' + x) in config and config['notification.' + x]['enabled'] == 'true':
			notification.addProvider (NOTIFICATION_SERVICES[x](config))
	
	notification.send("Monitor started!")

	system = System()
	print (system.getUsage())

	# Get the chain by name or by detect
	tasks = []
	for x in CHAINS:
		if 'chain' in config:
			if config['chain']['type'] == x.TYPE:
				chain = x(config)
				tasks = addTasks(chain, notification, system, config)
				break

		elif x.detect(config):
			chain = x(config)
			print ("Detected chain %s", chain.TYPE)
			tasks = addTasks(chain, notification, system, config)
			break

	# Mainloop
	TTS = 60
	autoRecover = 'autoRecover' in config['tasks'] and config['tasks']['autoRecover'] == 'true'

	while True:
		for t in tasks:
			if t.shouldBeChecked():
				try:
					r = t.run()
					t.markChecked()

					if autoRecover and r and t.shouldBeRecovered() and t.canRecover():
						t.recover()
						t.markRecovered()

				except Exception as e:
					print ('Error in task %s: %s' % (t.name, e))

		notification.flush()
		time.sleep(TTS)

if __name__ == "__main__":
	main()