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
