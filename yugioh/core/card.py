import collections
class YugiohCard(object):
	''' holds all the data of a yugioh card. '''
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
		return hash(self._cid)
	def __eq__(self, other):
		return isinstance(other, YugiohCard) and self._cid == other.cid()
		
	def __repr__(self):
		return 'YugiohCard({0})'.format(self.name())
	def __str__(self):
		return self.name()
		
	def name(self):
		'''returns the full name of the card.'''
		return self._name
		
	def text(self):
		''' returns the text on the card. '''
		return self._text
		
	def cid(self):
		''' returns the card id of the card as an integer. '''
		return self._cid
		
	def category(self):
		''' returns a text string that says what kind of card it is (i.e. Normal Spell, Counter Trap, Synchro Monster, etc).'''
		# mostly used for human readable purposes
		# for more fine grained queries, see the following set
		# of functions.
		return self._category
		
	def is_monster(self):
		''' returns True if card is a monster card'''
		return 'Monster' in self.category()
		
	def is_spell(self):
		''' returns True if card is a spell card'''
		return 'Spell' in self.category()
		
	def is_trap(self):
		''' returns True if card is a trap card'''
		# damn son, where'd you find this?
		return 'Trap' in self.category()
		
	def is_pendulum(self):
		''' returns True if card is a pendulum monster card'''
		return 'Pendulum' in self.category()
		
	def is_synchro(self):
		''' returns True if card is a synchro monster card'''
		return 'Synchro' in self.category()
		
	def is_xyz(self):
		''' returns True if card is an xyz monster card'''
		return 'Xyz' in self.category()
		
	def is_tuner(self):
		''' returns True if card is a tuner'''
		return 'Tuner' in self.category()
		
	def is_effect_monster(self):
		''' returns True if card is a monster with an effect'''
		return 'Effect' in self.category()
		
	def is_normal_monster(self):
		''' returns True if card is a Normal monster. This is not the same as a monster without an effect.'''
		return self.category() in ['Normal-Monster', 'Token']
		
	def is_ritual_monster(self):
		''' returns True if card is a Ritual Monster'''
		return self.is_monster() and 'Ritual' in self.category()
		
	def attack(self):
		''' returns the attack of the monster as an integer. If the card is not a monster, returns 0. If the monster has ? attack, returns a negative number.'''
		return self._attack
	
	def defense(self):
		''' returns the defense of the monster as an integer. If the card is not a monster, returns 0. If the monster has ? defense, returns a negative number.'''
		return self._defense
			
	def monster_type(self):
		'''returns the type of the monster as a string. Non-monsters return "N/A"'''
		return self._type
		
	def attribute(self):
		'''returns the attribute of the monster as a string. Non-monsters return "N/A"'''
		return self._attribute

	def level(self):
		'''returns the level of the monster as an integer. Non-monsters return 0'''
		return self._level
		
	def left_scale(self):
		'''returns the left pendulum scale of the monster as a string. Non-pendulums return None'''
		return self._lscale
				
	def right_scale(self):
		'''returns the right pendulum scale of the monster as a string. Non-pendulums return None'''
		return self._rscale

	
