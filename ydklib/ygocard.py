import collections
class YugiohCard(object):
	def __init__(self, name, text, cid, category, attribute, race, attack, defense, level, lscale=None, rscale=None):
		self._name = name
		self._text = text
		self._category = category
		self._attribute = attribute
		self._type = race
		self._attack = attack
		self._defense = defense
		self._level = level
		self._lscale = lscale
		self._rscale = rscale
		self._cid = cid
		
	def __hash__(self):
		return hash(self._name)
	def __eq__(self, other):
		return self._name == other.name()
	def __str__(self):
		return self.name()
		
	def name(self):
		return self._name
		
	def text(self):
		return self._text
		
	def cid(self):
		return self._cid
		
	def category(self):
		return self._category
		
	def is_monster(self):
		return 'Monster' in self.category()
		
	def is_spell(self):
		return 'Spell' in self.category()
		
	def is_trap(self):
		# damn son, where'd you find this?
		return 'Trap' in self.category()
		
	def is_pendulum(self):
		return 'Pendulum' in self.category()
		
	def is_synchro(self):
		return 'Synchro' in self.category()
		
	def is_xyz(self):
		return 'Xyz' in self.category()
		
	def is_tuner(self):
		return 'Tuner' in self.category()
		
	def is_effect_monster(self):
		return 'Effect' in self.category()
		
	def is_normal_monster(self):
		return self.category() in ['Normal-Monster', 'Token']
		
	def is_ritual_monster(self):
		return self.is_monster() and 'Ritual' in self.category()
		
	def attack(self):
		return self._attack
	
	def defense(self):
		return self._defense
			
	def monster_type(self):
		return self._type
		
	def attribute(self):
		return self._attribute

	def level(self):
		return self._level
		
	def left_scale(self):
		return self._lscale
				
	def right_scale(self):
		return self._rscale


class YugiohCollection(object):
	def __init__(self, groups):
		self._groups = collections.OrderedDict()
		for groupname in groups:
			self._groups[groupname] = []
			
	def new_group(self, name):
		if name not in self._groups:
			self._groups[name] = []
		else:
			raise KeyError('There is already a group with the name {0}'.format(name))
			
	def add_card(self, group, card):
		if group in self._groups:
			self._groups[group].append(card)
		else:
			self._groups[group] = [card]
			
	def add_cards(self, group, cards):
		if group in self._groups:
			self._groups[group].extend(cards)
		else:
			self._groups[group] = cards[:]
			
	def __iter__(self):
		for value in self._groups.values():
			for card in value:
				yield card
				
	def groups(self):
		return self._groups.items()
				
	def group(self, name):
		if name in self._groups:
			return self._groups[name]
		else:
			raise KeyError('No group named {0}'.format(name))
				
	def all(self):
		return iter(self)
		
class YugiohDeck(YugiohCollection):
	def __init__(self, name, author, main_deck, side_deck, extra_deck):
		YugiohCollection.__init__(self, ['main', 'side', 'extra'])
		self.name = name
		self.author = author
		if main_deck:
			self.add_cards('main', main_deck)
		if side_deck:
			self.add_cards('side', side_deck)
		if extra_deck:
			self.add_cards('extra', extra_deck)
		
	def main(self):
		return self.group('main')
	def side(self):
		return self.group('side')
	def extra(self):
		return self.group('extra')
