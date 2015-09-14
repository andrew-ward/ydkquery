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
		return self._cid == other.cid()
		
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

		
class YugiohDeck(object):
	def __init__(self, name, author, main_deck=None, side_deck=None, extra_deck=None):
		self._main_deck = {}
		self._side_deck = {}
		self._extra_deck = {}
		if main_deck:
			self.add_cards(main_deck)
		if side_deck:
			self.add_cards(side_deck, 'side')
		if extra_deck:
			self.add_cards(extra_deck, 'extra')
			

		'''the title of the deck'''
		self.name = name
		
		'''the creator of the deck'''
		self.author = author
			
	def _group(self, name):
		# for internal use only
		if name == 'main':
			return self._main_deck
		elif name == 'side':
			return self._side_deck
		elif name == 'extra':
			return self._extra_deck
		else:
			# should never happen if I did my job right.
			raise RuntimeError('ProgrammerError: invalid deck group {0}'.format(name)) 
			
	def add_card(self, card, group='main'):
		'''add a card to the deck. "group" specifies whether to add it to main, side, or extra.'''
		deck = self._group(group)
		if card in deck:
			deck[card] += 1
		else:
			deck[card] = 1
			
	def add_cards(self, cards, group='main'):
		'''add multiple cards to the deck. "group" specifies whether to add it to main, side, or extra.'''
		for card in cards:
			self.add_card(card, group)
			
	def count(self, card, group='main'):
		'''return how many instances of that card are in the deck. "group" specifies whether to add it to main, side, or extra.'''
		g = self._group(group)
		if card not in g:
			raise RuntimeError('Could not find card {0}'.format(card))
		return g.get(card, 0)
		
	def count_all(self, cards, group='main'):
		'''return how many instances of those cards are in the deck. "group" specifies whether to add it to main, side, or extra.'''
		return sum(self.count(card, group) for card in cards)

	def size(self, group='main'):		
		'''return how many cards are in the deck. "group" specifies whether to add it to main, side, or extra.'''
		return sum(self._group(group).values())
		
	def main(self):
		'''returns a set of all the cards in the main deck. This ignores duplicates.'''
		return set(self._main_deck.keys())
		
	def side(self):
		'''returns a set of all the cards in the side deck. This ignores duplicates.'''
		return set(self._side_deck.keys())
		
	def extra(self):
		'''returns a set of all the cards in the extra deck. This ignores duplicates.'''
		return set(self._extra_deck.keys())
		
	def get(self, name, group='main'):
		'''get the card named from the deck. "group" specifies whether to add it to main, side, or extra.'''
		deck = self._group(group)
		for card in deck.keys():
			if card.name() == name:
				return card
		
	def get_all(self, names, group='main'):
		'''get all the cards named from the deck as a set. "group" specifies whether to add it to main, side, or extra.'''
		deck = self._group(group)
		output = set()
		for card in deck.keys():
			if card.name() in names:
				output.add(card)
		return output
				
	def find(self, pred, group='main'):
		'''get a set of all cards for which the function pred is true. "group" specifies whether to add it to main, side, or extra.'''
		output = set()
		for card in self._group(group):
			if pred(card):
				output.add(card)
		return output
			
	def as_ydk(self):
		''' convert the deck to a .ydk formatted string.'''
		output = '#created by {0}\n'.format(self.author)
		output += '#main\n'
		for card in self.main():
			for i in range(self.count(card, 'main')):
				output += '{0}\n'.format(card.cid())
		output += '#extra\n'
		for card in self.extra():
			for i in range(self.count(card, 'extra')):
				output += '{0}\n'.format(card.cid())
		output += '!side\n'
		for card in self.side():
			for i in range(self.count(card, 'side')):
				output += '{0}\n'.format(card.cid())
		return output
		
	def as_markdown(self):
		''' convert the deck to a decklist string formatted for reddit-style markdown'''
		monsters = self.find(YugiohCard.is_monster)				
		output = "# Monster:{0}\n".format(self.count_all(monsters))
		for monster in monsters:
			output += "- **{0}x {1}**\n".format(self.count(monster), monster.name())

		spells = self.find(YugiohCard.is_monster)			
		output += "\n# Spells:{0}\n".format(self.count_all(spells))
		for spell in spells:
			output += "- **{0}x {1}**\n".format(self.count(spell), spell.name())

		traps = self.find(YugiohCard.is_monster)			
		output += "\n# Traps:{0}\n".format(self.count_all(traps))
		for trap in traps:
			output += "- **{0}x {1}**\n".format(self.count(trap), trap.name())
		
		output += "\n---\n# Extra Deck: {0}\n".format(len(self.extra()))
		for monster in self.extra():
			output += "- **{0}x {1}**\n".format(self.count(monster, group="extra"), monster.name())
			
		output += "\n---\n# Side Deck: {0}\n".format(len(self.side()))
		for card in self.side():
			output += "- **{0}x {1}**\n".format(self.count(card, group="side"), card.name())
		output += "---\n"
		return output
		
	def as_decklist(self):
		'''convert the deck to a simple, easy-to-read decklist without the formatting markdown has'''
		monsters = self.find(YugiohCard.is_monster)
		output = 'Main Deck\n'	
		output += "  Monster({0})\n".format(self.count_all(monsters))
		for monster in monsters:
			output += "    {0} x{1}\n".format(monster.name(), self.count(monster))

		spells = self.find(YugiohCard.is_spell)			
		output += "  Spells({0})\n".format(self.count_all(spells))
		for spell in spells:
			output += "    {0} x{1}\n".format(spell.name(), self.count(spell))

		traps = self.find(YugiohCard.is_trap)			
		output += "  Traps({0})\n".format(self.count_all(traps))
		for trap in traps:
			output += "    {0} x{1}\n".format(trap.name(), self.count(trap))
		
		output += "Extra Deck({0})\n".format(len(self.extra()))
		for monster in self.extra():
			output += "    {0} x{1}\n".format(monster.name(), self.count(monster, 'extra'))
			
		output += "Side Deck({0})\n".format(len(self.side()))
		for card in self.side():
			output += "    {0} x{1}\n".format(card.name(), self.count(card, 'side'))
		return output		
