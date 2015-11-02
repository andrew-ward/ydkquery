import sqlite3 as sqlite

from . import enum
from . import card
from . import deck
from . import banlist
from . import config

class CardNotFoundException(RuntimeError):
	pass
	
class InvalidQueryError(RuntimeError):
	pass

class YGOProDatabase(object):
	"""a wrapper around an sqlite connection to the cards.cdb database."""
	def __init__(self, cardscdb=None, banlists = None):
		self.db_path = cardscdb or config.DATABASE_PATH
		
		# a list of banlist.Banlist objects.
		self.banlist_data = banlists or banlist.load_banlists(config.BANLIST_PATH)
		
		if self.db_path == None:
			raise IOError('Cannot access database at {0}'.format(self.db_path))
		
		# with most of the query methods, it will open a connection if you
		# don't already have one - even if you explicitly closed it.
		self.connection = None
		
		# if you ask for every card in the database, you don't want to
		# have to do it twice. That's what this is for.
		self.__all_card_cache = None
		
	def open(self):
		"""Open a new connection with the database."""
		if self.connection == None:
			try:
				self.connection = sqlite.connect(self.db_path)
			except sqlite.OperationalError as soe:
				raise sqlite.OperationalError('unable to open database file "{0}"'.format(self.db_path))
		return self
	def close(self):
		"""Close the connection. If the database is closed, it can still reopen. If you try to find something with a closed database, it will be reopened."""
		if self.connection != None:
			self.connection.close()
			self.connection = None
		
	# allow using the database in a "with YGOProDatabase() as db:" form
	def __enter__(self):
		return self.open()
	def __exit__(self, t, value, traceback):
		self.close()
		return False
		
	def __del__(self):
		self.close()
			
	def __make_card(self, row):
		return YGOProCard.from_row(self.banlist_data, row)
			
	def find(self, arg, by='id'):
		"""Find a card given a certain parameter.

	:param arg: the search query. See 'by' for what goes here.
	:type arg: string or int
	:param by: 
		* id: find the card with the given card id
		* name: find the card with the given name.
		
	:type by: "id" or "name"
	:returns: the first card that matches the query.
	:rtype: YGOProCard
	:raises: database.CardNotFoundException
	:raises: database.InvalidQueryError"""
		if self.connection == None:
			self.open()
		if by == 'id':
			if isinstance(arg, str) and any(c.isalpha() for c in arg):
				raise TypeError('Invalid card id "{0}"'.format(arg))
			query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.id = ?'''
		elif by == 'name':
			query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.name LIKE ?'''
		else:
			raise InvalidQueryError('Invalid query type ({0})'.format(by))
		cursor = self.connection.cursor()
		cursor.execute(query, [arg])
		row = cursor.fetchone()
		if row:
			return self.__make_card(row)
		elif by=='id':
			raise CardNotFoundException('No card with id {0} exists'.format(arg))
		elif by=='name':
			raise CardNotFoundException('No card named {0} exists'.format(arg))
		else:
			raise NotImplementedError('wtf')
		
	def find_all(self, args, by='id'):
		"""Find multiple cards given a certain parameter.

	:param args: an iterable of search queries. See 'by' for what goes here.
	:type args: list of (string or int)
	:param by: 
		* id: find the card with the given card id
		* name: find the card with the given name. Supports sql patterns.	
	
	:type by: "id" or "name"
	:returns: all cards that match the query.
	:rtype: iterable of YGOProCard
	:raises: database.InvalidQueryError"""
		if self.connection == None:
			self.open()
		for arg in args:
			try:
				r = self.find(arg, by)
				if r != None:
					yield r
			except CardNotFoundException:
				continue
			
	def search(self, arg, by='name'):
		"""Find multiple given constraints.

	:param arg: the search query. See 'by' for what goes here.
	:type arg: string or int
	:param by: 
		* name: use sql patterns to match the card name.
		* text: use sql patterns to match the card test.
		* sql: use arbitrary sql expressions to match a database row.
		
	:type by: "name" or "text" or "Sql"
	:returns: all cards that match the query.
	:rtype: iterable of YGOProCard
	:raises: database.InvalidQueryError"""

		if self.connection == None:
			self.open()
		cursor = self.connection.cursor()
		if by == 'name':
			query = '''
				SELECT texts.name, texts.desc, datas.*
				FROM texts, datas
				WHERE texts.id = datas.id AND texts.name LIKE ?'''
			cursor.execute(query, [arg])
		elif by == 'text':		
			query = '''
				SELECT texts.name, texts.desc, datas.*
				FROM texts, datas
				WHERE texts.id = datas.id AND texts.desc LIKE ?'''
			cursor.execute(query, [arg])
		elif by == 'sql':
			query = '''SELECT texts.name, texts.desc, datas.*
				FROM texts, datas
				WHERE texts.id = datas.id AND {0}'''.format(arg)
			cursor.execute(query)
		else:
			raise InvalidQueryError('Invalid database search type ({0})'.format(by))		
		for row in cursor:
			yield self.__make_card(row)
			
	def all_cards(self, anime=False):
		"""Get every card available in the database. This will be really slow the first time you call it, but the results are cached so subsequent calls should be reasonably fast.
		
		:param anime: if true, returns anime-only cards as well.
		:returns: list of every yugioh card.
		:rtype: list of YGOProCard"""
		if self.__all_card_cache == None:
			if self.connection == None:
				self.open()
			cursor = self.connection.cursor()
			query = '''
				SELECT texts.name, texts.desc, datas.*
				FROM texts, datas
				WHERE texts.id = datas.id''' + ' AND datas.ot < 4' if not anime else ''
			cursor.execute(query)
			self.__all_card_cache = [self.__make_card(row) for row in cursor]
		return self.__all_card_cache
	
	def get_new_id(self):
		"""Get a new card id that does not conflict with any existing cards.
		
		:returns: an unused card id.
		:rtype: string"""
		# useful for making your own cards, though currently there isn't
		# any other support for it.
		if self.connection == None:
			self.open()
		query = '''SELECT max(datas.id) FROM datas'''
		cursor = self.connection.cursor()
		cursor.execute(query)
		result = cursor.fetchone()
		return str(result[0] + 1)

