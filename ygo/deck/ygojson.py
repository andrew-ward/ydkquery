import os
import json
from .deck import YugiohDeck, YugiohSet

class YGOJsonParseError(RuntimeError):
	pass

def open_deck(path, card_source):
	"""Opens and parses a .json file. 
	
:param path: absolute path to the deck
:type path: string
:param card_source: some database that allows finding cards by name
:type card_source: core.ygopro.YGOProDatabase
:returns: the deck
:rtype: decklist.deck.YugiohDeck"""
	with open(path, 'r') as fl:
		text = fl.read()
		return load(text, card_source)

def load(text, card_source=None):
	"""Parses a .json file. 
	
:param text: the contents of the decklist file as text
:type text: string
:param card_source: some database that allows finding cards by name
:type card_source: core.ygopro.YGOProDatabase
:returns: the deck
:rtype: core.deck.YugiohDeck"""
	card_source = card_source or search.get_source()
	tree = json.loads(text)
	return _load_deck(tree, card_source)

def dump(thing):
	"""
	:returns: the deck as a string of json
	:rtype: string"""
	if isinstance(thing, YugiohDeck):
		return json.dumps(_convert_deck(thing))
	elif isinstance(thing, YugiohSet):
		yset = json.dumps(_convert_set(thing))
		return YugiohDeck('', '', yset, [], [])
	else:
		return json.dumps(thing)

def _load_set(tree, card_source):
	result = []
	for key, count in tree.items():
		card = card_source.find_name(key)
		for i in range(count):
			result.append(card)
	return YugiohSet(result)

def _is_not_ygojson_deck(tree):
	return not all(tag in tree for tag in ['main', 'side', 'extra', 'author', 'name'])
	
			
def _load_deck(tree, card_source):
	if _is_not_ygojson_deck(tree):		
		raise YGOJsonParseError('Deck object does not contain all the neccesary tags')
	main = _load_set(tree['main'], card_source)
	side = _load_set(tree['side'], card_source)
	extra = _load_set(tree['extra'], card_source)
	name = tree['name']
	author = tree['author']
	return YugiohDeck(main, side, extra, name, author)
	


def _convert_set(ygoset):
	return dict((card.name, ygoset.count(card)) for card in ygoset)

def _convert_deck(deck):
	return {
		'name' : deck.name,
		'author' : deck.author,
		'main' : _convert_set(deck.main),
		'extra' : _convert_set(deck.side),
		'side' : _convert_set(deck.extra),
	}
