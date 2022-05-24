#!/usr/bin/python3
import sys 
import time
import configparser
import traceback

import srvcheck

from .notification import Emoji, Notification, DummyNotification, TelegramNotification, NOTIFICATION_SERVICES
from .tasks import *
from .utils import System, ConfSet, ConfItem
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

	for x in TASKS + chain.CUSTOM_TASKS:
		task = x(config, notification, system, chain)
		if 'disabled' in config['tasks'] and config['tasks']['disabled'].find(task.name) != -1:
			continue

		if task.isPluggable():
			tasks.append(task)
	return tasks

def main():
	# Parse configuration
	confRaw = configparser.ConfigParser()
	confRaw.read('/etc/srvcheck.conf')

	conf = ConfSet(confRaw)
	conf.addItem(ConfItem('chain.type', None, str))
	conf.addItem(ConfItem('chain.name', None, str))
	conf.addItem(ConfItem('tasks.autoRecover', False, bool))

	# Get version
	version = srvcheck.__version__

	# Initialization
	notification = Notification (conf.getOrDefault('chain.name'))

	for x in NOTIFICATION_SERVICES:
		if conf.exists('notification.%s.enabled' % x) and conf.getOrDefault('notification.%s.enabled' % x, False):
			notification.addProvider (NOTIFICATION_SERVICES[x](conf))
	
	notification.send("monitor v%s started %s" %(version, Emoji.Start))

	system = System(conf)
	print (system.getUsage())

	# Get the chain by name or by detect
	chain = None
	tasks = []
	for x in CHAINS:
		if conf.getOrDefault('chain.type') == x.TYPE:
			chain = x(conf)
			tasks = addTasks(chain, notification, system, conf)
			break

	if not chain:
		for x in CHAINS:
			if x.detect(conf):
				chain = x(conf)
				print ("Detected chain %s", chain.TYPE)
				tasks = addTasks(chain, notification, system, conf)
				break

	# Mainloop
	TTS = 60
	autoRecover = conf.getOrDefault('tasks.autoRecover')

	while True:
		for t in tasks:
			if t.shouldBeChecked():
				try:
					r = t.run()
					t.markChecked()

					if autoRecover and r and t.shouldBeRecovered() and t.canRecover():
						t.recover()
						t.markRecovered()

				except Exception:
					print ('Error in task %s: %s' % (t.name, traceback.format_exc()))

		notification.flush()		
		sys.stdout.flush()
		time.sleep(TTS)

if __name__ == "__main__":
	main()