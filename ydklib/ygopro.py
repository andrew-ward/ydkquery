import ygoenum
import ygocard
import sqlite3 as sqlite
import paths


class YGOProDatabase(object):
	'''a wrapper around an sqlite connection to the cards.cdb database.'''
	def __init__(self, cardscdb = None):
		self.db_path = cardscdb or paths.database()
		
		# with most of the query methods, it will open a connection if you
		# don't already have one - even if you explicitly closed it.
		self.connection = None
		
		# if you ask for every card in the database, you don't want to
		# have to do it twice. That's what this is for.
		self.__all_card_cache = None
		
	def open(self):
		''' open a new connection with the database'''
		if self.connection == None:
			try:
				self.connection = sqlite.connect(self.db_path)
			except sqlite.OperationalError as soe:
				raise sqlite.OperationalError('unable to open database file "{0}"'.format(self.db_path))
		return self
		
	def close(self):
		'''Close the connection. If the database is closed, it can still reopen. If you try to find something with a closed database, it will be reopened.'''
		if self.connection != None:
			self.connection.close()
			self.connection = None
		
	# allow using the database in a "with YGOProDatabase() as db:" form
	def __enter__(self):
		return self.open()
	def __exit__(self, t, value, traceback):
		self.close()
		return False
			
	def find(self, arg, by='id'):
		'''find a card given a certain parameter
	  id: find the card with the given card id
	name: find the card with the given name.
	         If multiple match, return the first
	         Supports using SQL patterns'''
		if self.connection == None:
			self.open()
		if by == 'id':
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
			raise RuntimeError('Invalid query type ({0})'.format(by))
		cursor = self.connection.cursor()
		cursor.execute(query, [arg])
		row = cursor.fetchone()
		if row == None:
			return row
		else:
			return YGOProCard.from_row(row)
		
	def find_all(self, args, by='id'):
		'''A convenience method for finding multiple things at once. See YGOPRODatabase.find for "by" options'''
		if self.connection == None:
			self.open()
		for arg in args:
			yield self.search(arg, by)
			
	def search(self, arg, by='name'):
		'''find multiple cards that fulfill certain requirements
	name: use sql patterns to match card names
	text: use sql patterns to match card texts
	 sql: use sql expressions to search cards'''

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
			raise RuntimeError('Invalid database search type ({0})'.format(by))		
		for row in cursor:
			yield YGOProCard.from_row(row)
			
	def all_cards(self, anime=False):
		'''get every card available in the database'''
		# really slow, so the YGOProDatabase will cache the result
		# making subsequent calls faster.
		if self.__all_card_cache == None:
			if self.connection == None:
				self.open()
			cursor = self.connection.cursor()
			query = '''
				SELECT texts.name, texts.desc, datas.*
				FROM texts, datas
				WHERE texts.id = datas.id''' + ' AND datas.ot < 4' if not anime else ''
			cursor.execute(query)
			self.__all_card_cache = [YGOProCard.from_row(row) for row in cursor]
		return self.__all_card_cache


	
	def get_new_id(self):
		'''get a new card id that does not conflict with any existing cards'''
		# useful for making your own cards, though currently there isn't
		# any other support for it.
		if self.connection == None:
			self.open()
		query = '''SELECT max(datas.id) FROM datas'''
		cursor = self.connection.cursor()
		cursor.execute(query)
		result = cursor.fetchone()
		return result[0] + 1


# http://stevehanov.ca/blog/index.php?id=114
# not my code, but given as example by the above blog post.	
def levenshtein( word1, word2 ):
	'''calculates the number of edits required to get from word1 to word2'''
	columns = len(word1) + 1
	rows = len(word2) + 1

	# build first row
	currentRow = [0]
	for column in xrange( 1, columns ):
		currentRow.append( currentRow[column - 1] + 1 )

	for row in xrange( 1, rows ):
		previousRow = currentRow
		currentRow = [ previousRow[0] + 1 ]

		for column in xrange( 1, columns ):

			insertCost = currentRow[column - 1] + 1
			deleteCost = previousRow[column] + 1

			if word1[column - 1] != word2[row - 1]:
				replaceCost = previousRow[ column - 1 ] + 1
			else:                
				replaceCost = previousRow[ column - 1 ]

			currentRow.append( min( insertCost, deleteCost, replaceCost ) )
	return currentRow[-1]

#Not very reliable, but better than nothing.
# working on a better way to do this.
def levenshtein_match(name, cards):
	'''use the Levenshtein algorithm to find the card with the most similar name.'''
	bestcard, minlev = None, len(name)
	for card in cards:
		lev = levenshtein(name, card.name())
		if lev < minlev:
			bestcard = card
			minlev = lev
	return bestcard

class YGOProCard(ygocard.YugiohCard):
	'''A YugiohCard with extra information from the ygopro database.'''
	
	@staticmethod
	def from_row(row):
		'''construct a new YugiohCard with a database row'''
		# someday I'll clean this up, but for now,
		# abandon hope all ye who enter here.
		'''
			name : row[0]
			desc : row[1]
			id : row[2]
			ot : row[3]
			alias : row[4]
			setcode : row[5]
			type : row[6]
			atk : row[7]
			def : row[8]
			level : row[9]
			race : row[10]
			attribute : row[11]
			category : row[12]
		'''
		if row == None:
			raise TypeError('Cannot create a YGOProCard from None')
		try:
			catstr = ygoenum.get_string('category', row[6])
			attrstr = ygoenum.get_string('attribute', row[11])
			typestr = ygoenum.get_string('type', row[10])
		except ygoenum.EnumError as enum:
			print 'problem reading card {0}'.format(row[0])
			raise enum
		level_value = row[9]
		lvl = None
		lscl = None
		rscl = None
		if level_value < 14:
			lvl = level_value
		else:
			# extract pendulum scales from level column.
			hxstr = hex(level_value)
			lvl = int(hxstr[8], 16)
			lscl = int(hxstr[2], 16)
			rscl = int(hxstr[4], 16)			
		return YGOProCard(row[0], row[1], row[2], row[3], row[4], row[5], catstr, attrstr, typestr, row[7], row[8], lvl, lscl, rscl)
	

	def __init__(self, name, text, cid, ot, alias, setcode, category, attribute, race, attack, defense, level, lscale=None, rscale=None):
		ygocard.YugiohCard.__init__(self, name, text, cid, category, attribute, race, attack, defense, level, lscale, rscale)
		# these are only really relevant to ygopro.
		self._alias_data = alias
		self._ot_data = ot
		self._setcode_data = setcode
	
	# only available for cards gotten from the database
	def availability(self):
		''' get the banlist that this card is playable on'''
		return ygoenum.get_string('banlist', self._ot_data)
		
	def alias(self):
		'''This marks cards with multiple artworks. Should be unnecessary to deal with.'''
		return self._alias_data
		
	def setcode(self):
		'''This marks what archetype a card belongs to. Multi-archtype cards makes this too complicated to deal with right now.'''
		return self._setcode_data


def database():
	'''returns a new database instance to use to search for cards.'''
	db = YGOProDatabase()
	db.open()
	return db

def all_cards():
	'''get every card available'''
	db = database()
	cards = list(db.all_card())
	db.close()
	return cards
