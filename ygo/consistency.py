import itertools
from . import deck
from . import yql

"""
Still under development. If you want to dig into the source, be my guest.
"""

VERBOSE = 0

def choose(n, k):
	# classic combinatorics function.
	# see https://en.wikipedia.org/wiki/Combination

	# Use this over itertools.combinations
	# we just want the number of combinations
	# itertools would actually generate the combinations
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

def available_copies(var, deck):
	total = 0
	for card in var:
		total += deck.count(card)
	return total

def union_all(ls):
	total = set()
	for st in ls:
		total.update(st)
	return total
	
def make_term(v, c):
	return (frozenset(v), c)

class Hand(object):
	def __init__(self, terms=None):
		self.terms = list(terms) or []
	def with_term(self, term):
		new_terms = self.terms + [term]
		return Hand(new_terms)
	def size(self):
		return sum(x[1] for x in self.terms) if len(self.terms) > 0 else 0
	def count(self, cset):
		total = 0
		for (var, count) in self.terms:
			if var.issubset(cset):
				total += count
		return total
	def __str__(self):
		terms = []
		for (v, c) in self.terms:
			if len(v) > 3:
				vtext = '{' + ', '.join(str(x) for x in list(v)[:3]+['...']) + '}'
			else:
				vtext = '{' + ', '.join(str(x) for x in v) + '}'
			ctext = str(c)
			text = vtext+'='+ctext
			terms.append(text)
		return 'Hand[' + '; '.join(terms) + ']'

	def combinations(self, deck):
		hand_size = self.size()
		total = 1.0
		for (var, varcount) in self.terms:
			copies = available_copies(var, deck)
			var_combinations = choose(copies, varcount)
			total *= var_combinations
		return total

def generate_hands(variables, deck, max_hand_size=5):
	# all variables must be disjoint sets of cards
	variable_iter = iter(variables)
	all_hands = []

	var = next(variable_iter)
	max_copies = min(available_copies(var, deck), max_hand_size)
	for varcount in range(1, max_copies+1):
		term = (frozenset(var), varcount)
		hand = Hand([term])
		all_hands.append(hand)

	for var in variable_iter:
		hand_buffer = []
		for existing_hand in all_hands:
			remaining_hand_capacity = max_hand_size - existing_hand.size()
			var_copies = available_copies(var, deck)
			max_copies = min(var_copies, remaining_hand_capacity)
			for varcount in range(1, max_copies+1):
				new_term = (frozenset(var), varcount)
				new_hand = existing_hand.with_term(new_term)
				hand_buffer.append(new_hand)
		all_hands = hand_buffer

	# fill out the incomplete hands
	hand_buffer = []
	all_variables = union_all(variables)
	restvar = set(deck).difference(all_variables)
	rest_copies = available_copies(restvar, deck)
	for existing_hand in all_hands:
		remaining_capacity = max_hand_size - existing_hand.size()
		if remaining_capacity > rest_copies:
			continue
		elif remaining_capacity == 0:
			hand_buffer.append(existing_hand)
		else:
			new_term = (frozenset(restvar), remaining_capacity)
			new_hand = existing_hand.with_term(new_term)
			hand_buffer.append(new_hand)

	return hand_buffer

def conjunction(exprs):
	a = exprs.pop()
	b = exprs.pop()
	assert(isinstance(a, AST))
	assert(isinstance(b, AST))
	current = a & b
	for x in exprs:
		assert(isinstance(x, AST))
		current &= x
	return current

def disjunction(exprs):
	a = exprs.pop()
	b = exprs.pop()
	assert(isinstance(a, AST))
	assert(isinstance(b, AST))
	current = a | b
	for x in exprs:
		assert(isinstance(x, AST))
		current |= (current, x)
	return current
	

