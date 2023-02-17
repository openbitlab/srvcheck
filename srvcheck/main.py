#!/usr/bin/python3
import argparse
import configparser
import sys
import os
import time
import traceback
from functools import reduce

import srvcheck

from .chains import CHAINS
from .notification import NOTIFICATION_SERVICES, Emoji, Notification
from .tasks import TASKS
from .utils import ConfItem, ConfSet, System, Persistent

if sys.version_info[0] < 3:
	print ('python2 not supported, please use python3')
	sys.exit (0)

try:
	import requests
except:
	print ('please install requests library (pip3 install requests)')
	sys.exit (0)


ConfSet.addItem(ConfItem('chain.type', None, str, 'type of the chain'))
ConfSet.addItem(ConfItem('chain.name', None, str, 'name of the chain'))
ConfSet.addItem(ConfItem('tasks.autoRecover', False, bool, 'enable auto recoverable tasks'))
ConfSet.addItem(ConfItem('tasks.disabled', '', str, 'comma separated list of disabled tasks'))
ConfSet.addItem(ConfItem('chain.service', None, str, 'node service name'))
ConfSet.addItem(ConfItem('tasks.govAdmin', None, str, 'Proposal voter nickname'))


def addTasks(services):
	# Create the list of tasks
	tasks = []

	for x in TASKS + services.chain.CUSTOM_TASKS:
		task = x(services)
		if services.conf.getOrDefault('tasks.disabled').find(task.name) != -1:
			continue

		if task.isPluggable(services):
			tasks.append(task)
	return tasks

def defaultConf():
	print (ConfSet.help())


class Services:
	def __init__(self, conf, notification, system, chain, persistent):
		self.conf = conf
		self.notification = notification
		self.system = system
		self.chain = chain
		self.persistent = persistent

def main():
	cf = '/etc/srvcheck.conf'
	parser = argparse.ArgumentParser(description='Srvcheck helps you to monitor blockchain nodes.')
	parser.add_argument('--config', type=str, default=cf, help='srvcheck config file')
	args = parser.parse_args()
	cf = args.config

	# Parse configuration
	confRaw = configparser.ConfigParser()
	confRaw.optionxform=str
	confRaw.read(cf)

	conf = ConfSet(confRaw)
	conf.addItem(ConfItem('configFile', cf, str))

	# Get version
	version = srvcheck.__version__

	# Initialization
	notification = Notification (conf.getOrDefault('chain.name'))
	for x, v in NOTIFICATION_SERVICES.items():
		if conf.exists(f'notification.{x}.enabled') and conf.getOrDefault(f'notification.{x}.enabled', False):
			notification.addProvider (v(conf))

	print(f"starting monitor v{version} {Emoji.Start}")
	system = System(conf)
	print (system.getUsage())

	persistent = Persistent(os.environ['HOME'] + '/.srvcheck_persistent.json')


	# Get the chain by name or by detect
	chain = None
	tasks = []
	for x in CHAINS:
		if conf.getOrDefault('chain.type') == x.TYPE:
			chain = x(conf)
			services = Services(conf, notification, system, chain, persistent)
			tasks = addTasks(services)
			break

	if not chain:
		for x in CHAINS:
			if x.detect(conf):
				chain = x(conf)
				print ("Detected chain", chain.TYPE)
				services = Services(conf, notification, system, chain, persistent)
				tasks = addTasks(services)
				print(tasks)
				break

	if not chain:
		print ("No chain detected")
		sys.exit (0)

	notification.send(f"monitor v{version} started {Emoji.Start}\nDetected chain: {chain.TYPE}\nEnabled tasks: {reduce(lambda x, y: x + ', ' + y, [x.name for x in tasks])}")

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
					print (f'Error in task {t.name}: {traceback.format_exc()}')

				# Slows down srvcheck
				time.sleep(0.2)
				
		notification.flush()
		sys.stdout.flush()
		time.sleep(TTS)

if __name__ == "__main__":
	main()
