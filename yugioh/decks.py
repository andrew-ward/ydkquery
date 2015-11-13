import os, sys
from .core import config, database
from . import decklist, ydk, ygojson, search

def deck_path(deck_name=None):
	"""Get path to deck in the ygopro deck directory from deck name.

:param deck_name: the name of the deck.
:type deck_name: string
:returns: absolute path into the ygopro deck directory
:rtype: string"""
	if not config.DECK_DIRECTORY:
		raise IOError('Deck Directory is not properly configured. Check your configuration.')
		
	if deck_name == None:
		return config.DECK_DIRECTORY
	else:
		if not deck_name.endswith('.ydk'):
			deck_name += '.ydk'
		return os.path.join(config.DECK_DIRECTORY, deck_name)

def find_deck(path):
	"""Determine location of the deck file. If it can't find the deck, search the ygopro deck directory.
	
:param path: expected path to the deck
:type path: string
:returns: absolute path to the deck. Return None if not found.
:rtype: string"""
	_, ext = os.path.splitext(path)
	if ext == '':
		path = path + '.ydk'
	for subpath in [os.path.abspath(path), deck_path(path)]:
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
		return 'ydk'
	elif ext.startswith('.'):
		return ext[1:]
	else:
		return ext
	
	
INPUT_FORMATS = {
	'txt' : decklist.load,
	'json' : ygojson.load,
	'ydk' : ydk.load
}

def load(text, fmt=None):
	if fmt in INPUT_FORMATS:
		return INPUT_FORMATS[fmt](text)
	else:
		if text[0] in '[{':
			return INPUT_FORMATS['json'](text)
		else:
			return INPUT_FORMATS['txt'](text)

def open_deck(path):
	"""Load a deck of any supported format from the given path. Checks current direcory, and then the ygopro decks directory."""
	if path in INPUT_FORMATS:
		text = sys.stdin.read()
		fmt = path
	else:
		abspath = find_deck(path)
		fmt = find_format(path)
		with open(abspath) as fl:
			text = fl.read()
	return INPUT_FORMATS[fmt](text)
	
	
OUTPUT_FORMATS = {
	'txt' : decklist.dump,
	'json' : ygojson.dump,
	'ydk' : ydk.dump
}

def dump(deck, path):
	if path in OUTPUT_FORMATS:
		fmt = path
	else:
		root, ext = os.path.splitext(path)
		if ext == '':
			fmt = 'ydk'
		elif ext[1:] in OUTPUT_FORMATS:
			fmt = ext[1:]
		else:
			raise NotImplementedError('Output format {} is not supported.'.format(ext))	
	return OUTPUT_FORMATS[fmt](deck)
		

def save_deck(deck, path):
	text = dump(deck, path)
	if path in OUTPUT_FORMATS:
		dest = None
	else:
		head, tail = os.path.split(path)
		if head == '':
			dest = deck_path(tail)
		else:
			dest = path
	if dest:
		with open(dest, 'w') as fl:
			fl.write(text)
	else:
		sys.stdout.write(text)
		
