#!/usr/bin/python3
import sys
import time
import configparser
import traceback
import argparse
from functools import reduce
import srvcheck

from .notification import Emoji, Notification, NOTIFICATION_SERVICES
from .tasks import TASKS
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


ConfSet.addItem(ConfItem('chain.type', None, str, 'type of the chain'))
ConfSet.addItem(ConfItem('chain.name', None, str, 'name of the chain'))
ConfSet.addItem(ConfItem('tasks.autoRecover', False, bool, 'enable auto recoverable tasks'))
ConfSet.addItem(ConfItem('tasks.disabled', '', str, 'comma separated list of disabled tasks'))
ConfSet.addItem(ConfItem('chain.service', None, str, 'node service name'))


def addTasks(chain, notification, system, config):
	# Create the list of tasks
	tasks = []

	for x in TASKS + chain.CUSTOM_TASKS:
		task = x(config, notification, system, chain)
		if config.getOrDefault('tasks.disabled').find(task.name) != -1:
			continue

		if task.isPluggable(config, chain):
			tasks.append(task)
	return tasks

def defaultConf():
	print (ConfSet.help())

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
				print ("Detected chain", chain.TYPE)
				tasks = addTasks(chain, notification, system, conf)
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

		notification.flush()
		sys.stdout.flush()
		time.sleep(TTS)

if __name__ == "__main__":
	main()
