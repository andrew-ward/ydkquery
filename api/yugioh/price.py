class PriceHistory(object):
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
		if isinstance(other, PriceHistory):
			return self.average < other.average
		else:
			return self.average < other
			
	def __gt__(self, other):
		if isinstance(other, PriceHistory):
			return self.average > other.average
		else:
			return self.average < other	
		
	def change(self, timescale):
		if timescale not in self._delta:
			raise TypeError('Cannot get price change data over last {0} days'.format(timescale))
		return self._delta[timescale]


class CardVersion(object):
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
