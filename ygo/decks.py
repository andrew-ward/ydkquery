import os, sys
from .core import config, database
from . import decklist, ydk, ygojson, search
import warnings

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
	
	
INPUT_FORMATS = {
	'txt' : decklist.load,
	'json' : ygojson.load,
	'ydk' : ydk.load
}

def loads(text, fmt=None):
	"Convert a string from a decklist format into a YugiohDeck object"
	if fmt in INPUT_FORMATS:
		return INPUT_FORMATS[fmt](text)
	else:
		if text[0] in '[{':
			return INPUT_FORMATS['json'](text)
		else:
			return INPUT_FORMATS['txt'](text)

def open_deck(path):
	"""Load a deck of any supported format from the given path. Checks current direcory, and then the ygopro decks directory."""
	if not os.path.exists(path):
		ypath = deck_path(path)
		if not os.path.exists(ypath):
			raise RuntimeError('Could not find deck {}'.format(path))
		else:
			path = ypath
	fmt = ''
	_, ext = os.path.splitext(path)
	if ext == '' or ext == '.ydk':
		fmt = 'ydk'
	elif ext == '.json':
		fmt = 'json'
	else:
		fmt = 'txt'
		
	with open(path) as fl:
		text = fl.read()
		return loads(text, fmt)

	
	
OUTPUT_FORMATS = {
	'txt' : decklist.dump,
	'json' : ygojson.dump,
	'ydk' : ydk.dump
}

def dumps(deck, fmt='ydk'):
	"Convert a YugiohDeck to a decklist format string. path can be a filepath with extension, or a format string (txt/json/ydk)"
	if fmt in OUTPUT_FORMATS:
		return OUTPUT_FORMATS[fmt](deck)
	else:
		raise RuntimeError('Unsupported format {}'.format(fmt))
		

def save_deck(deck, path):
	"Convert a deck object to a text format, and write it to a file. Determines location and format of output based on path. Mostly exists to automatically save files to ygopro/decks directory"
	if path in OUTPUT_FORMATS:
		fmt = path
		dest = None
	else:
		_, ext = os.path.splitext(path)
		dest = path
		if ext == '' or ext == '.ydk':
			fmt = 'ydk'
		elif ext == '.json':
			fmt = 'json'
		else:
			fmt = 'txt'
	text = dumps(deck, fmt)
	if dest != None:
		head, tail = os.path.split(path)
		if head == '':
			dest = deck_path(tail)
		else:
			dest = path
		with open(dest, 'w') as fl:
			fl.write(text)
	else:
		sys.stdout.write(text)
		
