"""The datatypes holding information about a yugioh deck."""

import collections
import itertools
from .card import YugiohCard

class YugiohSet(object):
	"""A set of yugioh cards that can be query'd"""
	def __init__(self, cards):
		self._contents = {}
		if cards:
			self.add_cards(cards)
			
	def __len__(self):
		"""
		:returns: Number of cards in the deck.
		:rtype: int"""
		return self.size()
		
	def __iter__(self):
		"""
		:returns: an iterator over each unique card in the deck. If you have two copies of the same card, it will only appear once.
		:rtype: iterator of card.YugiohCard"""
		return iter(self._contents.keys())
		
	def all(self):
		"""
		:returns: list of unique cards in the deck. If you have two copies of the same card, it will only appear once.
		:rtype: list of card.YugiohCard"""
		return list(self._contents.keys())
		
	def __getitem__(self, key):
		"""Return the number of copies of the given card in the deck"""
		return self.count(key)

	def add_card(self, card, count=1):
		"""Add a card to the deck.
		
		:param card: the card to add
		:type card: card.YugiohCard
		:param count: the number of copies to add (max 3)
		:type count: int
		:returns: None"""
		assert(isinstance(count, int))
		if card in self._contents:
			self._contents[card] += count
		else:
			self._contents[card] = count
			
	def add_cards(self, cards):
		"""Add multiple cards to the deck.
		
		:param cards: the cards to add
		:type cards: iterable of card.YugiohCard
		:returns: None"""
		for card in cards:
			self.add_card(card)
			
	def size(self):
		"""
		:returns: Number of cards in the deck.
		:rtype: int"""
		return sum(self._contents.values())
		
	def count(self, card):
		"""		
		:param card: the card to count
		:type card: card.YugiohCard
		
		:returns: number of copies in the deck
		:rtype: int"""
		return self._contents.get(card, 0)
		
	def count_all(self, cards):	
		"""		
		:param cards: the card to count
		:type cards: iterable of card.YugiohCard
		
		:returns: number of copies in the deck
		:rtype: int"""
		return sum(self.count(card) for card in cards)		
		
	def get(self, name):
		"""		
		:param name: the name of a card in the deck
		:type name: string
		
		:returns: the card named
		:rtype: card.YugiohCard"""
		for card in self._contents.keys():
			if name == card.name:
				return card				
				
	def get_all(self, names):
		"""		
		:param names: the names of a card in the deck
		:type nams: iterable of string
		
		:returns: the cards named
		:rtype: list of card.YugiohCard"""
		return list(map(self.get, names))		
		
	def find(self, pred):
		"""
		:param pred: a predicate to test on cards in the deck.
		:type pred: card.YugiohCard -> boolean
		
		:returns: the cards for which pred evaluated to true.
		:rtype: list of card.YugiohCard"""
		return list(card for card in self._contents if pred(card))
		
	def find_all(self, preds):
		"""
		:param preds: a series of predicates to test on cards in the deck.
		:type preds: iterable of (card.YugiohCard -> boolean)
		
		:returns: the cards for which any of the predicates evaluated to true.
		:rtype: list of card.YugiohCard"""
		result = []
		for pred in preds:
			result.extend(self.find(pred))
		return result
		
	def enumerate(self):
		"""
		:returns: A list of all cards in the deck, with one copy of each card for every copy of the card that appears in the deck.
		:rtype: list of card.YugiohCard"""
		result = []
		for card, count in self._contents.items():
			for i in range(count):
				result.append(card)
		return result
		
class YugiohDeck(object):
	"""A full yugioh deck, containing main, side, and extra decks
	
	:ivar name: The title of the deck.
	:vartype name: string
	
	:ivar author: The creator of the deck.
	:vartype author: string
	
	:ivar main: The main deck
	:vartype main: YugiohSet
	
	:ivar side: The side deck
	:vartype side: YugiohSet
	
	:ivar extra: The extra deck
	:vartype extra: YugiohSet"""
	def __init__(self, name, author, main_deck=None, side_deck=None, extra_deck=None):
		self.main = YugiohSet(main_deck)
		
		self.side = YugiohSet(side_deck)
		
		self.extra = YugiohSet(extra_deck)

		self.name = name
		
		self.author = author
		
	def all(self):
		"""
		:returns: A single YugiohSet holding every card in the deck, between main, extra, and side.
		:rtype: YugiohSet"""
		return YugiohSet(itertools.chain(self.main.enumerate(), self.side.enumerate(), self.extra.enumerate()))
		
	def __iter__(self):
		"""Iterates over main deck by default"""
		return iter(self.main)
		
	def __len__(self):
		"""Returns the size of the main deck by default"""
		return len(self.main)

	def as_ydk(self):
		"""
		:returns: the deck as .ydk formatted text.
		:rtype: string"""
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
		"""
		:returns: the deck as reddit-formatted markdown text.
		:rtype: string"""
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
		"""
		:returns: the deck as an easy-to-read raw text format.
		:rtype: string"""
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
