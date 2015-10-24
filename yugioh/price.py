"""contains datatypes that represent pricing information about cards.
Built to work with yugioh.yugiohprices"""

class PriceHistory(object):
	"""Contains all the price information about a single print run of a card. You shouldn't need to create an instance of this manually."""
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
		"""Highest reported price"""
		self.high = high
		
		"""Typical reported price"""
		self.average = avg
		
		"""Lowest reported price"""
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
		"""delta(int timeframe) -> int
		
		Return how much the price has changed over the last n days. Supported timeframes are 1, 3, 7, 21, 30, 90, 180, 365"""
		if timeframe not in self._delta:
			raise TypeError('Cannot get price change data over last {0} days'.format(timeframe))
		return self._delta[timeframe]


class CardVersion(object):
	"""Represents all the information available for a single print run of a card. """
	def __init__(self, set_name, print_tag, rarity, price):
		"""The set the card came out in (string)"""
		self.set_name = set_name
		
		"""The unique print id for each card (string)"""
		self.print_tag = print_tag
		
		"""The rarity the card was printed in (string)"""
		self.rarity = rarity
		
		"""The price of the card (PriceHistory)"""
		self.price = price # a PriceHistory object
		
	def __str__(self):
		return '{0} {1} from {2}'.format(self.rarity, str(self.price) if self.price else '??', self.set_name)
		
	def __repr__(self):
		return 'CardVersion({0})'.format(str(self))
		
	def __hash__(self):
		return hash(self.print_tag)
		
	def __eq__(self):
		return isinstance(other, CardRelease) and self.print_tag == other.print_tag
