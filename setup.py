#!/usr/bin/env python

from distutils.core import setup

def readme():
	with open('README.md') as fl:
		return fl.read()

setup(
	name='YDKTools',
	description = 'Yugioh deck manipulation library',
	long_description = readme(),
	
	version='0.1',


	author='aw-init',
	author_email='init.697370@gmail.com',
	
	url='https://github.com/aw-init/ydktools',
	
	license='MIT',
	
	packages=['yugioh'],
	scripts=['convert', 'pricecheck'],
)
