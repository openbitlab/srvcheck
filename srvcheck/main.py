#!/usr/bin/python3
import sys 
import time
import argparse

from srvcheck.notification import Notification
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


def main():
	# Parse configuration

	# Initialization
	notification = Notification () #args.apiToken, args.chatIds)
	system = System()
	chain = None 
	print (system.getUsage())

	for x in CHAINS:
		if x.detect():
			chain = x()
			print ("Detected chain %s", chain.NAME)
			break

	# Create the list of tasks
	tasks = []
	tasks.append(TaskChainStuck(notification, system, chain))
	tasks.append(TaskSystemUsage(notification, system, chain))
	tasks.append(TaskSystemUsageAlert(notification, system, chain))

	# Mainloop
	TTS = 60

	while True:
		for t in tasks:
			if t.shouldBeChecked():
				t.run()

		notification.flush()
		time.sleep(TTS)

if __name__ == "__main__":
	main()