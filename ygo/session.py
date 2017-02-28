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
		self.path = ygopro_path
		self.db = None

	def __enter__(self):
		self.open()
		return self

	def __exit__(self, t, value, traceback):
		self.close()
		return False

	def open(self):
		if self.db == None:
			db_path = os.path.join(self.path, 'cards.cdb')
			self.db = ygopro.YGOProDatabase(db_path)
		return self

	def close(self):
		if self.db != None:
			self.db.close()
			self.db = None

	def get_database(self):
		if self.db == None:
			self.open()
		return self.db

	def search_path(self, flname):
		if os.path.exists(flname):
			return flname

		trypath = os.path.join(self.path, 'deck', flname)
		if os.path.exists(trypath):
			return trypath
		else:
			return None

	def deck_path(self, flname):
		return os.path.join(self.path, 'deck', flname)

	def open_deck(self, flname, fmt=None):
		source = self.get_database()
		mod = decklist if fmt==None else _get_module(fmt)
		path = self.search_path(flname)
		if path != None:
			return mod.open_deck(flname, source)

	def load(self, text, fmt=None):
		source = self.get_database()
		mod = decklist if fmt==None else _get_module(fmt)
		return mod.load(text, source)

	def dump(self, deck, fmt='text'):
		source = self.get_database()
		mod = _get_module(fmt)
		return mod.dump(deck)

	def save_deck(self, deck, path):
		mod = decklist.detect_filename_format(path)
		text = mod.dump(deck)
		with open(path, 'w') as fl:
			fl.write(text)

	def find_name(self, name):
		return self.get_database().find_name(name)

	def find_id(self, cid):
		return self.get_database().find_id(cid)

	def all_cards(self):
		return self.get_database().all_cards()

	def yql(self, query, cardset=None):
		cardset = cardset or self.all_cards()
		expr = yql.compile_yql(query)
		return expr.filter(cardset)

	def price_data(self, card):
		cards = yugiohprices.get_price_data(card)
		return decklist.YugiohSet(cards)
		
		
