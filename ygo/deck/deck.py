"""The datatypes holding information about a yugioh deck."""

import collections
import itertools

class YugiohSet(object):
	"""A set of yugioh cards that can be query'd"""
	def __init__(self, cards=None):
		self._contents = {}
		if cards:
			self.add_cards(cards)
			
	def __len__(self):
		"""
		:returns: Number of cards in the deck.
		:rtype: int"""
		return sum(self._contents.values())

	def __str__(self):
		cards = []
		for card, count in self._contents.items():
			text = str(card)
			if count > 1:
				text += ' x' + str(count)
			cards.append(text)
		return '{' + ', '.join(cards) + '}'
		
	def __iter__(self):
		"""
		:returns: an iterator over each unique card in the deck. If you have two copies of the same card, it will only appear once.
		:rtype: iterator of card.YugiohCard"""
		return iter(self.keys())

	def keys(self):
		return self._contents.keys()

	def values(self):
		"""
		:returns: A list of all cards in the deck, with one copy of each card for every copy of the card that appears in the deck.
		:rtype: list of card.YugiohCard"""
		for card, count in self._contents.items():
			for i in range(count):
				yield card

	def items(self):
		return self._contents.items()

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

	def count(self, *cards):
		"""		
		:param cards: the cards to count
		:type cards: card.YugiohCard
		
		:returns: number of copies in the deck
		:rtype: int"""
		return sum(self._contents.get(card, 0) for card in cards)	
		
	def monsters(self):
		result = []
		for card in self.values():
			if card.is_monster():
				result.append(card)
		return YugiohSet(result)
		
	def spells(self, unique=True):
		result = []
		for card in self.values():
			if card.is_spell():
				result.append(card)
		return YugiohSet(result)
		
	def traps(self, unique=True):
		result = []
		for card in self.values():
			if card.is_trap():
				result.append(card)
		return YugiohSet(result)

	def as_deck(self):
		main = []
		extra = []
		for card in self.values():
			if card.in_main_deck():
				main.append(card)
			elif card.in_extra_deck():
				extra.append(card)
		return YugiohDeck('', '', main_deck=main, extra_deck=extra)
		
class YugiohDeck(dict):
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
	def __init__(self, name, author, main, side, extra):
		dict.__init__(self, {
			'name': name,
			'author': author,
			'main': main if isinstance(main, YugiohSet) else YugiohSet(main),
			'side': side if isinstance(side, YugiohSet) else YugiohSet(side),
			'extra': extra if isinstance(extra, YugiohSet) else YugiohSet(extra),
		})
	def __getattr__(self, key):
		if key in self:
			return self[key]
		else:
			raise AttributeError("'{}' object has not attribute '{}'".format(self.__class__.__name__, key))
		
	def as_set(self):
		"""
		:returns: A single YugiohSet holding every card in the deck, between main, extra, and side.
		:rtype: YugiohSet"""
		return YugiohSet(itertools.chain(self.main.enumerate(), self.side.enumerate(), self.extra.enumerate()))
