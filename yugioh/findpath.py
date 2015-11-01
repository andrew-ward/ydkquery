"""
This module is for local file manipulation of deck list files. Mostly implements a "search path" for deck lists that looks in the ygopro/deck/ directory if a deck isn't found. May add some more utility functions here later.

"""

import os
from . import ygopro

def find_deck(path):
	"""Determine location of the deck file. If it can't find the deck, search the ygopro deck directory.
	
:param path: expected path to the deck
:type path: string
:returns: absolute path to the deck. Return None if not found.
:rtype: string"""
	_, ext = os.path.splitext(path)
	if ext == '':
		path = path + '.ydk'
	for subpath in [os.path.abspath(path), ygopro.deck_path(path)]:
		if os.path.exists(subpath):
			return subpath
	raise IOError('No file found named {0}'.format(path))

def find_format(path):
	"""Determine format of the deck file. (.ydk, .txt, and .md are currently supported)
	
:param path: expected path to the deck
:type path: string
:returns: extension format of the deck.
:rtype: string"""
	deckpath = find_deck(path)
	_, ext = os.path.splitext(deckpath)
	if ext == '':
		return '.ydk'
	else:
		return ext
