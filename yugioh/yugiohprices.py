"""
A frontend for the yugiohprices api. Gets price data on a card.

May eventually create a more in-depth query library that uses this api.
"""

import json
import sys, re
from . import core, ygopro

if sys.version_info.major == 2:
	from urllib import urlopen, quote_plus
elif sys.version_info.major == 3:
	from urllib.request import urlopen
	from urllib.parse import quote_plus
else:
	svi = sys.version_info
	raise NotImplementedError('Python version {0}.{1}.{3} not supported'.format(svi.major, svi.minor, svi.micro))
	
class APIError(RuntimeError):
	pass

def _get_version_data(info):
	return CardVersion(
		info['name'],
		info['print_tag'],
		info['rarity'],
		_get_price_data(info['price_data'])
	)
def _get_price_data(info):
	if info['status'] == 'success':
		pinfo = info['data']['prices']
		return PriceHistory(
			pinfo['high'],
			pinfo['average'],
			pinfo['low'],
			{
				  1 : pinfo['shift'],
				  3 : pinfo['shift_3'],
				  7 : pinfo['shift_7'],
				 30 : pinfo['shift_30'],
				 90 : pinfo['shift_90'],
				180 : pinfo['shift_180'],
				365 : pinfo['shift_365']
			}
		)
		
def _api_request(url):
	fl = urlopen(url)
	if sys.version_info.major == 3:
		text = fl.readall().decode('utf-8')
	else:
		text = fl.read()
	info = json.loads(text)	
	fl.close()
	if info['status'] == 'fail':
		raise APIError('Got error "{0}" while trying to make api request {1}'.format(info['message'], url))
	else:
		return info['data']
		
def get_card_price_data(card):
	"""Get price data about card from YugiohPrices.com api, by using a card object.

:param card: a yugioh card.
:type card: core.card.YugiohCard
:returns: list of price data for that print run.
:rtype: list of price.CardVersion
:raises: yugiohprices.APIError
"""
	cname = quote_plus(card.name.encode('utf8', 'replace'))
	url = 'http://yugiohprices.com/api/get_card_prices/{0}'.format(cname)
	data = _api_request(url)
	return [_get_version_data(version) for version in data]
	
def get_name_price_data(card_name):
	"""Get price data about card from YugiohPrices.com api, by using the card's name.

:param card: The name of a yugioh card.
:type card: string
:returns: list of price data for that print run.
:rtype: list of price.CardVersion
:raises: yugiohprices.APIError
"""
	cname = quote_plus(card_name)
	url = 'http://yugiohprices.com/api/get_card_prices/{0}'.format(cname)
	data = _api_request(url)
	return [_get_version_data(version) for version in data]
	
def get_print_tag_price_data(print_tag):
	"""Get price data about card from YugiohPrices.com api, by using the unique print tag.

:param card: The valid print tag of a yugioh card.
:type card: string
:returns: list of price data for that print run.
:rtype: list of price.CardVersion
:raises: yugiohprices.APIError
"""
	cname = quote_plus(print_tag)
	url = 'http://yugiohprices.com/api/price_for_print_tag/{0}'.format(cname)
	data = _api_request(url)
	return [_get_version_data(data['price_data'])]
	
def get_price_data(arg):
	"""Get price data about card from YugiohPrices.com api.

:param card: card to get data about. Can be any of YugiohCard, print tag, card name, or card id.
:type card: core.card.YugiohCard or string
:returns: list of price data for each print run of the card.
:rtype: list of price.CardVersion
:raises: yugiohprices.APIError
"""
	if isinstance(arg, core.card.YugiohCard):
		return get_card_price_data(arg)
	elif arg.isdigit():
		card = ygopro.load_card(arg, by='id')
		return get_card_price_data(card)
	elif re.match('^[A-Z0-9]+-[A-Z]*[0-9]+$', arg):
		return get_print_tag_price_data(arg)
	else:
		return get_name_price_data(arg)

