"""
This module does a lot of the math of consistency checking itself.

Algorithm:
	After getting a set of disjoint variables, it tries to generate
		every possible combination of the variables, while trimming
		the number of hands frequently. Since we'll usually have
		only 3-4 different groups, the number of hands stays fairly
		small, between 10-50. Worst case is if every card in a deck
		is its own group, which balloons to ~700,000 hands. This is
		still possible with modern computers, but is to be avoided.
		In exchange for this performance risk, it becomes vastly more
		expressive than any other similar tool I've found.
		
	Once we have all the possible hands, we use binomial coefficients
		to find out how many ways that a hand can occur given a specific
		deck.
		
	Finally, we see what proportion of the hands fulfill an expression,
		determine the number of ways to draw those hands, and divide
		that by the total number of possible hands.
"""
from .interface import all_cards, count_all, size
def choose(n, k):
	# classic combinatorics function.
	# see https://en.wikipedia.org/wiki/Combination
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

class Term(object):
	# a variable and the amount expected
	# exists as a lightweight data structure inside Hand.
	def __init__(self, k, cardset):
		self.cardset = cardset
		self.count = k
		
	def combinations(self, deck, hand_size=5):
		# determine how many ways the given set of cards can be drawn
		# such that there are exactly $(self.count) of them in a hand.
		total = count_all(deck, self.cardset)
		return choose(total, self.count)
		
	def __repr__(self):
		last = next(iter(self.cardset))
		return '{{{0}}}={1}'.format(str(last), self.count)

class Hand(object):
	# a set of rules for a hand one could draw from the deck.
	# basically just a list of Terms, with some convenience functions
	# for building them.
	def __init__(self, cards):
		self.__terms = cards
		
	def __iter__(self):
		return iter(self.__terms)
		
	@staticmethod
	def new(k, cards):
		#shorthand for creating a new Hand object.
		return Hand([Term(k, cards)])
		
	def add_term(self, k, cards):
		# shorthand for making a new Hand that is
		# just an extension of an old one
		return Hand( list(self) + [Term(k, cards)] )
		
	def __repr__(self):
		return '[{0}]'.format(', '.join(str(x) for x in self if x.count > 0))
		
	def size(self):
		# get number of cards in this hand.
		# useful for making sure you don't have 6 card hands
		# if your only expecting 5 cards.
		return sum(t.count for t in self)	
		
	def combinations(self, deck, hand_size=5):
		# get the number of ways to make this hand.
		# delegates to component Terms.
		combins = 1.0
		for term in self:
			combins *= term.combinations(deck, hand_size)
		return combins

def _filter_hands(hands, variables, deck, hand_size=5, complete=True):
	# given a set of hands, trim out all the ones that are impossible
	# if it is a finished hand that is too small, adds a dummy variable to fill the hand
	# used only inside generate_hands.
	for hand in hands:
		if hand.size() > hand_size:
			# if the hand is too large, dump it.
			continue
		elif hand.size() < hand_size and complete:
			# only works on the final pass when the hand has been
			# nominally finished. Adds new variable if the hand
			# is too small. The variable is just all the cards that
			# weren't mentioned in the given variables.
			diff = hand_size - hand.size()
			tmpvar = all_cards(deck) - set(v for varb in variables for v in varb)
			yield hand.add_term(diff, tmpvar)
		else:
			# checks that hand doesn't expect more copies of a card
			# than exist in the deck.
			legal = True
			for term in hand:
				if term.count > count_all(deck, term.cardset):
					legal = False
					break
			if legal:
				yield hand
			
def generate_hands(variables, deck, hand_size=5):
	# generates all possible hands of the given variable sets
	# loops over each variable, and adds some number of copies of
	# itself to each existing hand.
	handset = []
	for var in variables:
		swap = []
		if len(handset) == 0:
			# this runs only for the first variable.
			for x in range(0, hand_size+1):
				swap.append( Hand.new(x, var) )
		else:
			for hand in handset:
				for x in range(0, hand_size+1):
					swap.append( hand.add_term(x, var) )
		# remove as many hands as we can as we go
		# reducing exponential build
		handset = list(_filter_hands(swap, variables, deck, hand_size, complete=False))
		
	# do one more extra strength filter now that we are sure
	# of the final hands.
	return list(_filter_hands(handset, variables, deck, hand_size, complete=True))

