import operator
import itertools
import cons3
class SyntaxError(RuntimeError):
	def __init__(self):
		RuntimeError.__init__(self, 'SyntaxError'.format(s))
		
class AST(object):
	def __call__(self, hand):
		raise NotImplementedError(type(self))
	def __eq__(self, other):
		if isinstance(other, int):
			return Equal([self, Number(other)])
		else:
			return Equal([self, other])
			
	def __lt__(self, other):
		if isinstance(other, int):
			return LessThan([self, Number(other)])
		else:
			return LessThan([self, other])
			
	def __gt__(self, other):
		if isinstance(other, int):
			return GreaterThan([self, Number(other)])
		else:
			return GreaterThan([self, other])
			
	def __and__(self, other):
		if isinstance(other, int):
			raise SyntaxError()
		elif isinstance(other, And):
			return other & self
		else:
			return And([self, other])
			
	def __or__(self, other):
		if isinstance(other, int):
			raise SyntaxError()
		elif isinstance(other, Or):
			return other | self
		else:
			return Or([self, other])
			
	def __add__(self, other):
		if isinstance(other, int):
			return Add([self, Number(other)])
		elif isinstance(other, Add):
			return other + self
		else:
			return Add([self, other])
	
class Number(AST):
	def __init__(self, n):
		self.value = n
	def __str__(self):
		return str(self.value)
	def __call__(self, hand):
		return self.value
	def variables(self):
		return frozenset()
		
class Cardset(AST):
	def __init__(self, cset):
		self.cards = frozenset(cset)
	def __str__(self):
		return '{' + ','.join(str(x) for x in self.cards) + '}'
	def __call__(self, hand):
		total = 0
		for term in hand:
			if self.cards <= term.cardset:
				total += term.count
		return total
	def variables(self):
		yield self.cards
	
class Constraint(AST):
	def __init__(self, terms):
		self.__terms = terms
		
	def __iter__(self):
		return iter(self.__terms)		
			
	def variables(self):
		results = []
		for new_term in itertools.chain(*(x.variables() for x in self)):
			swap = []
			for curr_var in results:
				if len(new_term) == 0:
					swap.append( curr_var )
					
				elif new_term == curr_var:
					new_term = frozenset()
					swap.append( curr_var )
					
				elif new_term <= curr_var:
					swap.append( new_term )
					swap.append( curr_var - new_term )
					new_term = frozenset()
					
				elif new_term >= curr_var:
					swap.append( curr_var )
					new_term = new_term - curr_var
					
				elif len(new_term & curr_var) > 0:
					swap.append( curr_var - new_term )
					swap.append( curr_var & new_term )
					new_term = new_term - curr_var
					
				else:
					swap.append( curr_var )
			if len(new_term) > 0:
				swap.append( new_term )
			results = swap
		return results
				
class And(Constraint):
	def __str__(self):
		return '({0})'.format(' & '.join(map(str, self)))
	def __call__(self, hand):
		return all(term(hand) for term in self)

class Or(Constraint):
	def __str__(self):
		return '({0})'.format(' | '.join(map(str, self)))
	def __call__(self, hand):
		return any(term(hand) for term in self)
		
class Add(Constraint):
	def __str__(self):
		return '({0})'.format(' + '.join(map(str, self)))
	def __call__(self, hand):
		return sum(term(hand) for term in self)
		
class GreaterThan(Constraint):
	def __str__(self):
		return '({0})'.format(' > '.join(map(str, self)))
	def __call__(self, hand):
		last = None
		for term in self:
			if last == None or last > term(hand):
				last = term(hand)
			else:
				return False
		return True

class LessThan(Constraint):
	def __str__(self):
		return '({0})'.format(' < '.join(map(str, self)))
	def __call__(self, hand):
		last = None
		for term in self:
			if last == None or last < term(hand):
				last = term(hand)
			else:
				return False
		return True
		
class Equal(Constraint):
	def __str__(self):
		return '({0})'.format(' = '.join(map(str, self)))
	def __call__(self, hand):
		last = None
		for term in self:
			if last == None or last == term(hand):
				last = term(hand)
			else:
				return False
		return True

if __name__ == '__main__':
	a = Cardset({'A'})
	b = Cardset({'B'})
	valid1 = ((a + b) == 2) & (a > 0)
	valid2 = ((a==1) & (b==1))
	variable_list = valid1.variables()
	deck = cons3.Deck(size=10, A=1, B=2, C=3, D=2)
	hand_size = 2
	hands = cons3.generate_hands(variable_list, deck, hand_size)
	vh1 = []
	vh2 = []
	for hand in hands:
		if valid1(hand):
			vh1.append(hand)
		if valid2(hand):
			vh2.append(hand)
	print valid1
	for hand in vh1:
		print '    {0}'.format(hand)
	print valid2
	for hand in vh2:
		print '    {0}'.format(hand)
