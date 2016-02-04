"""The datatypes holding information about a yugioh deck."""

import collections
import itertools
from .card import YugiohCard

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
		return self.size()
		
	def __iter__(self):
		"""
		:returns: an iterator over each unique card in the deck. If you have two copies of the same card, it will only appear once.
		:rtype: iterator of card.YugiohCard"""
		return iter(self._contents.keys())
		
	def unique(self):
		"""
		:returns: list of unique cards in the deck. If you have two copies of the same card, it will only appear once.
		:rtype: list of card.YugiohCard"""
		return list(self._contents.keys())
	
	def all(self):
		"""
		:returns: all cards in the deck. If there are two or more copies of the card, it will return the card twice.
		:rtype: list of card.YugiohCard"""
		return self.enumerate()
	
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
		assert(isinstance(card, YugiohCard))
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
		
	def monsters(self):
		result = []
		for card in self.all():
			if card.is_monster():
				result.append(card)
		return YugiohSet(result)
		
	def spells(self, unique=True):
		result = []
		for card in self.all():
			if card.is_spell():
				result.append(card)
		return YugiohSet(result)
		
	def traps(self, unique=True):
		result = []
		for card in self.all():
			if card.is_trap():
				result.append(card)
		return YugiohSet(result)

	def as_deck(self):
		main = []
		extra = []
		for card in self.all():
			if card.in_main_deck():
				main.append(card)
			elif card.in_extra_deck():
				extra.append(card)
		return YugiohDeck('', '', main_deck=main, extra_deck=extra)
		
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
		if isinstance(main_deck, YugiohSet):
			self.main = main_deck
		else:
			self.main = YugiohSet(main_deck)
			
		if isinstance(side_deck, YugiohSet):
			self.side = side_deck
		else:		
			self.side = YugiohSet(side_deck)
		
		if isinstance(extra_deck, YugiohSet):
			self.extra = extra_deck
		else:
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
