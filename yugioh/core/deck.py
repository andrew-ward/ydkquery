"""The datatypes holding information about a yugioh deck."""

import collections
from .card import YugiohCard

class YugiohSet(object):
	"""A set of yugioh cards that can be query'd"""
	def __init__(self, cards):
		self._contents = {}
		if cards:
			self.add_cards(cards)
			
	def __len__(self):
		"""len(self) -> int
		returns Number of cards in the deck."""
		return self.size()
		
	def __iter__(self):
		"""iter(self) -> card.YugiohCard iterator
Iterate over each unique card in the deck.
i.e. if you have two copies of the same card, it will only appear once."""
		return iter(self._contents.keys())
		
	def all(self):
		"""self.all() -> card.YugiohCard list
Return list of unique cards in the deck.
i.e. if you have two copies of the same card, it will only appear once.
"""
		return list(self._contents.keys())
		
	def __getitem__(self, key):
		"""self[card.YugiohCard] -> int
Return the number of copies of the given card in the deck"""
		return self.count(key)

	def add_card(self, card, count=1):
		"""self.add_card(card.YugiohCard, count=int) -> None
add a card to the deck."""
		assert(isinstance(count, int))
		if card in self._contents:
			self._contents[card] += count
		else:
			self._contents[card] = count
			
	def add_cards(self, cards):
		"""self.add_cards(card.YugiohCard iterable) -> None
Add multiple cards to the deck"""
		for card in cards:
			self.add_card(card)
			
	def size(self):
		"""self.size() -> int
returns number of cards in the deck."""
		return sum(self._contents.values())
		
	def count(self, card):
		"""self.count(card.YugiohCard) -> int
Return the number of copies of the given card in the deck"""
		return self._contents.get(card, 0)
		
	def count_all(self, cards):		
		"""self.count_all(card.YugiohCard iterable) -> int
Return the number of copies of each of the given cards in the deck"""
		return sum(self.count(card) for card in cards)		
		
	def get(self, name):
		"""self.get(string) -> card.YugiohCard
get the card named from the deck."""
		for card in self._contents.keys():
			if name == card.name:
				return card				
				
	def get_all(self, names):
		"""self.get_all(string iterable) -> card.YugiohCard list
return list of all cards named"""
		return list(map(self.get, names))		
		
	def find(self, pred):
		"""self.find(card.YugiohCard -> bool) -> card.YugiohCard list
get a list of all cards for which the function pred is true."""
		return list(card for card in self._contents if pred(card))
		
	def find_all(self, preds):
		"""self.find_all( (card.YugiohCard -> bool) iterable) -> card.YugiohCard list
get a list of all cards for which any of the given predicates are true."""
		result = []
		for pred in preds:
			result.extend(self.find(pred))
		return result
		
	def enumerate(self):
		"""self.enumerate() -> card.YugiohCard list
get a list of all cards in the deck, with one copy of each card for every copy of the card that appears in the deck."""
		result = []
		for card, count in self._contents.items():
			for i in range(count):
				result.append(card)
		return result
		
class YugiohDeck(object):
	"""A full yugioh deck, containing main, side, and extra decks"""
	def __init__(self, name, author, main_deck=None, side_deck=None, extra_deck=None):
		"""The main deck. (YugiohSet)"""
		self.main = YugiohSet(main_deck)
		
		
		"""The side deck. (YugiohSet)"""
		self.side = YugiohSet(side_deck)
		
		
		"""The extra deck. (YugiohSet)"""
		self.extra = YugiohSet(extra_deck)

		"""the title of the deck (string)"""
		self.name = name
		
		"""the creator of the deck (string)"""
		self.author = author
		
	def all(self):
		"""self.all() -> YugiohSet
get a single YugiohSet holding every card in the deck, between main, extra, and side."""
		return YugiohSet(itertools.chain(self.main.enumerate(), self.side.enumerate(), self.extra.enumerate()))
		
	def __iter__(self):
		"""iter(self) -> YugiohCard iterable
only iterates over main deck by default"""
		return iter(self.main)
		
	def __len__(self):
		"""len(self) -> int
returns the size of the main deck by default"""
		return len(self.main)

	def as_ydk(self):
		"""self.as_ydk() -> string
get the deck as .ydk formatted text."""
		output = '#created by {0}\n'.format(self.author)
		output += '#main\n'
		for card in self.main.enumerate():
			output += '{0}\n'.format(card.cid)
		output += '#extra\n'
		for card in self.extra.enumerate():
			output += '{0}\n'.format(card.cid)
		output += '!side\n'
		for card in self.side.enumerate():
			output += '{0}\n'.format(card.cid)
		return output
		
	def as_markdown(self):
		"""self.as_markdown() -> string
get the deck as reddit-formatted markdown text."""
		monsters = self.main.find(YugiohCard.is_monster)
		output = '## {0}\n*by {1}*\n'.format(self.name, self.author)
		output += "# Monster:{0}\n".format(self.main.count_all(monsters))
		for monster in monsters:
			output += "- **{0}x {1}**\n".format(self.main.count(monster), monster.name)

		spells = self.main.find(YugiohCard.is_spell)			
		output += "\n# Spells:{0}\n".format(self.main.count_all(spells))
		for spell in spells:
			output += "- **{0}x {1}**\n".format(self.main.count(spell), spell.name)

		traps = self.main.find(YugiohCard.is_trap)			
		output += "\n# Traps:{0}\n".format(self.main.count_all(traps))
		for trap in traps:
			output += "- **{0}x {1}**\n".format(self.main.count(trap), trap.name)
		
		output += "\n---\n# Extra Deck: {0}\n".format(len(self.extra))
		for monster in self.extra:
			output += "- **{0}x {1}**\n".format(self.extra.count(monster), monster.name)
			
		output += "\n---\n# Side Deck: {0}\n".format(len(self.side))
		for card in self.side:
			output += "- **{0}x {1}**\n".format(self.side.count(card), card.name)
		output += "---\n"
		return output
		
	def as_decklist(self):
		"""self.as_decklist() -> string
convert the deck to a simple, easy-to-read decklist without the formatting markdown has"""
		output = '{0}\nby {1}\n'.format(self.name, self.author)
		monsters = self.main.find(YugiohCard.is_monster)
		output += 'Main Deck\n'	
		output += "  Monster({0})\n".format(self.main.count_all(monsters))
		for monster in monsters:
			output += "    {0} x{1}\n".format(monster.name, self.main.count(monster))

		spells = self.main.find(YugiohCard.is_spell)			
		output += "  Spells({0})\n".format(self.main.count_all(spells))
		for spell in spells:
			output += "    {0} x{1}\n".format(spell.name, self.main.count(spell))

		traps = self.main.find(YugiohCard.is_trap)			
		output += "  Traps({0})\n".format(self.main.count_all(traps))
		for trap in traps:
			output += "    {0} x{1}\n".format(trap.name, self.main.count(trap))
		
		output += "Extra Deck({0})\n".format(len(self.extra))
		for monster in self.extra:
			output += "    {0} x{1}\n".format(monster.name, self.extra.count(monster))
			
		output += "Side Deck({0})\n".format(len(self.side))
		for card in self.side:
			output += "    {0} x{1}\n".format(card.name, self.side.count(card))
		return output
