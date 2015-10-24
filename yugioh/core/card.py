import collections
class YugiohCard(object):
	""" holds all the data of a single yugioh card. """
	def __init__(self, name, text, cid, banlist_status, category, attribute, race, attack, defense, level, lscale=None, rscale=None):
		"""full name of the card (string)"""
		self.name = name
		
		"""text on the card (string)"""
		self.text = text
		
		"""a text string that says what kind of card it is (i.e. Normal Spell, Counter Trap, Synchro Monster, etc) (string)"""
		self.category = category
		
		"""the unique card id (string)"""
		self.cid = cid		
		
		self._banlist_status = banlist_status
				
		# only exist for monsters
		"""the attribute of the monster (string)"""
		self.attribute = attribute if attribute != "N/A" else None
		
		"""the type of the monster (string)"""
		self.type = race if race != "N/A" else None
		
		"""the level/rank of the monster (int)"""
		self.level = level if level > 0 else None
		
		"""the attack stat of the monster. ? attack is negative (int)"""
		self.attack = attack if 'Monster' in self.category else None
		
		"""the defense stat of the monster. ? defense is negative (int)"""
		self.defense = defense if 'Monster' in self.category else None
		
		"""The left pendulum scale of the monster (int)"""
		self.left_scale = lscale
		
		"""The right pendulum scale of the monster (int)"""
		self.right_scale = rscale
		
		
	def __hash__(self):
		return hash(self.cid)
	def __eq__(self, other):
		return isinstance(other, YugiohCard) and self.cid == other.cid
		
	def __repr__(self):
		return 'YugiohCard({0})'.format(self.name)
	def __str__(self):
		return self.name
		
	def is_monster(self):
		"""self.is_monster() -> bool
returns True if card is a monster card"""
		return 'Monster' in self.category
		
	def is_spell(self):
		"""self.is_spell() -> bool
 returns True if card is a spell card"""
		return 'Spell' in self.category
		
	def is_trap(self):
		"""self.is_trap() -> bool
returns True if card is a trap card"""
		# damn son, where'd you find this?
		return 'Trap' in self.category
		
	def is_pendulum(self):
		"""self.is_pendulum() -> bool
returns True if card is a pendulum monster card"""
		return 'Pendulum' in self.category
		
	def is_synchro(self):
		"""self.is_synchro() -> bool
returns True if card is a synchro monster card"""
		return 'Synchro' in self.category
		
	def is_xyz(self):
		"""self.is_xyz() -> bool
returns True if card is an xyz monster card"""
		return 'Xyz' in self.category
		
	def is_tuner(self):
		"""self.is_tuner() -> bool
returns True if card is a tuner"""
		return 'Tuner' in self.category
		
	def is_effect_monster(self):
		"""self.is_effect_monster() -> bool
returns True if card is a monster with an effect"""
		return 'Effect' in self.category
		
	def is_normal_monster(self):
		"""self.is_normal_monster() -> bool
returns True if card is a Normal monster. This is not the same as a monster without an effect."""
		return self.category in ['Normal-Monster', 'Token']
		
	def is_ritual_monster(self):
		"""self.is_ritual_monster() -> bool
returns True if card is a Ritual Monster"""
		return self.is_monster and 'Ritual' in self.category()
		
	def is_legal(self, banlist='TCG'):
		return self.allowed() > 0
		
	def allowed(self, banlist='TCG'):
		"""self.allowed(string banlist) -> (0 <= int <= 3)
return the number of copies allowed in a deck according to the given banlist."""
		for key in self._banlist_status:
			if banlist.upper() in key:
				return self._banlist_status[key]
		raise KeyError('No banlist called {0}'.format(banlist))

	def banlist_status(self, banlist='TCG'):
		"""self.banlist_status() -> string (unlimited|semi-limited|limited|forbidden)
return text representation of how many are allowed under a given banlist"""
		n = self.allowed(banlist)
		if n == 0:
			return 'forbidden'
		elif n == 1:
			return 'limited'
		elif n == 2:
			return 'semi-limited'
		elif n == 3:
			return 'unlimited'
		else:
			raise RuntimeError('wtf. {0} says you can run {1} copies in {2} format'.format(self.name(), n, banlist))
