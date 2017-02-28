PYPARSING_EXISTS = True
try:
	import pyparsing
	from pyparsing import Word, Literal, CaselessKeyword, MatchFirst, Group, Optional
except ImportError:
	PYPARSING_EXISTS = False
import re

CARD_KEYS = [ 'name', 'text', 'category',
		'level', 'left_scale', 'right_scale', 'scale',
		'attack', 'defense', 'type', 'attribute' ]

CARD_PROPERTIES = [ 'monster', 'spell', 'trap',
		'normal', 'effect', 'fusion',
		'xyz', 'synchro', 'ritual',
		'union', 'spirit', 'gemini',
		'toon', 'tuner', 'flip',
		'pendulum', 'continuous', 'equip',
		'quick-play', 'counter', 'field']

SYNTAX = None

def _syntax():
	global SYNTAX

	if SYNTAX != None:
		return SYNTAX

	number = Word("0123456789")

	string = pyparsing.dblQuotedString

	symbol = Word(pyparsing.alphas + '-')
	@symbol.setParseAction
	def add_quotations(s, loc, result):
		return string.parseString('"{}"'.format(result[0]))

	text = string | symbol

	bool_variable = MatchFirst(CaselessKeyword(attr) for attr in CARD_PROPERTIES)
	bool_variable = bool_variable | CaselessKeyword('true') | CaselessKeyword('false')

	value_variable = MatchFirst(CaselessKeyword(attr) for attr in CARD_KEYS)

	variable = bool_variable | value_variable

	comparator_op = MatchFirst(Literal(x) for x in ['=', '<', '>', '~'])

	logical_op = MatchFirst(CaselessKeyword(x) for x in ['and', 'or'])
	not_op = CaselessKeyword('not')

	atom = MatchFirst([value_variable, bool_variable, text, number])

	expr = pyparsing.Forward()
	
	atom_compare = (atom.setResultsName('LHand') +
		comparator_op.setResultsName('Comparator') +
		atom.setResultsName('RHand'))

	atom_equal = (value_variable + atom)
	@atom_equal.setParseAction
	def add_implicit_equals(string, loc, result):
		return atom_compare.parseString('{} ~ {}'.format(result[0], result[1]))

	atom_true = bool_variable.copy()
	@atom_true.setParseAction
	def add_implicit_operands(string, loc, result):
		return atom_compare.parseString('{} = true'.format(result[0]))

	atom_not = (not_op + atom)
	@atom_not.setParseAction
	def invert_atom(string, loc, result):
		return atom_compare.parseString('{} = false'.format(result[1]))


	compare =  Group(atom_compare | atom_equal | atom_true | atom_not).setResultsName('Constraint')

	expr << Group(compare + Optional(logical_op.setResultsName('Operator') + expr)).setResultsName('Expression')
	SYNTAX = expr
	return expr

class YQuery(object):
	def __call__(self, card):
		raise NotImplementedError()
	def filter(self, cardset):
		for card in cardset:
			if self(card):
				yield card

class Atom(YQuery):
	def __init__(self, v):
		self.value = v

class Integer(Atom):
	def __str__(self):
		return '{}'.format(self.value)
	def __call__(self, card):
		return self.value

class String(Atom):
	def __str__(self):
		return '"{}"'.format(self.value)
	def __call__(self, card):
		return self.value

class KeyVariable(Atom):
	def __str__(self):
		return '(var {})'.format(self.value)
	def __call__(self, card):
		result  = card[self.value]
		return card[self.value]

class CategoryVariable(Atom):
	def __str__(self):
		return '(is? {})'.format(self.value)
	def __call__(self, card):
		return self.value.capitalize() in card['category']

class Binary(YQuery):
	def __init__(self, a, b):
		self.a = a
		self.b = b

class GreaterThan(Binary):
	def __str__(self):
		return '(> {} {})'.format(self.a, self.b)
	def __call__(self, card):
		return self.a(card) > self.b(card)

class LessThan(Binary):
	def __str__(self):
		return '(< {} {})'.format(self.a, self.b)
	def __call__(self, card):
		return self.a(card) < self.b(card)

class Equal(Binary):
	def __str__(self):
		return '(equal {} {})'.format(self.a, self.b)
	def __call__(self, card):
		return self.a(card) == self.b(card)

class Match(Binary):
	def __str__(self):
		return '(match {} {})'.format(self.a, self.b)
	def __call__(self, card):
		value = self.a(card)
		pattern = self.b(card)
		try:
			result = re.search(pattern, value)
			if result is None:
				return 0
			else:
				return 1
		except TypeError:
			return value == pattern

class And(Binary):
	def __str__(self):
		return '({} and {})'.format(self.a, self.b)
	def __call__(self, card):
		return self.a(card) and self.b(card)

class Or(Binary):
	def __str__(self):
		return '({} and {})'.format(self.a, self.b)
	def __call__(self, card):
		return self.a(card) and self.b(card)
	

def compile_yql(text):
	if not PYPARSING_EXISTS:
		raise ImportError("No module named 'pyparsing'")
	if isinstance(text, YQuery):
		return text
	else:
		parser = _syntax()
		result = parser.parseString(text)
		expr = _compile_expression(result['Expression'])
		return expr

def _compile_expression(result):
	lhand = _compile_constraint(result['Constraint'])
	if 'Operator' in result:
		op = result['Operator']
		rhand = _compile_expression(result['Expression'])
		if op.lower() == 'and':
			lhand = And(lhand, rhand)
		elif op.lower() == 'or':
			lhand = Or(lhand, rhand)
	return lhand

def _compile_constraint(result):
	op = result['Comparator']
	lhand = _compile_atom(result['LHand'])
	rhand = _compile_atom(result['RHand'])
	if op == '=':
		return Equal(lhand, rhand)
	elif op == '<':
		return LessThan(lhand, rhand)
	elif op == '>':
		return GreaterThan(lhand, rhand)
	elif op == '~':
		return Match(lhand, rhand)
	else:
		raise NotImplementedError(op)

def _compile_atom(result):
	if len(result) > 1 and result[0] == '"' and result[-1] == '"':
		return String(result[1:-1])
	elif result.isdigit():
		return Integer(int(result))
	elif result.lower() == 'true':
		return Integer(1)
	elif result.lower() == 'false':
		return Integer(0)
	elif result.lower() in CARD_KEYS:
		return KeyVariable(result.lower())
	else:
		return CategoryVariable(result.lower())

if __name__ == '__main__':
	import deck
	db = deck.YgoproPercyDatabase('/home/andy/Applications/ygopro-percy/cards.cdb')
	expr = compile_yql('type Dragon')
	cards = db.all_cards()
	result = list(filter(cards, expr))
	print(len(result))
	first = result[0]
	print(first['name'])
	print(first['type'])
