import ply.lex as lex
import ply.yacc as yacc

import ygo

tokens = [
	'PROPERTY',
	'NUMBER',
	'STRING',

	'ASSERTION',

	'NOT',
	'OR',
	'AND',

	'COMPARE',

	'OPAREN',
	'CPAREN',
]

def t_NUMBER(t):
	r'[0-9]+'
	t.value = int(t.value)
	return t

def t_STRING(t):
	'/[^/\n]*/|"[^"\n]*"|\'[^\'\n]*\''
	t.value = t.value[1:-1]
	return t

def t_PROPERTY(t):
	r'(?i)name|text|id|cid|type|race|attribute|level|rank|attack|defense|left_scale|right_scale|status|def|atk|lscale|rscale|scale|right-scale|left-scale'
	return t

def t_ASSERTION(t):
	'(?i)monster|spell|trap|tuner|normal|effect|ritual|fusion|spirit|union|gemini|synchro|xyz|quickplay|continuous|equip|field|counter|flip|toon|pendulum|pend|extra|main|ocg|tcg|dark|light|earth|wind|water|fire|divine|warrior|spellcaster|fairy|fiend|zombie|machine|aqua|pyro|rock|winged-beast|plant|insect|thunder|dragon|beast|beast-warrior|dinosaur|fish|sea-serpent|reptile|psychic|divine-beast|creator-god|wyrm|banned|forbidden|limited|semilimited|semi|semi-limited|unlimited'
	return t

def t_COMPARE(t):
	r'<|<=|>=|>'
	return t

t_NOT = r'(?i)not|~'
t_OR = r'(?i)or'
t_AND = r'(?i)and'
t_OPAREN = r'\('
t_CPAREN = r'\)'


t_ignore = ' \t\n'

def t_error(t):
    raise TypeError("Unknown text '%s'" % (t.value,))

lexer = lex.lex()

# disjunction
def p_disjunction_0(p):
	'disjunction : disjunction OR conjunction'
	a = p[1]
	b = p[3]
	p[0] = lambda card: a(card) or b(card)

def p_disjunction_1(p):
	'disjunction : conjunction'
	p[0] = p[1]

# conjunction
def p_conjunction_0(p):
	'conjunction : conjunction term'
	a = p[1]
	b = p[2]
	p[0] = lambda card: a(card) and b(card)

def p_conjunction_1(p):
	'conjunction : conjunction AND term'
	a = p[1]
	b = p[3]
	p[0] = lambda card: a(card) and b(card)

def p_conjunction_2(p):
	'conjunction : term'
	p[0] = p[1]

# term
def p_term_0(p):
	'term : ASSERTION'
	a = p[1]
	al = a.lower()
	if al in 'dark|light|earth|wind|water|fire|divine'.split('|'):
		p[0] = lambda card: card.attribute == a.upper()
	elif al in 'warrior|spellcaster|fairy|fiend|zombie|machine|aqua|pyro|rock|winged-beast|plant|insect|thunder|dragon|beast|beast-warrior|dinosaur|fish|sea-serpent|reptile|psychic|divine-beast|creator-god|wyrm'.split('|'):
		p[0] = lambda card: card.type.lower() == al
	elif al == 'monster':
		p[0] = lambda card: card.is_monster()
	elif al == 'spell':
		p[0] = lambda card: card.is_spell()
	elif al == 'trap':
		p[0] = lambda card: card.is_trap()
	elif al == 'tuner':
		p[0] = lambda card: card.is_tuner()
	elif al == 'normal':
		p[0] = lambda card: card.is_normal_monster()
	elif al == 'effect':
		p[0] = lambda card: card.is_effect_monster()
	elif al == 'ritual':
		p[0] = lambda card: card.is_ritual()
	elif al == 'fusion':
		p[0] = lambda card: card.is_fusion()
	elif al == 'spirit':
		p[0] = lambda card: card.is_spirit()
	elif al == 'union':
		p[0] = lambda card: card.is_union()
	elif al == 'gemini':
		p[0] = lambda card: card.is_gemini()
	elif al == 'synchro':
		p[0] = lambda card: card.is_synchro()
	elif al == 'xyz':
		p[0] = lambda card: card.is_xyz()
	elif al == 'quickplay':
		p[0] = lambda card: card.is_quickplay()
	elif al == 'continuous':
		p[0] = lambda card: card.is_continuous()
	elif al == 'equip':
		p[0] = lambda card: card.is_equip()
	elif al == 'field':
		p[0] = lambda card: card.is_field()
	elif al == 'counter':
		p[0] = lambda card: card.is_counter()
	elif al == 'flip':
		p[0] = lambda card: card.is_flip()
	elif al == 'toon':
		p[0] = lambda card: card.is_continuous()
	elif al == 'pendulum':
		p[0] = lambda card: card.is_continuous()
	elif al == 'extra':
		p[0] = lambda card: card.in_extra_deck()
	elif al == 'main':
		p[0] = lambda card: card.in_main_deck()
	elif al == 'ocg':
		p[0] = lambda card: card.allowed('OCG') > 0
	elif al == 'tcg':
		p[0] = lambda card: card.allowed('TCG') > 0
	elif al in ('banned', 'forbidden'):
		p[0] = lambda card: card.allowed() == 0
	elif al == 'limited':
		p[0] = lambda card: card.allowed() == 1
	elif al in ('semi', 'semilimited', 'semi-limited'):
		p[0] = lambda card: card.allowed() == 2
	elif al == 'unlimited':
		p[0] = lambda card: card.allowed() == 3
	
