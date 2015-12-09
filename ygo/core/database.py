import sqlite3 as sqlite

from . import enum, card, deck, config, search_interface

class CardNotFoundException(RuntimeError):
	pass
	
class InvalidQueryError(RuntimeError):
	pass
	
class YGOProDatabase(search_interface.CardRetriever):
	"""a wrapper around an sqlite connection to the cards.cdb database."""
	def __init__(self, cardscdb=None):
		self.db_path = cardscdb or config.DATABASE_PATH
		
		if self.db_path == None:
			raise IOError('Cannot access database. Check your configuration.')
		
		# with most of the query methods, it will open a connection if you
		# don't already have one - even if you explicitly closed it.
		self.connection = None
		
		# if you ask for every card in the database, you don't want to
		# have to do it twice. That's what this is for.
		self.__all_card_cache = None
		
	def find(self, card_key):
		if isinstance(card_key, card.YugiohCard):
			return card_key
		flag = False
		try:
			flag = card_key.isdigit()
		except AttributeError:
			raise InvalidQueryError('"{0}" is not a valid card key'.format(repr(card_key)))
		if flag:
			return self.find_id(card_key)
		#elif re.match('^[0-9A-Z]+-[A-Z]+[0-9]*$', card_key):
		#	return self._find_print_tag(card_key)
		else:
			return self.find_name(card_key)
			
	def all_cards(self):
		return self.find_all()

		
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
			
	def __make_card(self, row):
		return YGOProCard.from_row(row)
			
	def find_name(self, name):
		if self.connection == None:
			self.open()			
		name = unicode(name, 'utf-8')
		cursor = self.connection.cursor()
		query = u'''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.name LIKE ?'''
		cursor.execute(query, [name])
		for row in cursor:
			return self.__make_card(row)
		raise CardNotFoundException('Could not find card with name {0}'.format(name))
			
	def find_id(self, cid):
		if self.connection == None:
			self.open()			
		
		cursor = self.connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.id = ?'''
		cursor.execute(query, [cid])
		for row in cursor:
			return self.__make_card(row)
		raise CardNotFoundException('Could not find card with id#{0}'.format(cid))
			
	def find_sql(self, expr, anime=False):
		if self.connection == None:
			self.open()			
		
		cursor = self.connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND '''
		if not anime:
			query += 'datas.ot < 4 AND '
		query += expr
		cursor.execute(query)
		return [self.__make_card(row) for row in cursor]
		
	def find_all(self, anime=False):
		if self.connection == None:
			self.open()			
		
		cursor = self.connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id'''
		if not anime:
			query += ' AND datas.ot < 4'
		cursor.execute(query)
		return deck.YugiohSet(self.__make_card(row) for row in cursor)

class YGOProCard(card.YugiohCard):
	"""A YugiohCard with extra information from the ygopro database.
	
	:ivar alias: This marks cards with multiple artworks
	:vartype alias: int
	:ivar availability: get the location that this card is playable in. (i.e. TCG exclusive, OCG exclusive, Anime card, etc)
	:vartype availability: "Any" or "TCG" or "OCG" or "Anime"
	:ivar setcode: This marks what archetype a card belongs to. If two cards have the same setcode, they belong to the same archetypes. The reverse is not neccesarily true.
	:vartype setcode: int"""
	
	@staticmethod
	def from_row(row):
		"""Construct a new YugiohCard with a database row.

		:param banlist_data: information about the current banlist
		:type banlist_data: banlist.Banlist
		:param row: a row from the sql database
		:type row: name, desc, id, ot, alias, setcode, type, atk, def, level, race, attribute, category"""
		if row == None:
			raise TypeError('Cannot create a YGOProCard from None')
			
		
		name = row[0] # unicode
		text = row[1] # unicode
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
			
		return YGOProCard(
			name, text, str(cid),
			availability, alias, setcode,
			category, attribute, monster_type,
			attack, defense, level, left_scale, right_scale)

	

	def __init__(self, name, text, cid, ot, alias, setcode, category, attribute, race, attack, defense, level, lscale=None, rscale=None):
		card.YugiohCard.__init__(self, name, text, cid, category, attribute, race, attack, defense, level, lscale, rscale)
		
		self.alias = alias
		
		self.availability = enum.get_string('banlist', ot)
		
		self.setcode = setcode
