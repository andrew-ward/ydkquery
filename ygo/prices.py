from .core import yugiohprices, card, deck
from . import search

class CardRelease(object):
	def __init__(self, print_tag, set_name, rarity, price_data):
		self.print_tag = print_tag
		self.set_name = set_name
		self.rarity = rarity
		if price_data:
			self.has_price = True
			self.low = price_data['low']
			self.high = price_data['high']
			self.average = price_data['average']
			self.delta = price_data['shift']
		else:
			self.has_price = False
			self.low = None
			self.high = None
			self.average = None
			self.delta = None
	def __hash__(self):
		return hash(self.print_tag)
	def __eq__(self, other):
		return isinstance(other, CardRelease) and self.print_tag == other.print_tag
	def is_holo(self):
		return self.rarity not in ('Common', 'Rare', 'Short Print')
		

def rarity_score(rarity):
	rl = rarity.lower()
	if 'common' in rl:
		if 'super' in rl and 'short' in rl and 'print' in rl:
			return 2
		elif 'short' in rl and 'print' in rl:
			return 1
		else:
			return 0
	elif 'rare' in rl:
		if 'super' in rl:
			return 4
		elif 'ultra' in rl:
			return 5
		elif 'secret' in rl:
			return 6
		elif 'ultimate' in rl:
			return 7
		elif any(x in rl for x in ['parallel','starfoil','shatterfoil', 'gold', 'platinum']):
			return 8
		elif 'ghost' in rl:
			return 9
		else:
			return 3
	elif 'super' in rl:
		return 4
	elif 'ultra' in rl:
		return 5
	elif 'secret' in rl:
		return 6
	elif 'ultimate' in rl:
		return 7
	elif 'ghost' in rl:
		return 9
	else:
		return 8
			

			
class ReleaseSet(object):
	def __init__(self, card, versions):
		self.card = card
		self._versions = set(versions)
		self.has_price = any(x.has_price for x in self._versions)
	def __iter__(self):
		return iter(self._versions)
	def __len__(self):
		return len(self._versions)
	def holos(self):
		return ReleaseSet(self.card, (x for x in self._versions if x.is_holo()))
	def select(self, f):
		return ReleaseSet(self.card, (x for x in self._versions if f(x)))
	def price_sort(self, key='low'):
		if key == 'low':
			return list(sorted(self._versions, key=lambda x: x.low))
		elif key == 'high':
			return list(sorted(self._versions, key=lambda x: x.high))
		elif key == 'average':
			return list(sorted(self._versions, key=lambda x: x.average))
		elif key == 'average':
			return list(sorted(self._versions, key=lambda x: x.average))
		elif key == 'hype':
			return list(sorted(self._versions, key=lambda x: x.hype()))
		else:
			return list(sorted(self._versions, key=f))
	def cheapest_release(self):
		if self.has_price:
			return min((x.low, x) for x in self if x.has_price)[1]
	def cheapest_price(self):
		if self.has_price:
			return min(x.low for x in self if x.has_price)
		else:
			return None

def card_versions(card_key, fail=False):
	card = search.find(card_key)
	if fail:
		all_data = yugiohprices.get_card_prices(card.name)
	else:
		try:
			all_data = yugiohprices.get_card_prices(card.name)
		except yugiohprices.APIError:
			return ReleaseSet(card, [])
	results = []
	for dat in all_data:
		results.append(CardRelease(
			dat['print_tag'],
			dat['set_name'],
			dat['rarity'],
			dat['price_data']))
	return ReleaseSet(card, results)

def card_sets():
	return yugiohprices.card_sets()

def card_support(card_key):
	card = search.find(card_key)
	support = yugiohprices.card_support(card.name.encode('utf8', 'replace'))
	result = []
	for name in support:
		result.append(search.find(name))
	return deck.YugiohSet(result)