"""
Goal: Modify __call__ so that it can evaluate on Cards, not Hands.
Two seperate AST?

"""
class AST(object):
	def __str__(self):
		raise RuntimeError('No string conversion available for consistency.AST')
	def __or__(self, other):
		assert(isinstance(self, AST))
		assert(isinstance(other, AST))
		return Or(self, other).simplify()

	def __and__(self, other):
		assert(isinstance(self, AST))
		assert(isinstance(other, AST))
		return And(self, other).simplify()

	def __gt__(self, other):
		assert(isinstance(self, AST))
		assert(isinstance(other, AST))
		return GreaterThan(self, other).simplify()

	def __lt__(self, other):
		assert(isinstance(self, AST))
		assert(isinstance(other, AST))
		return LessThan(self, other).simplify()

	def __eq__(self, other):
		assert(isinstance(self, AST))
		assert(isinstance(other, AST))
		return Equal(self, other).simplify()

	def __invert__(self):
		assert(isinstance(self, AST))
		return Not(self).simplify()

	def __neq__(self, other):
		return self == (~other)

	def pre_evaluate(self):
		return None

	def simplify(self):
		pe = self.pre_evaluate()
		if pe is None:
			return self
		else:
			return Number(pe)

	def __call__(self, hand):
		# returns the number of copies that match the expression
		return 0

class Cardset(AST):
	'''a set of cards. The fundamental variable of expressions.'''
	def __init__(self, cards_iterable):
		cards = [card for card in cards_iterable]
		assert(all(isinstance(x, deck.Card) for x in cards))
		self.contents = frozenset(cards)

	def __len__(self):
		return len(self.contents)

	def __str__(self):
		strfy = [str(x) for x in self.contents]
		if len(strfy) > 2:
			strfy = strfy[:2]
			strfy.append('...')
		return '#[{}]'.format(', '.join(strfy))

	def __repr__(self):
		return 'Cardset[{}]'.format(', '.join(str(x) for x in self.contents))

	def __iter__(self):
		return iter(self.contents)

	def __call__(self, hand):
		#a lone cardset cannot pass or fail a hand,
		#so it simply returns the number of cards matching itself in the hand.'''
		if len(self.contents) == 0:
			return 0
		else:
			return hand.count(self.contents)

	def __xor__(self, other):
		return self.constrain(other)

	def constrain(self, other):
		if isinstance(other, Cardset):
			return Cardset(self.contents.intersection(other.contents))
		elif isinstance(other, yql.YQuery) or isinstance(other, str):
			result = yql.filter(self.contents, other)
			return Cardset(list(result))
		else:
			raise RuntimeError('Cannot constrain cardset {} by filter {}'.format(self, other))
		
	def variables(self, deck):
		yield self.contents

	def pre_evaluate(self):
		if len(self) == 0:
			return 0
		else:
			None
	def simplify(self):
		if len(self) == 0:
			return 0
		else:
			return self

class Constraint(AST):
	'''A logical operation on several card sets.'''
	def __init__(self, a, b):
		assert(isinstance(a, AST))
		assert(isinstance(a, AST))
		self.op1 = a
		self.op2 = b
	def __iter__(self):
		return iter([self.op1, self.op2])
	def variables(self, deck):
		final_variables = []

		op1_vars = list(self.op1.variables(deck))
		op2_vars = list(self.op2.variables(deck))
		initial_variables = op1_vars + op2_vars
		
		# add variables one at a time to a final set of variables
		for new_variable in initial_variables:
			final_variables = self.add_variable(final_variables, new_variable)
		return final_variables

	def add_variable(self, existing_variables, new_variable):
		# empty variable means no change
		if len(new_variable) == 0:
			return existing_variables

		resulting_variables = []
		awaiting_inspection = existing_variables[:]
		while len(awaiting_inspection) > 0:
			existing = awaiting_inspection.pop()

			# new_variable was already entirely included
			if new_variable == existing:
				resulting_variables.extend(awaiting_inspection)
				break
				
			# new variable is included as part of another 
			elif new_variable.issubset(existing):
				remainder = existing.difference(new_variable)
				resulting_variables.append(remainder)
				resulting_variables.extend(awaiting_inspection)
				break

			# new variable is already partly covered by an existing variable
			elif new_variable.issuperset(existing):
				resulting_variables.append(existing)
				new_variable = new_variable.difference(existing)

			# new variable and existing variable can be split into three new variables
			elif len(new_variable.intersection(existing)) > 0:
				intersection = new_variable.intersection(existing)
				resulting_variable.append(intersection)
				resulting_variables.append(existing.difference(intersection))
				new_variable = new_variable.difference(intersection)

			# new and existing variables are entirely disjoint
			else:
				resulting_variables.append(existing)
		resulting_variables.append(new_variable)
		return resulting_variables

