import sys, re
from . import abstract, card
	
class APIError(RuntimeError):
	pass


def get_price_data(card):
	url = "http://yugiohprices.com/api/get_card_prices/"+abstract.quote_plus(card.name)
	data = abstract.get_json(url)
	output = []
	if 'status' in data and data['status'] == 'success':
		data = data['data']
		for run in data:
			rarity = run['rarity']
			print_tag = run['print_tag']
			price_summary = PriceSummary()
			listings = []
			if 'status' in run['price_data'] and run['price_data']['status'] == 'success':
				print_data = run['price_data']['data']
				price_summary = PriceSummary(print_data['prices'])
				listings = print_data['listings']
			pcard = PrintedCard(card, print_tag, rarity, price_summary, listings)
			output.append(pcard)
	return output

class PriceSummary(dict):
	def __getattr__(self, key):
		if key in self:
			return self[key]
		else:
			return None
	def __setitem__(self, key, value):
		raise NotImplementedError("PriceSummary.__setitem__")

class PrintedCard(card.YugiohCard):
	def __init__(self, original, print_tag, rarity, summary, listings):
		self.clone(original)
		self.properties['rarity'] = rarity
		self.properties['print_tag'] = print_tag
		self.price = summary
		self.listings = listings
	def __hash__(self):
		return hash(self.print_tag + self.id)
	def __eq__(self, other):
		return isinstance(other, PrintedCard) and self.print_tag == other.print_tag
	def __lt__(self, other):
		return self.print_tag < other.print_tag
	def __gt__(self, other):
		return self.print_tag > other.print_tag

def get_cheapest_price(printed_cards):
	least = None
	for card in printed_cards:
		if least == None or (card.price.average is not None and card.price.average < least):
			least = card.price.average
	return least

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
			
