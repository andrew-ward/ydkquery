"""
This is the front end for reading and writing ygopro .ydk deck lists,
as well as searching the ygopro database for cards.
"""

import os
from .core.deck import YugiohDeck
from . import search

def load(text, card_source=None):
	"""Opens and parses a .ydk file. 
	
:param path: absolute path to the deck
:type path: string
:param db_path: absolute path to the ygopro card database
:type db_path: string
:returns: the deck
:rtype: core.deck.YugiohDeck"""
	card_source = card_source or search.get_source()
	main = []
	side = []
	extra = []
	author = ''
	title = ''
	current = main
	'''
	.ydk files have a very simple text only format.
	They are a list of card ids, interspersed by #comments that control
	what part of your deck the card ids are supposed to go in.
	They also support a mostly unused author tag.
	Also for some reason the side deck is !side instead of #side. iunno.
	'''
	for line in text.splitlines():
		if line.startswith('#created by '):
			author = (line.rstrip())[11:]
		elif line.startswith('#main'):
			current = main
		elif line.startswith('#extra'):
			current = extra
		elif line.startswith('!side'):
			current = side
		else:
			cid = line.rstrip()
			card = card_source.find(cid)
			current.append(card)
	return YugiohDeck(title, author, main, side, extra)
	
def dump(deck):
	"""
	:returns: the deck as .ydk formatted text.
	:rtype: string"""
	output = []
	output.append('#created by {0}'.format(deck.author))
	output.append('#main')
	for card in deck.main.enumerate():
		output.append(card.cid)
	output.append('#extra')
	for card in self.extra.enumerate():
		output.append(card.cid)
	output.append('!side')
	for card in self.side.enumerate():
		output.append(card.cid)
	return '\n'.join(output)

