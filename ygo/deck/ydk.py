"""
This is the front end for reading and writing ygopro .ydk deck lists,
as well as searching the ygopro database for cards.
"""

from .deck import YugiohDeck

def open_deck(path, card_source):
	"""Opens and parses a .ydk file. 
	
:param path: absolute path to the deck
:type path: string
:param card_source: some database that allows finding cards by name
:type card_source: core.ygopro.YGOProDatabase
:returns: the deck
:rtype: decklist.deck.YugiohDeck"""
	with open(path, 'r') as fl:
		text = fl.read()
		return load(text, card_source)

def load(text, card_source):
	"""Parses a .ydk file. 
	
:param text: the contents of the decklist file as text
:type text: string
:param card_source: some database that allows finding cards by name
:type card_source: core.ygopro.YGOProDatabase
:returns: the deck
:rtype: core.deck.YugiohDeck"""
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
		line = line.rstrip()
		if line.startswith('#created by'):
			author = line[11:].strip()
		elif line.startswith('#main'):
			current = main
		elif line.startswith('#extra'):
			current = extra
		elif line.startswith('!side'):
			current = side
		else:
			cid = line.rstrip()
			card = card_source.find_id(cid)
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
	for card in deck.extra.enumerate():
		output.append(card.cid)
	output.append('!side')
	for card in deck.side.enumerate():
		output.append(card.cid)
	return '\n'.join(output)

