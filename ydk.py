import sqlite3 as sqlite
import ygoenum
import collections

YGOPRO_PATH = '/home/owner/Desktop/ygopro-1.033.4v2-Percy/'
class YGOPROClientError(RuntimeError): pass
class YGOPROCardClient(object):
	def __init__(self, cardscdb = (YGOPRO_PATH + '/cards.cdb')):
		self.db_path = cardscdb
		self.connection = None
	def open(self):
		if self.connection == None:
			self.connection = sqlite.connect(self.db_path)
		return self.connection
	def close(self):
		if self.connection != None:
			self.connection.close()
			self.connection = None
	def card_by_id(self, cid):
		if self.connection == None:
			raise YGOPROClientError('Cannot load cards while database is closed')
		cursor = self.connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.id = ?'''
		cursor.execute(query, [cid])
		row = cursor.fetchone()
		return YugiohCard(row)
	def cards_by_pattern(self, pattern):
		if self.connection == None:
			raise YGOPROClientError('Cannot load cards while database is closed')
		cursor = self.connection.cursor()
		query = '''
			SELECT texts.name, texts.desc, datas.*
			FROM texts, datas
			WHERE texts.id = datas.id AND texts.name LIKE ?'''
		cursor.execute(query, [pattern])
		for row in cursor:
			yield YugiohCard(row)
		

class YDK(YGOPROCardClient):
	def __init__(self, ydk_path):
		YGOPROCardClient.__init__(self)
		self.author = '...'
		self.main_deck = []
		self.extra_deck = []
		self.side_deck = []
		current = self.main_deck
		self.open()
		with open(ydk_path) as fl:
			for line in fl:
				if line.startswith('#created by '):
					self.author = (line.rstrip())[11:]
				elif line.startswith('#main'):
					current = self.main_deck
				elif line.startswith('#extra'):
					current = self.extra_deck
				elif line.startswith('!side'):
					current = self.side_deck
				elif line.startswith('#'):
					continue
				else:
					cid = int(line.rstrip())
					card = self.card_by_id(cid)
					current.append(card)
		self.close()
	def save(self, fl):
		fl.write('#created by {0}\n'.format(self.author))
		fl.write('#main\n')
		for card in self.main():
			fl.write('{0}\n'.format(card.cid()))
		fl.write('#extra\n')
		for card in self.extra():
			fl.write('{0}\n'.format(card.cid()))
		fl.write('!side\n')
		for card in self.side():
			fl.write('{0}\n'.format(card.cid()))
	def __enter__(self):
		return self
	def __exit__(self, t, value, traceback):
		self.close()
		return False
	def main(self):
		return iter(self.main_deck)
	def extra(self):
		return iter(self.extra_deck)
	def side(self):
		return iter(self.side_deck)
	def all(self):
		for card in self.main():
			yield card
		for card in self.extra():
			yield card
		for card in self.side():
			yield card

def ydkopen(flname):
	return YDK(flname)


class YDKC(object):
	def __init__(self, ydk_path):
		YGOPROCardClient.__init__(self)
		self.author = ''
		self.sections = collections.OrderedDict()
		self.sections['main'] = []
		current = self.sections['main']
		self.open()
		with open(ydk_path) as fl:
			for line in fl:
				if line.startswith('#created by '):
					self.author = (line.rstrip())[11:]
				elif line.startswith('#main'):
					current = self.sections['main']
				elif line.startswith('#extra'):
					if 'extra' not in self.sections:
						self.sections['extra'] = []
					current = self.sections['extra']
				elif line.startswith('!side'):
					if 'side' not in self.sections:
						self.sections['side'] = []
					current = self.sections['side']
				elif line.startswith('#!'):
					new_section_name = (line.rstrip())[2:]
					if new_section_name not in self.sections:
						self.sections[new_section_name] = []
					current = self.sections[new_section_name]
				else:
					cid = int(line.rstrip())
					card = self.card_by_id(cid)
					current.append(card)
		self.close()
	def save(self, fl):
		fl.write('#created by {0}\n'.format(self.author))
		for sname in self.sections:
			if sname == 'main':
				fl.write('#main\n')
			elif sname == 'extra':
				fl.write('#extra\n')
			elif sname == 'side':
				fl.write('!side\n')
			else:
				fl.write('#!{0}\n'.format(sname))

			for card in self.section(sname):
				fl.write('{0}\n'.format(card.cid()))
	def __enter__(self):
		return self
	def __exit__(self, t, value, traceback):
		self.close()
		return False
	def main(self):
		return iter(self.sections['main'])
	def extra(self):
		return iter(self.sections.get('extra', []))
	def side(self):
		return iter(self.sections.get('side', []))
	def section(self, name):
		return iter(self.sections.get(name, []))
	def all(self):
		for card in self.main():
			yield card
		for card in self.extra():
			yield card
		for card in self.side():
			yield card
			
def ydkcopen(flname):
	return YDKC(flname)

class YugiohCard(object):
	def __init__(self, row):
		self.attributes = {
			'name' : row[0], #
			'desc' : row[1], #
			'id' : row[2], #
			'ot' : row[3], #
			'alias' : row[4], #
			'setcode' : row[5], #
			'type' : row[6],
			'atk' : row[7], #
			'def' : row[8], #
			'level' : row[9], #
			'race' : row[10], #
			'attribute' : row[11], #
			'category' : row[12]
		}
	def __str__(self):
		return self.name()
		
	def name(self):
		return self.attributes['name']
		
	def text(self):
		return self.attributes['desc']
		
	def cid(self):
		return self.attributes['id']
		
	def availability(self, raw=False):
		n = self.attributes['ot']
		return n if raw else ygoenum.get_string('banlist', n)
		
	def alias(self):
		# This marks cards with multiple artworks. Should be unnecessary to deal with.
		return self.attributes['alias']
		
	def setcode(self):
		# this marks what archetype a card belongs to.
		# multi-archtype cards makes this too complicated to deal with right now.
		return self.attributes['setcode']

	def category(self, raw=False):
		n = self.attributes['type']
		return n if raw else ygoenum.get_string('category', n)
		
	def is_monster(self):
		return self.attributes['type'] in ygoenum.MONSTER
		
	def is_spell(self):
		return self.attributes['type'] in ygoenum.SPELL
		
	def is_trap(self):
		# damn son, where'd you find this?
		return self.attributes['type'] in ygoenum.TRAP
		
	def is_pendulum(self):
		return self.attributes['type'] in ygoenum.PENDULUM	
		
	def is_synchro(self):
		return self.attributes['type'] in ygoenum.SYNCHRO
		
	def is_xyz(self):
		return self.attributes['type'] in ygoenum.XYZ
		
	def is_tuner(self):
		return self.attributes['type'] in ygoenum.TUNER	
		
	def is_effect_monster(self):
		n = self.attributes['type']
		return n in ygoenum.MONSTER and n not in ygoenum.NON_EFFECT
		
	def is_normal_monster(self):
		return self.attributes['type'] == 17
		
	def is_non_effect_monster(self):
		return self.attributes['type'] in ygoenum.NON_EFFECT
		
	def is_ritual_monster(self):
		return self.attributes['type'] in ygoenum.RITUAL
		
	def attack(self):
		return self.attributes['atk']
	
	def defense(self):
		return self.attributes['def']	
			
	def monster_type(self, raw=False):
		n = self.attributes['race']
		return n if raw else ygoenum.get_string('type', n)
		
	def attribute(self, raw=False):
		n = self.attributes['attribute']
		return n if raw else ygoenum.get_string('attribute', n)
		
	def level(self):
		if self.is_pendulum():
			# pendulum scales are represented with level
			# 0xL0R000V where L, R are the pendulum scales, and V is the level
			# the level is stored as decimal, however, so we convert to hex string first
			lvl = hex(int(self.attributes['level']))
			return int(lvl[8], 16)
		else:
			return self.attributes['level']
		
	def left_scale(self):
		if self.is_pendulum():
			lvl = hex(int(self.attributes['level']))
			return int(lvl[2], 16)
		else:
			return None
				
	def right_scale(self):	
		if self.is_pendulum():
			lvl = hex(int(self.attributes['level']))
			return int(lvl[4], 16)
		else:
			return None		
		
