def choose(n, k):
	if n == k:
		return 1.0
	elif k == 0:
		return 1.0
	elif n == 0:
		return 0.0
	num = 1
	den = 1
	for i in range(0, k):
		num *= (n - i)
		den *= (k - i)
	return num / float(den)

class Deck:
	def __init__(self, size=None, **kwargs):
		self.counts = kwargs
		if size != None:
			s = sum(self.counts.values())
			diff = size - s
			self.counts['_'] = diff
			
	def count_all(self, cset):
		return sum(self.counts[key] for key in cset)
		
	def size(self):
		return sum(self.counts.values())


class Term(object):
	def __init__(self, k, cardset):
		self.cardset = cardset
		self.count = k
		
	def combinations(self, deck, hand_size=5):
		total = deck.count_all(self.cardset)
		return choose(total, self.count)
		
	def __repr__(self):
		return '{{{0}}}={1}'.format(''.join(self.cardset), self.count)

class Hand(object):
	def __init__(self, cards):
		self.__terms = cards
		
	def __iter__(self):
		return iter(self.__terms)
		
	@staticmethod
	def new(k, cards):
		return Hand([Term(k, cards)])
		
	def add_term(self, k, cards):
		return Hand( list(self) + [Term(k, cards)] )
		
	def __repr__(self):
		return '[{0}]'.format(', '.join(str(x) for x in self))
		
	def __getitem__(self, key):
		for term in self:
			if term.cardset == key:
				return term.count
		
	def size(self):
		return sum(t.count for t in self)	
		
	def combinations(self, deck, hand_size=5):
		combins = 1.0
		for term in self:
			combins *= term.combinations(deck, hand_size)
		return combins

def filter_hands(hands, deck, hand_size=5, complete=True):
	# given a set of hands, trim out all the ones that are impossible
	# if it is a finished hand that is too small, adds a dummy variable to fill the hand
	for hand in hands:
		if hand.size() > hand_size:
			continue
		elif hand.size() < hand_size and complete:
			diff = hand_size - hand.size()
			tmpvar = {'_'}
			yield hand.add_term(diff, tmpvar)
		else:
			legal = True
			for term in hand:
				if term.count > deck.count_all(term.cardset):
					legal = False
					break
			if legal:
				yield hand
			
def generate_hands(variables, deck, hand_size=5):
	# generates all possible hands of the given variable sets
	handset = []
	for var in variables:
		swap = []
		if len(handset) == 0:
			for x in range(0, hand_size+1):
				swap.append( Hand.new(x, var) )
		else:
			for hand in handset:
				for x in range(0, hand_size+1):
					swap.append( hand.add_term(x, var) )
		handset = list(filter_hands(swap, deck, hand_size, complete=False))
	return list(filter_hands(handset, deck, hand_size, complete=True))

def likelihood(hands, deck, f, hand_size=5):
	success = 0
	for hand in hands:
		if f(hand):
			success += hand.combinations(deck, hand_size)
	return float(success) / float(choose(deck.size(), hand_size))

if __name__ == '__main__':
	A = {'A'}
	B = {'B'}
			
	deck = Deck(size=40, A=9, B=16)
		
	hand_size = 5
		
	hands = generate_hands([A, B], deck, hand_size)

	print likelihood(hands, deck, lambda x: True, hand_size)
