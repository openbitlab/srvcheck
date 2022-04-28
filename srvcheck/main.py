#!/usr/bin/python3
import sys 
import argparse
from .utils import Node
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
	node = Node()
	chain = None 
	print (node.getUsage())

	for x in CHAINS:
		if x.detect():
			chain = x()
			break

	print ("Detected chain %s", chain.NAME)



if __name__ == "__main__":
	main()