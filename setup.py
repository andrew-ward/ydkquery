#!/usr/bin/env python

from distutils.core import setup

setup(
	name='ydktools',
	version='0.1',
	description = 'Yugioh deck manipulation library',
	author = 'AW',
	url='https://github.com/aw-init/ydkquery',
	packages=['yugioh'],
	scripts=['convert', 'pricecheck']
)
