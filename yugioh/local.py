"""
This module is for local file manipulation of deck list files. Mostly implements a "search path" for deck lists that looks in the ygopro/deck/ directory if a deck isn't found. May add some more utility functions here later.

"""

import os
import ygopro

def find_deck(path):
	"""find_deck(path) -> absolute path
	determine location of the deck file """
	for subpath in [path, ygopro.deck_path(path)]:
		if os.path.exists(subpath):
			return subpath
	return None

def find_format(path):
	"""find_format(path) -> file extension
	find what format the given deck is saved in."""
	deckpath = find_deck(path)
	_, ext = os.path.splitext(deckpath)
	if ext == '':
		return '.ydk'
	else:
		return ext
