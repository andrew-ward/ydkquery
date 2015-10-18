import collections
from card import YugiohCard

class YugiohSet(object):
	def __init__(self, cards):
		self._contents = {}
		if cards:
			self.add_cards(cards)
	def __len__(self):
		return self.size()
	def __iter__(self):
		return iter(self.all())
	def add(self, card):
		if card in self._contents:
			self._contents[card] += 1
		else:
			self._contents[card] = 1
	def add_card(self, card):
		self.add(card)
	def add_cards(self, cards):
		for card in cards:
			self.add_card(card)
	def size(self):
		return sum(self._contents.values())
	def count(self, card):
		return self._contents.get(card, 0)
	def count_all(self, cards):
		return sum(self.count(card) for card in cards)
	def get(self, name):
		'''get the card named from the deck.'''
		for card in self._contents.keys():
			if name == card.name():
				return card
	def get_all(self, names):
		return list(map(self.get, names))
	def find(self, pred):
		'''get a set of all cards for which the function pred is true.'''
		return set(card for card in self._contents if pred(card))
	def find_all(self, preds):
		result = set()
		for pred in preds:
			result = result & self.find(pred)
		return result
	def all(self):
		return set(self._contents.keys())
	def enumerate(self):
		result = []
		for card, count in self._contents.items():
			for i in range(count):
				result.append(card)
		return result
		
class YugiohDeck(object):
	def __init__(self, name, author, main_deck=None, side_deck=None, extra_deck=None):
		self.main = YugiohSet(main_deck)
		self.side = YugiohSet(side_deck)
		self.extra = YugiohSet(extra_deck)

		'''the title of the deck'''
		self.name = name
		
		'''the creator of the deck'''
		self.author = author
		
	def __iter__(self):
		return iter(self.main)
	def __len__(self):
		return len(self.main)

	def as_ydk(self):
		''' convert the deck to a .ydk formatted string.'''
		output = '#created by {0}\n'.format(self.author)
		output += '#main\n'
		for card in self.main.enumerate():
			output += '{0}\n'.format(card.cid())
		output += '#extra\n'
		for card in self.extra.enumerate():
			output += '{0}\n'.format(card.cid())
		output += '!side\n'
		for card in self.side.enumerate():
			output += '{0}\n'.format(card.cid())
		return output
		
	def as_markdown(self):
		''' convert the deck to a decklist string formatted for reddit-style markdown'''
		monsters = self.main.find(YugiohCard.is_monster)				
		output = "# Monster:{0}\n".format(self.main.count_all(monsters))
		for monster in monsters:
			output += "- **{0}x {1}**\n".format(self.main.count(monster), monster.name())

		spells = self.main.find(YugiohCard.is_spell)			
		output += "\n# Spells:{0}\n".format(self.main.count_all(spells))
		for spell in spells:
			output += "- **{0}x {1}**\n".format(self.main.count(spell), spell.name())

		traps = self.main.find(YugiohCard.is_trap)			
		output += "\n# Traps:{0}\n".format(self.main.count_all(traps))
		for trap in traps:
			output += "- **{0}x {1}**\n".format(self.main.count(trap), trap.name())
		
		output += "\n---\n# Extra Deck: {0}\n".format(len(self.extra))
		for monster in self.extra:
			output += "- **{0}x {1}**\n".format(self.extra.count(monster), monster.name())
			
		output += "\n---\n# Side Deck: {0}\n".format(len(self.side))
		for card in self.side:
			output += "- **{0}x {1}**\n".format(self.side.count(card), card.name())
		output += "---\n"
		return output
		
	def as_decklist(self):
		'''convert the deck to a simple, easy-to-read decklist without the formatting markdown has'''
		monsters = self.main.find(YugiohCard.is_monster)
		output = 'Main Deck\n'	
		output += "  Monster({0})\n".format(self.main.count_all(monsters))
		for monster in monsters:
			output += "    {0} x{1}\n".format(monster.name(), self.main.count(monster))

		spells = self.main.find(YugiohCard.is_spell)			
		output += "  Spells({0})\n".format(self.main.count_all(spells))
		for spell in spells:
			output += "    {0} x{1}\n".format(spell.name(), self.main.count(spell))

		traps = self.main.find(YugiohCard.is_trap)			
		output += "  Traps({0})\n".format(self.main.count_all(traps))
		for trap in traps:
			output += "    {0} x{1}\n".format(trap.name(), self.main.count(trap))
		
		output += "Extra Deck({0})\n".format(len(self.extra))
		for monster in self.extra:
			output += "    {0} x{1}\n".format(monster.name(), self.extra.count(monster))
			
		output += "Side Deck({0})\n".format(len(self.side))
		for card in self.side:
			output += "    {0} x{1}\n".format(card.name(), self.side.count(card))
		return output