class Number(AST):
	def __init__(self, v):
		assert(isinstance(v, int) and v >= 0)
		self._value = v
	def variables(self, deck):
		yield frozenset()
	def __str__(self):
		return str(self._value)
	def __call__(self, hand):
		return self._value
	def pre_evaluate(self):
		return self._value

class HandSize(AST):
	def variables(self, deck):
		yield frozenset()
	def __str__(self):
		return '$H'
	def __call__(self, hand):
		return hand.size()
	def pre_evaluate(self):
		return None

class GreaterThan(Constraint):
	def __str__(self):
		return '({})'.format(' > '.join(str(x) for x in self))
	def __call__(self, hand):
		return self.op1(hand) > self.op2(hand)
	def pre_evaluate(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is None or right is None:
			return None
		else:
			return left > right
	def simplify(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is None or right is None:
			return GreaterThan(self.op1.simplify(), self.op2.simplify())
		else:
			return Number(int(left > right))

class LessThan(Constraint):
	def __str__(self):
		return '({})'.format(' < '.join(str(x) for x in self))
	def __call__(self, hand):
		return self.op1(hand) < self.op2(hand)
	def pre_evaluate(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is None or right is None:
			return None
		else:
			return left < right
	def simplify(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is None or right is None:
			return LessThan(self.op1.simplify(), self.op2.simplify())
		else:
			return Number(int(left < right))

class Equal(Constraint):
	def __str__(self):
		return '({})'.format(' = '.join(str(x) for x in self))
	def __call__(self, hand):
		return self.op1(hand) == self.op2(hand)
	def pre_evaluate(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is None or right is None:
			return None
		else:
			return left < right
	def simplify(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is None or right is None:
			return Equal(self.op1.simplify(), self.op2.simplify())
		else:
			return Number(int(left == right))

class And(Constraint):
	def __str__(self):
		return '({})'.format(' && '.join(str(x) for x in self))
	def __call__(self, hand):
		return self.op1(hand) != 0 and self.op2(hand) != 0
	def pre_evaluate(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is 0 or right is 0:
			return 0
		elif left is not None and left > 0:
			return right
		elif right is not None and right > 0:
			return left
		else:
			return None
	def simplify(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is 0 or right is 0:
			return Number(0)
		elif left is not None and left > 0:
			return self.op2.simplify()
		elif right is not None and right > 0:
			return self.op1.simplify()
		else:
			return And(self.op1.simplify(), self.op2.simplify())

class Or(Constraint):
	def __str__(self):
		return '({})'.format(' || '.join(str(x) for x in self))
	def __call__(self, hand):
		return self.op1(hand) != 0 or self.op2(hand) != 0
	def pre_evaluate(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is None or right is None:
			return None
		elif left > 0 or right > 0:
			return 1
		elif left is 0:
			return right
		elif right is 0:
			return left
		else:
			raise RuntimeError('failed complete matching')
	def simplify(self):
		left = self.op1.pre_evaluate()
		right = self.op2.pre_evaluate()
		if left is None and right is None:
			return Or(self.op1.simplify(), self.op2.simplify())
		elif right is 0:
			return self.op1.simplify()
		elif left is 0:
			return self.op2.simplify()
		else:
			return self.op1.simplify() | self.op2.simplify()
			

class Not(AST):
	def __init__(self, subexpr):
		self._subexpr = subexpr
	def __str__(self):
		return 'not {}'.format(str(self._subexpr))
	def variables(self, deck):
		return self._subexpr.variables(deck)
	def __call__(self, hand):
		return self._subexpr(hand) == 0

	def pre_evaluate(self):
		value = self._subexpr.pre_evaluate()
		if value is 0:
			return 1
		elif value > 0:
			return 0
		else:
			return None

	def simplify(self):
		value = self.pre_evaluate()
		if value is 0:
			return Number(1)
		elif value > 0:
			return Number(0)
		else:
			return Not(self._subexpr.simplify())

def probability(deck, expr, hand_size=5):
	variables = expr.variables(deck)
	successes = 0
	hands = generate_hands(variables, deck, hand_size)
	for hand in hands:
		if expr(hand):
			successes += hand.combinations(deck)

	total_possible_hands = choose(len(deck), hand_size)
	return float(successes) / total_possible_hands