def p_term_1(p):
	'term : lhand COMPARE rhand'
	lh = p[1]
	c = p[2]
	rh = p[3]

	if c == '<':
		p[0] = lambda card: lh(card) < rh(card)
	elif c == '<=':
		p[0] = lambda card: lh(card) <= rh(card)
	elif c == '>':
		p[0] = lambda card: lh(card) > rh(card)
	elif c == '>=':
		p[0] = lambda card: lh(card) >= rh(card)
	else:
		raise RuntimeError('Invalid COMPARE token {}'.format(c))

def p_term_2(p):
	'term : lhand rhand'
	lh = p[1]
	rh = p[2]
	def equal(card):
		lr = lh(card)
		rr = rh(card)
		if isinstance(lr, int) and isinstance(rr, int):
			return lr == rr
		elif isinstance(lr, str) and isinstance(rr, str):
			return rr.lower() in lr.lower()
		else:
			return str(lr) == str(rr)
	p[0] = equal


def p_term_3(p):
	'term : NOT term'
	f = p[1]
	p[0] = lambda card: not f(card)

def p_term_4(p):
	'term : OPAREN disjunction CPAREN'
	p[0] = p[2]

def p_term_5(p):
	'term : STRING'
	s = p[1]
	p[0] = lambda card: s.lower() in card.name.lower()

# lhand
def p_lhand_0(p):
	'lhand : PROPERTY'
	prop = p[1]
	p[0] = lambda card: card.get(prop)

def p_lhand_1(p):
	'lhand : NUMBER'
	n = p[1]
	p[0] = lambda card: n


def __do_replace(word, subs):
	for frm, targ in subs.items():
		word = word.replace(frm, targ)
	return word
# rhand
def p_rhand_0(p):
	'rhand : PROPERTY'
	if prop == 'status':
		p[0] = lambda card: card.allowed()
	else:
		prop = __do_replace(p[1], {
			'def' : 'defense',
			'atk' : 'attack',
			'lscale' : 'left_scale',
			'rscale' : 'right_scale',
			'scale' : 'left_scale',
			'left-scale' : 'left_scale',
			'right-scale' : 'right_scale'
		})
		p[0] = lambda card: card.get(prop)

def p_rhand_1(p):
	'rhand : NUMBER'
	n = p[1]
	p[0] = lambda card: n

def p_rhand_2(p):
	'rhand : STRING'
	s = p[1]
	p[0] = lambda card: s

def p_error(t):
    raise RuntimeError("Syntax Error")

parser = yacc.yacc(optimize=1)

# Interface
def create_query(querytext):
	return parser.parse(querytext)

def select(querytext, cards=None):
	cards = cards or ygo.search.all_cards()
	f = create_query(querytext)
	for card in cards:
		if f(card):
			yield card

def match(querytext, card):
	return create_query(querytext)(card)

def select_cardset(querytext, cards=None):
	cards = select(querytext, cards)
	return ygo.consist.Cardset(cards)
