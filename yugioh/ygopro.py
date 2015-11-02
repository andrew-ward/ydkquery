"""
This is the front end for reading and writing ygopro .ydk deck lists,
as well as searching the ygopro database for cards.
"""

import os
from . import core

class YGOProError(RuntimeError): pass

def save_deck(deck, fl):
	"""Write the given deck to file as a ydk.
	
:param deck: the deck
:type deck: core.deck.YugiohDeck
:param fl: the output file
:type fl: file
:returns: None"""
	fl.write(deck.as_ydk())

def deck_path(deck_name=None):
	"""Get path to deck in the ygopro deck directory from deck name.

:param deck_name: the name of the deck.
:type deck_name: string
:returns: absolute path into the ygopro deck directory
:rtype: string"""
	if deck_name == None:
		return core.config.DECK_DIRECTORY
	else:
		if not deck_name.endswith('.ydk'):
			deck_name += '.ydk'
		return os.path.join(core.config.DECK_DIRECTORY, deck_name)


def load_deck(path, db_path=None):
	"""Opens and parses a .ydk file. Uses ygopro.YGOProDatabase to figure out what card cooresponds to the given card id. 
	
:param path: absolute path to the deck
:type path: string
:param db_path: absolute path to the ygopro card database
:type db_path: string
:returns: the deck
:rtype: core.deck.YugiohDeck"""
	  
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

def load_card(name, by='guess', db_path=None):
	"""Get the card with the given name from the ygopro database.
	
:param path: full name of the card
:type path: string
:param by: how you want to get the card.
:type by: "name" or "id"
:param db_path: absolute path to the ygopro card database
:type db_path: string
:returns: the card
:rtype: core.card.YugiohCard
:raises: core.database.CardNotFoundException"""
	with core.database.database(db_path) as db:
		if by == 'guess':
			if name.isdigit():
				return db.find(name, by='id')
			else:
				return db.find(name, by='name')
		else:
			return db.find(name, by=by)
	


def database(db_path=None):
	"""Get a new handle to the ygopro card database.
	
:param db_path: absolute path to the ygopro card database
:type db_path: string
:returns: the database handle
:rtype: core.database.YGOProDatabase"""
	return core.database.database(db_path)

def all_cards(db_path=None):
	"""Get all cards in the ygopro database.
	
:param db_path: absolute path to the ygopro card database
:type db_path: string
:returns: list of every card in the database
:rtype: list of core.database.YGOProCard"""
	return core.database.all_cards(db_path)