class YGOProCard(card.YugiohCard):
	"""A YugiohCard with extra information from the ygopro database.
	
	:ivar alias: This marks cards with multiple artworks
	:vartype alias: int
	:ivar availability: get the location that this card is playable in. (i.e. TCG exclusive, OCG exclusive, Anime card, etc)
	:vartype availability: "Any" or "TCG" or "OCG" or "Anime"
	:ivar setcode: This marks what archetype a card belongs to. If two cards have the same setcode, they belong to the same archetypes. The reverse is not neccesarily true.
	:vartype setcode: int"""
	
	@staticmethod
	def from_row(banlist_data, row):
		"""Construct a new YugiohCard with a database row.

		:param banlist_data: information about the current banlist
		:type banlist_data: banlist.Banlist
		:param row: a row from the sql database
		:type row: name, desc, id, ot, alias, setcode, type, atk, def, level, race, attribute, category"""
		if row == None:
			raise TypeError('Cannot create a YGOProCard from None')
			
		name = row[0]
		text = row[1]
		cid = row[2]
		
		availability = row[3]
		alias = row[4]
		setcode = row[5]
		
		attack = row[7]
		defense = row[8]
		
		try:
			category = enum.get_string('category', row[6])
			attribute = enum.get_string('attribute', row[11])
			monster_type = enum.get_string('type', row[10])
		except enum.EnumError as enum_err:
			raise enum.EnumError('While creating card {0} '+str(enum))
			
		raw_level = row[9]
		level = None
		left_scale = None
		right_scale = None
		if raw_level < 14:
			level = raw_level
		else:
			# extract pendulum scales from level column.
			hxstr = hex(raw_level)
			level = int(hxstr[8], 16)
			left_scale = int(hxstr[2], 16)
			right_scale = int(hxstr[4], 16)
			
		if 'Monster' not in category:
			level = None
			left_scale = None
			right_scale = None
			attack = None
			defense = None
			
		half_built_card = YGOProCard(
			name, text, str(cid), None,
			availability, alias, setcode,
			category, attribute, monster_type,
			attack, defense, level, left_scale, right_scale)
		
		# for each banlist, record how many copies of this card are allowed.
		# doing this backward to allow for expanding banlist data sources
		allowed = {}
		for banlist in banlist_data:
			allowed[banlist.name.upper()] = banlist.allowed(half_built_card)
			
		half_built_card._banlist_status = allowed
		
		return half_built_card
	

	def __init__(self, name, text, cid, blist_info, ot, alias, setcode, category, attribute, race, attack, defense, level, lscale=None, rscale=None):
		card.YugiohCard.__init__(self, name, text, cid, blist_info, category, attribute, race, attack, defense, level, lscale, rscale)
		
		self.alias = alias
		
		self.availability = enum.get_string('banlist', ot)
		
		self.setcode = setcode
	


def database(db_path = None):
	"""Returns a new database instance to use to search for cards.
	
	:returns: a new database handle.
	:rtype: YGOProDatabase"""
	db = YGOProDatabase(db_path)
	db.open()
	return db

def all_cards(db_path = None):
	"""Get every card available in the database
	
	:returns: every card in the database.
	:rtype: list of YGOProCard"""
	db = database(db_path)
	return db.all_cards()
