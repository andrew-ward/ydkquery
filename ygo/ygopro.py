import sqlite3 as sqlite

from . import card

class CardNotFoundException(RuntimeError):
	pass
	
class InvalidQueryError(RuntimeError):
	pass
	
class YGOProDatabase(object):
	"""a wrapper around an sqlite connection to the cards.cdb database."""
	def __init__(self, path=None):
		self._path = path
		self._connection = None

	def open(self, path=None):
		path = path or self._path
		if path is not None:
			try:
				self._connection = sqlite.connect(path)
			except sqlite.OperationalError as soe:
				raise sqlite.OperationalError('unable to open database file "{0}"'.format(path))
		else:
			raise IOError('No database filename given')

	def close(self):
		if self._connection is not None:
			self._connection.close()

	def __enter__(self):
		self.open()
		return self

	def __exit__(self, t, value, traceback):
		self.close()
		return False

	def all_cards(self):
		"""
		Get all cards in the database.
		:returns: list of YugiohCards
		"""
		if self._connection is None:
			self.open()
		cursor = self._connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND datas.ot != 4'''
		cursor.execute(query)
		output = []
		for row in cursor:
			yield self.__make_card(row)
		

	def find_id(self, cid):
		"""
		Get a card with the given id
		:param cid: The card's id.
		:type cid: str or int
		:returns: A YugiohCard object
		"""
		if self._connection is None:
			self.open()
		cursor = self._connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.id = ? AND datas.ot != 4'''
		cursor.execute(query, [cid])
		for row in cursor:
			return self.__make_card(row)
		raise CardNotFoundException('Could not find card with id#{0}'.format(cid))

	def find_name(self, name):
		"""
		Get a card with the given name
		:param cid: The card's name.
		:type cid: str
		:returns: A YugiohCard object
		"""
		if self._connection is None:
			self.open()
		cursor = self._connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.name = ? AND datas.ot != 4'''
		cursor.execute(query, [name])
		for row in cursor:
			card = self.__make_card(row)
			return card
		raise CardNotFoundException('Could not find card with name "{0}"'.format(name))

	def __make_card(self, row):
		card = {}
		card['name'] = row[0]
		card['text'] = row[1]
		card['id'] = str(row[2])

		# mostly irrelevant
		card['availability'] = row[3]
		card['alias'] = row[4]
		card['setcode'] = row[5]			

		card['category'] = row[6]

		is_monster = True
		if row[6] % 2 == 0:
			# non-monster
			is_monster = False
			card['attack'] = None
			card['defense'] = None
			card['level'] = None
			card['left_scale'] = None
			card['right_scale'] = None

		elif row[9] < 14:
			# non-pendulum monster
			card['attack'] = row[7]
			card['defense'] = row[8]
			card['level'] = row[9]
			card['left_scale'] = None
			card['right_scale'] = None
		else:
			card['attack'] = row[7]
			card['defense'] = row[8]
			hxstr = hex(row[9])
			card['level'] = int(hxstr[8], 16)
			card['left_scale'] = int(hxstr[2], 16)
			card['right_scale'] = int(hxstr[4], 16)


		if is_monster:
			card['type'] = MONSTER_TYPE.get(row[10])
			card['attribute'] = ATTRIBUTE.get(row[11])
		else:
			card['type'] = None
			card['attribute'] = None
		return YGOProCard(card)

MONSTER_TYPE = {
	0 : None,
	1 : 'Warrior',
	2 : 'Spellcaster',
	4 : 'Fairy',
	8 : 'Fiend',
	16 : 'Zombie',
	32 : 'Machine',
	64 : 'Aqua',
	128 : 'Pyro',
	256 : 'Rock',
	512 : 'Winged-Beast',
	1024 : 'Plant',
	2048 : 'Insect',
	4096 : 'Thunder',
	8192 : 'Dragon',
	16384 : 'Beast',
	32768 : 'Beast-Warrior',
	65536 : 'Dinosaur',
	131072 : 'Fish',
	262144 : 'Sea Serpent',
	524288 : 'Reptile',
	1048576 : 'Psychic',
	2097152 : 'Divine Beast',
	4194304 : 'Creator God',
	8388608 : 'Wyrm'
}

ATTRIBUTE = {
	0 : 'Non-Monster',
	1 : 'EARTH',
	2 : 'WATER',
	4 : 'FIRE',
	8 : 'WIND',
	16 : 'LIGHT',
	32 : 'DARK',
	64 : 'DIVINE'
}

def bit(byteval,idx):
    return ((byteval&(1<<idx))!=0)


class YGOProCard(card.YugiohCard):
	"""A YugiohCard with extra information from the ygopro database.
	
	:ivar alias: This marks cards with multiple artworks
	:vartype alias: int
	:ivar availability: get the location that this card is playable in. (i.e. TCG exclusive, OCG exclusive, Anime card, etc)
	:vartype availability: "Any" or "TCG" or "OCG" or "Anime"
	:ivar setcode: This marks what archetype a card belongs to. If two cards have the same setcode, they belong to the same archetypes. The reverse is not neccesarily true.
	:vartype setcode: int"""
	
	def __init__(self, attr):
		"""Construct a new YugiohCard with a database row.

		:param attr: a dict containing all the information to construct the card
		:type attr: keys include name, text, id, category, attribute, type, attack, defense, level, left_scale, right_scale, availability, alias, and setcode, """
		
		card.YugiohCard.__init__(self,
			attr['name'], attr['text'], attr['id'],
			attr['category'], attr['attribute'], attr['type'],
			attr['attack'], attr['defense'], attr['level'],
			attr['left_scale'], attr['right_scale'])

		self.properties['availability'] = attr['availability']
		self.properties['alias'] = attr['alias']
		self.properties['setcode'] = attr['setcode']

	@property
	def availability(self):
		return self.__availability

	@property
	def alias(self):
		return self._alias

	@property
	def setcode(self):
		return self.__setcode
