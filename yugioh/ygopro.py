"""
This is the front end for reading and writing ygopro .ydk deck lists,
as well as searching the ygopro database for cards.
"""

import os
from . import core

class YGOProError(RuntimeError): pass

def save_deck(deck, fl):
	"""save_deck(core.deck.YugiohDeck, file)
	
	takes a YugiohDeck, converts to ydk, and writes to a file."""
	fl.write(deck.as_ydk())

def deck_path(deck_name=None):
	"""deck_path(string) -> absolute path
	
	uses the paths module to turn the name of a deck as you would see it in ygopro, to a filename and absolute path."""
	if deck_name == None:
		return core.config.DECK_DIRECTORY
	else:
		if not deck_name.endswith('.ydk'):
			deck_name += '.ydk'
		return os.path.join(core.config.DECK_DIRECTORY, deck_name)


def load_deck(path, db_path=None):
	"""load_deck(absolute path deck, absolute path database) -> core.deck.YugiohDeck
	
	  opens and parses a .ydk file. Uses ygopro.YGOProDatabase to figure out what card cooresponds to the given card id. """
	  
	if not isinstance(path, str):
		raise TypeError('yugioh.ygopro.load_deck({0})'.format(path))
	name = os.path.basename(path)[:-4]
	db = core.database.database(db_path)
	main = []
	side = []
	extra = []
	author = ''
	current = main
	db.open()
	'''
	.ydk files have a very simple text only format.
	They are a list of card ids, interspersed by #comments that control
	what part of your deck the card ids are supposed to go in.
	They also support a mostly unused author tag.
	Also for some reason the side deck is !side instead of #side. iunno.
	'''
	with open(path) as fl:
		for line in fl:
			if line.startswith('#created by '):
				author = (line.rstrip())[11:]
			elif line.startswith('#main'):
				current = main
			elif line.startswith('#extra'):
				current = extra
			elif line.startswith('!side'):
				current = side
			else:
				cid = int(line.rstrip())
				card = db.find(cid)
				current.append(card)
	db.close()
	return core.deck.YugiohDeck(name, author, main, side, extra)

def load_card(name, db_path=None):
	"""load_card(string card_name, absolute path database) -> core.card.YugiohCard
	
	get the card with the given name from the ygopro database """
	db = core.database.database(db_path)
	card = db.find(name, by='name')
	db.close()
	if card == None:
		raise YGOProError('Could not find card {0}'.format(name))
	return card