def load_card(print_tag):
	"""Use unique print run set/number tags to find a card.
	
	:param print_tag: The print tag for a particular reprint of a card. For example, SDK-001 for the Starter Deck: Kaiba Ultra Rare Blue-Eyes White Dragon.
	:type print_tag: string
	:returns: the card
	:rtype: core.database.YGOProCard
	:raises: core.database.CardNotFoundException
	:raises: yugiohprices.APIError"""
	if not re.match('^[A-Z0-9]+-[A-Z]*[0-9]+$', print_tag):
		raise APIError('{0} is not a valid print tag.'.format(print_tag))
	cname = quote_plus(print_tag)
	url = 'http://yugiohprices.com/api/price_for_print_tag/{0}'.format(cname)
	
	fl = urlopen(url)
	if sys.version_info.major == 3:
		text = fl.readall().decode('utf-8')
	else:
		text = fl.read()
	info = json.loads(text)
	
	if info['status'] == 'fail':
		raise APIError('Got error "{0}" while trying to find card {1}'.format(info['message'], print_tag))
	else:
		card_name = info['data']['name']
		return ygopro.load_card(card_name, by='name')

def get_price(card):
	"""Get the minimum expected price for the given card.
	
	:param card: the card
	:type card: core.card.YugiohCard
	:returns: price in dollars
	:rtype: int
	:raises: yugiohprices.APIError"""
	card_data = get_price_data(card)
	prices = [version.price.low for version in card_data if version.price]
	if len(prices) == 0:
		raise APIError('No prices available for {0}'.format(card.name))
	else:
		return min(prices)


"""contains datatypes that represent pricing information about cards.
Built to work with yugioh.yugiohprices"""

class PriceHistory(object):
	"""Contains all the price information about a single print run of a card. You shouldn't need to create an instance of this manually.

:ivar high: Highest reported price.
:vartype high: int

:ivar average: Average reported price
:vartype average: int

:ivar low: Lowest reported price.
:vartype low: int
"""
	def __init__(self, high, avg, low, delta = None):
		self._delta = delta or {
			1 : 0,
			3 : 0,
			7 : 0,
			30 : 0,
			90 : 0,
			180 : 0,
			365 : 0
		}
		
		self.high = high
		
		self.average = avg
		
		self.low = low
		
	def __str__(self):
		return '${0:.2f}'.format(self.average)
		
	def __lt__(self, other):
		"""Check if one price is cheaper on average than another"""
		if isinstance(other, PriceHistory):
			return self.average < other.average
		else:
			return self.average < other
			
	def __gt__(self, other):
		"""Check if one price is more expensive on average than another"""
		if isinstance(other, PriceHistory):
			return self.average > other.average
		else:
			return self.average < other	
		
	def delta(self, timeframe):
		"""Return how much the price has changed over the last n days. Supported timeframes are 1, 3, 7, 21, 30, 90, 180, 365

		:param timeframe: how many days ago you would like to compare to.
		:type timeframe: int
		:returns: the change in price since n days ago in dollars
		:rtype: int"""
		if timeframe not in self._delta:
			raise TypeError('Cannot get price change data over last {0} days'.format(timeframe))
		return self._delta[timeframe]


class CardVersion(object):
	"""Represents all the information available for a single print run of a card.

:ivar name: The card this is a print of.
:vartype name: string

:ivar set_name: The set the card came out in.
:vartype set_name: string

:ivar print_tag: The unique print id for each card.
:vartype print_tag: string

:ivar rarity: The rarity the card was printed in.
:vartype rarity: string

:ivar price: The price of the card.
:vartype price: PriceHistory
"""
	def __init__(self, set_name, print_tag, rarity, price):
		
		self.set_name = set_name
		
		self.print_tag = print_tag
				
		self.rarity = rarity
		
		self.price = price
		
	def __str__(self):
		return '{0} {1} from {2}'.format(self.rarity, str(self.price) if self.price else '??', self.set_name)
		
	def __repr__(self):
		return 'CardVersion({0})'.format(str(self))
		
	def __hash__(self):
		return hash(self.print_tag)
		
	def __eq__(self):
		return isinstance(other, CardRelease) and self.print_tag == other.print_tag
