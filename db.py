import sqlite3
import urlparse

ygopro_path = '/home/owner/Desktop/ygopro-1.033.4v2-Percy/'

MONSTER_ATTRIBUTE = {
	'EARTH' : 1,
	'WATER' : 2,
	'FIRE' :  4,
	'WIND' :  8,
	'LIGHT' : 16,
	'DARK' :  32,
	'DIVINE' : 64
}

MONSTER_TYPE = {
	'Warrior' :       1,
	'Spellcaster' :   2,
	'Fairy' :         4,
	'Fiend' :         8,
	'Zombie' :        16,
	'Machine' :       32,
	'Aqua' :          64,
	'Pyro' :          128,
	'Rock' :          256,
	'Winged-Beast':   512,
	'Plant' :         1024,
	'Insect' :        2048,
	'Thunder' :       4096,
	'Dragon' :        8192,
	'Beast' :         16384,
	'Beast-Warrior' : 32768,
	'Dinosaur' :      65536,
	'Fish' :          131072,
	'Sea-Serpent' :   262144,
	'Reptile' :       524288,
	'Psychic' :       1048576,
	'Divine-Beast' :  2097152,
	'Creator-God' :   4194304,
	'Wyrm' :          8388608,
}
BANLIST = {
	'OCG' : 1,
	'TCG' : 2,
	'Any' : 3,
	'Anime' : 4,
}
CARD_CATEGORY = {
	'Normal-Spell':                 2,
	'Normal-Trap':                  4,
	'Normal-Monster':               17,
	'Effect-Monster':               33,
	'Fusion-Monster':               65,
	'Fusion-Effect-Monster':        97,
	'Ritual-Monster':               129,
	'Ritual-Spell':                 130,
	'Ritual-Effect-Monster':        161,
	'Spirit-Monster':               545,
	'Union-Monster':                1057,
	'Gemini-Monster':               2081,
	'Tuner-Normal-Monster':         4113,
	'Tuner-Effect-Monster':         4129,
	'Synchro--Normal-Monster':      8193,
	'Synchro-Effect-Monster':       8225,
	'Synchro-Tuner-Effect-Monster': 12321,
	'Token':                        16401,
	'Quick-Play-Spell':             65538,
	'Continuous-Spell':             131074,
	'Continuous-Trap':              131076,
	'Equip-Spell':                  262146,
	'Field-Spell':                  524290,
	'Counter-Trap':                 1048580,
	'Flip-Effect-Monster':          2097185,
	'Toon-Monster':                 4194337,
	'Xyz-Normal-Monster':           8388609,
	'Xyz-Effect-Monster':           8388641,
	'Pendulum-Normal-Monster' :     16777233,
	'Pendulum-Effect-Monster' :     16777249,
}

MAGIC_NUMBERS = {}
MAGIC_NUMBERS.update(MONSTER_ATTRIBUTE)
MAGIC_NUMBERS.update(MONSTER_TYPE)
MAGIC_NUMBERS.update(BANLIST)
MAGIC_NUMBERS.update(CARD_CATEGORY)

def reverseLookup(dct, number):
	for key, value in dct.items():
		if number == value:
			return key
	return None

def ygopath(path):
	return urlparse.urljoin(ygopro_path, path)


class Card(object):
	def __init__(self, stats, raw=False):
		# dict that contains all the information about the card
		self.stats = stats

		# a 'raw' Card contains the raw numbers from the database
		# nonraw Card contains human readable information, but throws away some data
		self.raw = raw

	def __str__(self):
		if self.raw:
			return '{0} <raw>'.format(self.stats['name'])
		else:
			return '{0}'.format(self.stats['name'])

	def containsRawData(self):
		return self.raw
	def __contains__(self, other):
		return other in self.stats
	def __getitem__(self, name):
		if name in self.stats:
			return self.stats[name]
		else:
			raise KeyError(name)

class Searcher(object):
	def __init__(self):
		self.connection = sqlite3.connect(ygopath('cards.cdb'))

	def cursor(self):
		return self.connection.cursor()

	def cid_from_name(self, name):
		cursor = self.cursor()
		sql = '''
			SELECT texts.id
			FROM texts
			WHERE texts.name = ?'''
		cursor.execute(sql, [name])
		result = cursor.fetchone()
		return result[0] if result else None

	def name_from_cid(self, cid):
		cursor = self.cursor()
		sql = '''
			SELECT texts.name
			FROM texts
			WHERE texts.id = ?'''
		cursor.execute(sql, [cid])
		result = cursor.fetchone()
		return result[0] if result else None

	def __searchCard(self, cid):
		cursor = self.cursor()
		sql = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.id = ?'''
		cursor.execute(sql, [cid])
		result = cursor.fetchone()
		return result
	

	def rawObject(self, cid):
		results = self.__searchCard(cid)
		return Card({
			# these are just the names of the database columns
			'name' : result[0],
			'desc' : result[1],
			'id' : result[2],
			'ot' : result[3],
			'alias' : result[4],
			'setcode' : result[5],
			'type' : result[6],
			'atk' : result[7],
			'def' : result[8],
			'level' : result[9],
			'race' : result[10],
			'attribute' : result[11],
			'category' : result[12]
		}, raw = True)

	def asPrettyObject(self, cid):
		result = self.__searchCard(cid)
		pobj = {}
		pobj['name'] = result[0]
		pobj['text'] = result[1]
		pobj['id'] = result[2]
		pobj['banlist'] = reverseLookup(BANLIST, result[3])
		# not sure what to do with alias or setcode
		# setcode has to do with archetypes
		# alias is for the same card with multiple artworks
		pobj['category'] = reverseLookup(CARD_CATEGORY, result[6])
		pobj['attack']  = result[7]
		pobj['defense'] = result[8]
		if pobj['category'].startswith('Pendulum'):
			# pendulum scales are represented with level
			# 0xL0R000V where L, R are the pendulum scales, and V is the level
			# the level is stored as decimal, however, so we convert to hex string first
			lvl = int(result[9])
			hxstr = hex(lvl)
			pobj['left-scale'] = int(hxstr[2], 16)
			pobj['right-scale'] = int(hxstr[4], 16)
			pobj['level'] = int(hxstr[8], 16)
		else:
			pobj['level'] = int(result[9])
			pobj['left-scale'] = None
			pobj['right-scale'] = None
		pobj['type'] = reverseLookup(MONSTER_TYPE, result[10])
		pobj['attribute'] = reverseLookup(MONSTER_ATTRIBUTE, result[11])
		return Card(pobj, raw=False)		

class YDKLoader(Searcher):
	def __init__(self, ydkfile):
		Searcher.__init__(self)
		self.creator = ''
		self.mainDeck = []
		self.extraDeck = []
		self.sideDeck = []
		current =self. mainDeck
		for line in ydkfile:
			line = line.rstrip()
			if line.startswith('#created by'):
				creator = line[12:]
			elif line in ('#main', '!main'):
				current = self.mainDeck
			elif line in ('#extra', '!extra'):
				current = self.extraDeck
			elif line in ('#side', '!side'):
				current = self.sideDeck
			elif line.startswith('#'):
				continue
			else:
				current.append(line)
	def __iter__(self):
		for cid in self.mainDeck:
			yield self.asPrettyObject(cid)

		
def card_by_name(name):
	search = Searcher()
	return search.asPrettyObject(search.cid_from_name(name))

def card_by_cid(cid):
	return Searcher().asPrettyObject(cid)

def ydkopen(deckname):
	fl =  open(ygopath('deck/'+deckname+'.ydk'))
	return YDKLoader(fl)
