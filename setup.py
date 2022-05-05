# -*- coding: utf-8 -*-
# Copyright (C) 2019 Davide Gessa

from setuptools import find_packages
from setuptools import setup

setup(name='srvcheck',
	version='0.1',
	description='',
	author=['Davide Gessa'],
	setup_requires='setuptools',
	author_email=['gessadavide@gmail.com'],
	packages=[
		'srvcheck',
		'srvcheck.chains',
		'srvcheck.utils',
		'srvcheck.tasks',
		'srvcheck.notification'
	],
	entry_points={
		'console_scripts': [
			'srvcheck=srvcheck.main:main',
		],
	},
    zip_safe=False,
	install_requires=['requests'],
)