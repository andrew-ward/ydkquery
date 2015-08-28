import ygoenum
import ygocard
import sqlite3 as sqlite
YGOPRO_PATH = '/home/owner/Desktop/ygopro-1.033.4v2-Percy/'

class YGOPRODatabase(object):
	def __init__(self, cardscdb = (YGOPRO_PATH + '/cards.cdb')):
		self.db_path = cardscdb
		self.connection = None
	def open(self):
		if self.connection == None:
			self.connection = sqlite.connect(self.db_path)
		return self
	def __enter__(self):
		return self.open()
	def __exit__(self, t, value, traceback):
		self.close()
		return False
	def close(self):
		if self.connection != None:
			self.connection.close()
			self.connection = None
	def card_by_id(self, cid):
		if self.connection == None:
			raise RuntimeError('Cannot load cards while database is closed')
		cursor = self.connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.id = ?'''
		cursor.execute(query, [cid])
		row = cursor.fetchone()
		return DevproCard.from_row(row)
		
	def cards_by_pattern(self, pattern):
		if self.connection == None:
			raise RuntimeError('Cannot load cards while database is closed')
		cursor = self.connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.name LIKE ?'''
		cursor.execute(query, [pattern])
		for row in cursor:
			yield DevproCard.from_row(row)

	def cards_by_pattern(self, pattern):
		if self.connection == None:
			raise RuntimeError('Cannot load cards while database is closed')
		cursor = self.connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.name LIKE ?'''
		cursor.execute(query, [pattern])
		for row in cursor:
			yield DevproCard.from_row(row)
			
	def all_cards(self, anime=False):
		if self.connection == None:
			raise RuntimeError('Cannot load cards while database is closed')
		cursor = self.connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id''' + ' AND datas.ot < 4' if not anime else ''
		cursor.execute(query)
		for row in cursor:
			yield DevproCard.from_row(row)
		
			
	def cards_by_sql(self, subquery):
		if self.connection == None:
			raise RuntimeError('Cannot load cards while database is closed')
		cursor = self.connection.cursor()
		query = '''SELECT texts.name, texts.desc, datas.*
		FROM texts, datas
		WHERE texts.id = datas.id AND {0}'''.format(subquery)
		cursor.execute(query)
		for row in cursor:
			yield YugiohCard(row)

class DevproCard(ygocard.YugiohCard):
	@staticmethod
	def from_row(row):
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
		catstr = ygoenum.get_string('category', row[6])
		attrstr = ygoenum.get_string('attribute', row[11])
		typestr = ygoenum.get_string('type', row[10])
		level_value = row[9]
		lvl = None
		lscl = None
		rscl = None
		if level_value < 14:
			lvl = level_value
		else:
			hxstr = hex(level_value)
			lvl = int(hxstr[8], 16)
			lscl = int(hxstr[2], 16)
			rscl = int(hxstr[4], 16)			
		return DevproCard(row[0], row[1], row[2], row[3], row[4], row[5], catstr, attrstr, typestr, row[7], row[8], lvl, lscl, rscl)
	

	def __init__(self, name, text, cid, ot, alias, setcode, category, attribute, race, attack, defense, level, lscale=None, rscale=None):
		ygocard.YugiohCard.__init__(self, name, text, cid, category, attribute, race, attack, defense, level, lscale, rscale)
		self._alias_data = alias
		self._ot_data = ot
		self._setcode_data = setcode
		
	def availability(self):
		return ygoenum.get_string('banlist', self._ot_data)
		
	def alias(self):
		# This marks cards with multiple artworks. Should be unnecessary to deal with.
		return self._alias_data
		
	def setcode(self):
		# this marks what archetype a card belongs to.
		# multi-archtype cards makes this too complicated to deal with right now.
		return self._setcode_data


def database():
	db = YGOPRODatabase()
	db.open()
	return db

def all_cards():
	db = search()
	cards = list(db.all_card())
	db.close()
	return cards
