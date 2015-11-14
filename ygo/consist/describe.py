"""
Declares an Abstract Syntax Tree that represents an expression.
The AST can be built up using python operators, and in the future,
maybe a simple Domain Specific Language.

ASTs can determine disjoint sets of variables from their terms,
evaluate if they are true for a given hand, and determine
their probability of being true.

When building an expression using operators, remember that the
left hand term is responsible for what happens. Therefore, 
even though there is support for using base integers in expressions,
they can't be on the left side of an expression, or else python will
try to use int.__operator__ instead of AST.__operator__.

If you use Cardset without comparing it to a number, Instead of
throwing an error, it will simply evaluate to true as long
as there is at least one of that card. Whether that is reliable or
wanted has yet to be decided.

"""
import operator
import itertools
from . import handgen
from .interface import all_cards, count_all, size
from ..core.deck import YugiohSet

class SyntaxError(RuntimeError):
	'''this error is thrown if the user creates an invalid expression'''
	def __init__(self):
		RuntimeError.__init__(self, 'SyntaxError'.format(s))
		
class AST(object):
	'''The base class for all the expression building blocks. Handles creating nested AST.'''
	
	def __call__(self, hand):
		#this should return True if the hand matches this expression. AST is abstract, so it simply fails
		raise NotImplementedError(type(self))
		
	def variables(self):
		# Generate a disjoint set of cards that are used in this expression"""
		raise NotImplementedError()
		
	# uses operators as expression builders.
	# these return higher order ASTs
	# this particular set compares variables to ints
	def __eq__(self, other):
		"""The number of occurences of the left-hand expression is equal to other.
		
		:param other: the right-hand expression
		:type other: int"""
		if isinstance(other, int):
			return Equal([self, Number(other)])
		else:
			return Equal([self, other])			
	def __lt__(self, other):
		"""The number of occurences of the left-hand expression is less than to the number of occurences of the right-hand expression.
		
		:param other: the right-hand expression
		:type other: int"""
		if isinstance(other, int):
			return LessThan([self, Number(other)])
		else:
			return LessThan([self, other])		
	def __gt__(self, other):
		"""The number of occurences of the left-hand expression is greater than the number of occurences of the right-hand expression.
		
		:param other: the right-hand expression
		:type other: int"""
		if isinstance(other, int):
			return GreaterThan([self, Number(other)])
		else:
			return GreaterThan([self, other])	
	def __and__(self, other):
		"""Both the left and right expressions are true.
		
		:param other: the right-hand expression
		:type other: consist.describe.AST
		:raises: SyntaxError"""
		if isinstance(other, int):
			raise SyntaxError()
		elif isinstance(other, And):
			return other & self
		else:
			return And([self, other])		
	def __or__(self, other):
		"""Either the left or right expressions are true..
		
		:param other: the right-hand expression
		:type other: consist.describe.AST
		:raises: SyntaxError"""
		if isinstance(other, int):
			raise SyntaxError()
		elif isinstance(other, Or):
			return other | self
		else:
			return Or([self, other])
			
	def __add__(self, other):
		"""Return the sum of the number of occurences of the left hand expression and the right hand expression..
		
		:param other: the right-hand expression
		:type other: consist.describe.AST"""
		if isinstance(other, int):
			return Add([self, Number(other)])
		elif isinstance(other, Add):
			return other + self
		else:
			return Add([self, other])
			
	def probability(self, deck, hand_size=5):
		"""Returns the probability of drawing a hand for which this expression is true, for a given deck. This ties all the pieces together from handgen and describe.
		
		:param deck: the deck you are checking consistency of
		:type deck: yugioh.core.deck.YugiohDeck
		:param hand_size: the number of cards in your opening hand
		:type hand_size: int"""
		variables = self.variables()
		hands = handgen.generate_hands(variables, deck, hand_size)
		successes = 0
		for hand in hands:
			if self(hand):
				successes += hand.combinations(deck, hand_size)
		return float(successes) / handgen.choose(handgen.size(deck), hand_size)

