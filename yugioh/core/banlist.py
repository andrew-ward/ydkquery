"""This module is for managing the banlist (lflist.conf) files supplied by ygopro."""
import re
from . import config

class ParseError(RuntimeError):
	pass

class Banlist(object):
	"""Holds all the information for a single banlist.
	
	:ivar name: the name of the banlist
	:vartype name: string"""
	def __init__(self, name, f, l, s):
		self.name = name
		self._cards = {}
		for cid in f:
			self._cards[cid] = 0
		for cid in l:
			self._cards[cid] = 1
		for cid in s:
			self._cards[cid] = 2
	def __repr__(self):
		return 'Banlist({0})'.format(self)
	def __str__(self):
		return self.name
	
	def allowed(self, card):
		return self._cards.get(card.cid, 3)
		
	def forbidden_cards(self):
		"""
		:returns: list of all forbidden cards
		:type: list of core.card.YugiohCard"""
		return list(card for (card, n) in self._cards.items() if n == 0)
		
	def limited_cards(self):
		"""
		:returns: list of all forbidden cards
		:type: list of core.card.YugiohCard"""
		return list(card for (card, n) in self._cards.items() if n == 1)

	def semi_limited_cards(self):
		"""
		:returns: list of all forbidden cards
		:type: list of core.card.YugiohCard"""
		return list(card for (card, n) in self._cards.items() if n == 2)
		
	def forbidden(self, cid):
		"""Check if a card is forbidden
		
		:param cid: card id of the card you want to check
		:type cid: string
		:returns: whether card is forbidden
		:rtype: boolean"""
		return self[cid] == 0
		
	def limited(self, cid):
		"""Check if a card is limited
		
		:param cid: card id of the card you want to check
		:type cid: string
		:returns: whether card is limited
		:rtype: boolean"""
		return self[cid] == 1
		
	def semi_limited(self, cid):
		"""Check if a card is semi_limited
		
		:param cid: card id of the card you want to check
		:type cid: string
		:returns: whether card is semi_limited
		:rtype: boolean"""
		return self[cid] == 2
		
	def unlimited(self, cid):
		"""Check if a card is unlimited
		
		:param cid: card id of the card you want to check
		:type cid: string
		:returns: whether card is unlimited
		:rtype: boolean"""
		return self[cid] == 3
		
			
		
def load_banlists(banlist_path=None):
	"""Get every banlist available as a list. Used by yugioh.core.database.
	
	:param banlist_path: the path to the lflist.conf supplied by ygopro.
	:type banlist_path: string
	
	:returns: list of all the banlists information available.
	:rtype: list of Banlist	"""
	banlist_path = banlist_path or config.BANLIST_PATH
	if banlist_path == None:
		raise IOError('Cannot access banlist. Check your configuration.')
	with open(banlist_path, 'r') as fl:
		lines = [x.rstrip() for x in fl.readlines()]
		banlists = []
		
		forbidden = []
		limited = []
		semi_limited = []
		name = None
		current = None
		
		row_re = re.compile('^(\d+) *[012] *--(.*?)$')
		
		for line in lines[1:]:
			if line.startswith('!'):
				if current != None:
					bl = Banlist(name, forbidden, limited, semi_limited)
					banlists.append(bl)
				name = line[1:]
				forbidden = []
				limited = []
				semi_limited = []
				current = None
			elif line.startswith('#forbidden'):
				current = forbidden
			elif line.startswith('#limit'):
				current = limited
			elif line.startswith('#semi limit'):
				current = semi_limited
			elif len(line.strip()) == 0:
				continue
			else:
				match = row_re.match(line)
				cid = match.group(1)
				current.append(cid)
		if current != None:
			bl = Banlist(name, forbidden, limited, semi_limited)
			banlists.append(bl)
		return banlists
