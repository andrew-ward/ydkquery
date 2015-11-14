import os
import json
from .core.deck import YugiohDeck, YugiohSet
from . import search

class YGOJsonParseError(RuntimeError):
	pass

def _load_set(tree, card_source):
	result = []
	for key, count in tree.items():
		card = card_source.find(key)
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
	return YugiohDeck(name, author, main, side, extra)
	
def load(text, card_source=None):
	card_source = card_source or search.get_source()
	tree = json.loads(text)
	return _load_deck(tree, card_source)

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

def dump(thing):
	if isinstance(thing, YugiohDeck):
		return json.dumps(_convert_deck(thing))
	elif isinstance(thing, YugiohSet):
		yset = json.dumps(_convert_set(thing))
		return YugiohDeck('', '', yset, [], [])
	else:
		return json.dumps(thing)