class Cardset(AST, YugiohSet):
	'''a set of YugiohCards. The fundamental variable of expressions. By combining instances of this card using math expressions, you can create complex expressions to represent good hands.'''
	def __init__(self, cards_iterable):
		if cards_iterable == None:
			raise TypeError("Cardset does not accept NoneType")
		else:
			YugiohSet.__init__(self, cards_iterable)
	def __str__(self):
		return '{' + ','.join(str(x) for x in self) + '}'
	def __call__(self, hand):
		#a lone cardset cannot pass or fail a hand,
		#so it simply returns the number of cards matching itself in the hand.'''
		total = 0
		for term in hand:
			if frozenset(self) <= term.cardset:
				total += term.count
		return total
		
	def variables(self):
		yield frozenset(self)
	
class Number(AST):
	'''An integer that can be compared with cardsets'''
	def __init__(self, n):
		self.value = n
	def __str__(self):
		return str(self.value)
	def __call__(self, hand):
		return self.value
	def variables(self):
		return frozenset()
			
class Constraint(AST):
	'''second level AST for compound expression objects (i.e. Add, And, etc.)'''
	def __init__(self, terms):
		self.__terms = terms
		
	def __iter__(self):
		return iter(self.__terms)		
			
	def variables(self):
		''' return a list of disjoint cardsets collected from the cardsets used in this expression'''
		results = []
		# this just gets all the variables from its components
		# and chains them together into a single iterable.
		# it then trys to add each new variable to the list of variables
		# at each step, results is guaranteed to be disjoint
		for new_term in itertools.chain(*(x.variables() for x in self)):
			swap = []
			for curr_var in results:
				if len(new_term) == 0:
					# if the new variable is the empty set,
					# then there is no way it can intersect anything
					swap.append( curr_var )
					
				elif new_term == curr_var:
					# if they're the same, then we only add one,
					# and zero out the term we're adding.
					new_term = frozenset()
					swap.append( curr_var )
					
				# if we encounter a collision, we split out the parts
				# that collide, and remove the collision from new_term
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
					# if the two are disjoint, then there is no problem
					swap.append( curr_var )
			# if there's anything new left that didn't collide,
			# add it to the list of variables.
			if len(new_term) > 0:
				swap.append( new_term )
			results = swap
		return results
				
class And(Constraint):
	'''represents an And(&) expression in the ast.'''
	def __str__(self):
		return '({0})'.format(' & '.join(map(str, self)))
	def __call__(self, hand):
		return all(term(hand) for term in self)

class Or(Constraint):
	'''represents a Or(|) expression in the ast.'''
	def __str__(self):
		return '({0})'.format(' | '.join(map(str, self)))
	def __call__(self, hand):
		return any(term(hand) for term in self)
		
class Add(Constraint):
	'''represents an Add(+) expression in the ast.'''
	def __str__(self):
		return '({0})'.format(' + '.join(map(str, self)))
	def __call__(self, hand):
		return sum(term(hand) for term in self)
		
class GreaterThan(Constraint):
	'''represents a GreaterThan(>) expression in the ast.'''
	def __str__(self):
		return '({0})'.format(' > '.join(map(str, self)))
	def __call__(self, hand):
		# we aren't sure that this has only two operands,
		# so we just check that each term is less than the last
		# i.e. a > b > c
		last = None
		for term in self:
			if last == None or last > term(hand):
				last = term(hand)
			else:
				return False
		return True

class LessThan(Constraint):
	'''represents a LessThan(<) expression in the ast.'''
	def __str__(self):
		return '({0})'.format(' < '.join(map(str, self)))
	def __call__(self, hand):
		# we aren't sure that this has only two operands,
		# so we just check that each term is greater than the last
		# i.e. a < b < c
		last = None
		for term in self:
			if last == None or last < term(hand):
				last = term(hand)
			else:
				return False
		return True
		
class Equal(Constraint):
	'''represents an Equal(==) expression in the ast.'''
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

	
