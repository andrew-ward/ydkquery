"""
Various functionality from all over the library, collected into one class. the Sessions class creates a YGOProDatabase used by most of the library as a card source. Most of the methods are simple function calls to different modules that require a YGOProDatabase object to work.
"""

import os

# for opening and closing decks
from . import deck as decklist

# for connecting and searching the ygopro database
from . import ygopro

# for yql selecting
from . import yql

# for getting price information
from . import yugiohprices

def _get_module(fmt):
	if fmt.endswith('ydk'):
		return decklist.ydk
	elif fmt.endswith('json'):
		return decklist.json
	else:
		return decklist.text

class Session(object):
	def __init__(self, ygopro_path):
		"""
		Create a Session object.
		:param ygopro_path: the path to the directory your YGOPro is installed in. If your install is broken up into multiple pieces, choose the one containing cards.cdb.
		"""
		self.path = ygopro_path
		self.db = None

	def __enter__(self):
		self.open()
		return self

	def __exit__(self, t, value, traceback):
		self.close()
		return False

	def open(self):
		"""
		Open a connection to the database. The database is opened automatically when another method is used that needs it.
		"""
		if self.db == None:
			db_path = os.path.join(self.path, 'cards.cdb')
			self.db = ygopro.YGOProDatabase(db_path)
		return self

	def close(self):
		"""
		Close the connection to the database.
		"""
		if self.db != None:
			self.db.close()
			self.db = None

	def get_database(self):
		"""
		Get the underlying database object. If no database is open, open one.
		"""
		if self.db == None:
			self.open()
		return self.db

	def search_path(self, flname):
		"""
		Search for a deck by filename. Will search the current directory and the ygopro deck directory. (Letting you create decks in ygopro, and then refer to them by name only)
		:param flname: The relative filename of a deck.
		:return: An absolute path to the deck, or None if not found.
		"""
		af = os.path.abspath(flname)
		if os.path.exists(af):
			return af

		trypath = os.path.abspath(os.path.join(self.path, 'deck', flname))
		if os.path.exists(trypath):
			return trypath
		else:
			return None

	def deck_path(self, flname):
		"""Get a filename as if it were in the ygopro deck directory"""
		return os.path.join(self.path, 'deck', flname)

	def open_deck(self, flname, fmt=None):
		"""
		Open a deck by filename.
		:param flname: The relative path of the filename. Uses search_path to find the file.
		:type flname: str
		:param fmt: If given, specifies a format that the deck is stored in. If not given, format will be autodetected based on extension.
		:type fmt: default None, 'ydk', 'json', or 'txt'
		"""
		source = self.get_database()
		mod = decklist if fmt==None else _get_module(fmt)
		path = self.search_path(flname)
		if path != None:
			return mod.open_deck(path, source)

	def load(self, text, fmt=None):
		"""
		Load a deck from a string.
		:param text: A string containing a deck list.
		:type text: string
		:param fmt: If given, specifies a format that the deck is stored in. If not given, format will be autodetected based on content.
		:type fmt: default None, 'ydk', 'json', or 'txt'
		"""
		source = self.get_database()
		mod = decklist if fmt==None else _get_module(fmt)
		return mod.load(text, source)

	def dump(self, deck, fmt='text'):
		"""
		Write out a YugiohDeck object to a string.
		:param deck: The deck to dump.
		:type deck: ygo.YugiohDeck
		:param fmt: Specify a format that the deck will be written in.
		:type fmt: default 'txt', 'ydk', or 'json'
		"""
		if not isinstance(deck, decklist.YugiohDeck):
			raise TypeError("Cannot dump an '{}' object to a decklist".format(deck.__class__.__name__))
		source = self.get_database()
		mod = _get_module(fmt)
		return mod.dump(deck)

	def save_deck(self, deck, path, fmt=None):
		"""
		Write out a YugiohDeck object to a file.
		:param deck: The deck to dump.
		:type deck: ygo.YugiohDeck
		:param path: The file path that the file is created at.
		:type path: string
		:param fmt: Specify a format that the deck will be written in. If None, autodetect the format based on the file extension of path.
		:type fmt: default None, 'txt', 'ydk', or 'json'
		"""
		if fmt == None:
			mod = decklist.detect_filename_format(path)
		else:
			mod = _get_module(fmt)
		text = mod.dump(deck)
		with open(path, 'w') as fl:
			fl.write(text)

	def find_name(self, name):
		"""
		Get a card with the given name
		:param cid: The card's name.
		:type cid: str
		:return: A YugiohCard object
		"""
		return self.get_database().find_name(name)

	def find_id(self, cid):
		"""
		Get a card with the given id
		:param cid: The card's id.
		:type cid: str or int
		:return: A YugiohCard object
		"""
		return self.get_database().find_id(cid)

	def all_cards(self):
		"""
		Get all cards in the database.
		:return: list of YugiohCards
		"""
		return self.get_database().all_cards()

	def yql(self, query, cardset=None):
		"""
		Perform a yql filter on the given cardset.
		:param query: The yql query to compile.
		:type query: str
		:param cardset: A sequence of cards to filter. If not given, use all_cards().
		:type cardset: default None, or iterable of YugiohCard
		:return: an iterable of YugiohCard
		"""
		cardset = cardset or self.all_cards()
		expr = yql.compile_yql(query)
		return expr.filter(cardset)

	def price_data(self, card):
		"""
		Get the average price of the cheapest version of the card. Uses the public api for the incredible yugiohprices.com price aggregator.
		:param card: The card you want to know the price of.
		:type card: YugiohCard
		:return: a list of PrintedCard objects containing information about each print run of the given card.
		:rtype: list of ygo.prices.PrintedCard
		"""
		cards = yugiohprices.get_price_data(card)
		return decklist.YugiohSet(cards)

	def get_price(self, card):
		"""
		Get the average price of the cheapest version of the card. Uses the public api for the incredible yugiohprices.com price aggregator.
		:param card: The card you want to know the price of.
		:type card: YugiohCard
		:return: the price of the card
		:rtype: float
		"""
		cards = yugiohprices.get_price_data(card)
		return yugiohprices.get_cheapest_price(cards)
		
		
