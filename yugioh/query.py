from . import search
from .core import enum
	
class QuerySyntaxError(RuntimeError):
	pass
	
def compare_arg(var, txt):
	if txt.isdigit():
		return var == int(txt)
	elif txt[-1] in '+-':
		val = int(txt[:-1])
		if txt[-1] == '+':
			return var >= val
		else:
			return var <= val
	else:
		raise QuerySyntaxError('Invalid query argument {}'.format(txt))
		
def compare_format(card, expected):
	try:
		return card.availability.lower() == expected.lower()
	except AttributeError:
		return expected.lower() in ('tcg', 'any')
	
keywords = [
	'name', 'named', 'text', 'description',
	'level', 'rank', 'attack', 'defense',
	'scale', 'rightscale', 'leftscale',
	'monster', 'spell', 'trap',
	'synchro', 'xyz', 'pendulum', 'ritual', 'fusion',
	'tuner', 'flip', 'union', 'spirit', 'gemini', 'toon',
	'equip', 'field', 'counter', 'continuous', 'normal',
	'limited', 'forbidden', 'semilimited', 'unlimited',
	'ocg', 'tcg', 'any', 'anime'
]
keywords.extend(x.lower() for x in enum.attributes.keys())
keywords.extend(x.lower() for x in enum.types.keys())

def parse_filter(stream):
	if len(stream) > 0:
		cmdr = stream.pop()
		cmd = cmdr.lower()
		if cmd == 'not':
			expr = parse_filter(stream)
			return lambda card: not expr(card)
		elif cmd.startswith('name'):
			arg = stream.pop()
			return lambda card: arg in card.name
		elif cmd in ['text', 'description']:
			arg = stream.pop()
			return lambda card: arg in card.text			
		elif cmd == 'level':
			arg = stream.pop()
			return lambda card: compare_arg(card.level, arg)
		elif cmd == 'rank':
			arg = stream.pop()
			return lambda card: compare_arg(card.level, arg)
		elif cmd == 'attack':
			arg = stream.pop()
			return lambda card: compare_arg(card.attack, arg)
		elif cmd == 'defense':
			arg = stream.pop()
			return lambda card: compare_arg(card.defense, arg)
		elif cmd == 'scale':
			arg = stream.pop()
			return lambda card: compare_arg(card.right_scale, arg)
		elif cmd.replace('-','') == 'rightscale':
			arg = stream.pop()
			return lambda card: compare_arg(card.right_scale, arg)
		elif cmd.replace('-','') == 'leftscale':
			arg = stream.pop()
			return lambda card: compare_arg(card.right_scale, arg)
		elif cmd.upper() in enum.attributes.keys():
			return lambda card: card.attribute == cmd.lower()
		elif any(cmd.replace('-','') == t.lower().replace('-','')  for t in enum.types.keys()):
			return lambda card: card.type.lower().replace('-','') == cmd.lower().replace('-','')
			
		elif cmd == 'monster':
			return lambda card: card.is_monster()		
		elif cmd == 'synchro':
			return lambda card: card.is_synchro()
		elif cmd == 'xyz':
			return lambda card: card.is_xyz()
		elif cmd == 'fusion':
			return lambda card: card.is_fusion()
		elif cmd == 'ritual':
			return lambda card: 'Ritual' in card.category
		elif cmd == 'pendulum':		
			return lambda card: card.is_pendulum()
		elif cmd == 'tuner':
			return lambda card: card.is_tuner()
		elif cmd == 'spirit':
			return lambda card: 'Spirit' in card.category
		elif cmd == 'union':
			return lambda card: 'Union' in card.category
		elif cmd == 'flip':
			return lambda card: 'Flip' in card.category
		elif cmd == 'gemini':
			return lambda card: 'Gemini' in card.category
		elif cmd == 'toon':
			return lambda card: 'Toon' in card.category
			
			
		elif cmd == 'spell':
			return lambda card: card.is_spell()
		elif cmd == 'equip':
			return lambda card: 'Equip' in card.category
		elif cmd == 'field':
			return lambda card: 'Field' in card.category
		elif cmd.replace('-','') == 'quickplay':
			return lambda card: 'Quick-Play' in card.category
			
			
		elif cmd == 'trap':
			return lambda card: card.is_trap()
		elif cmd == 'counter':
			return lambda card: 'Counter' in card.category		
		elif cmd == 'normal':
			return lambda card: 'Normal' in card.category or (card.is_monster() and 'Effect' not in card.category)
		elif cmd == 'continuous':
			return lambda card: 'Continuous' in card.category
		elif cmd == 'forbidden':
			return lambda card: card.allowed() == 0	
		elif cmd == 'limited':
			return lambda card: card.allowed() == 1
		elif cmd.replace('-','') == 'semilimited':
			return lambda card: card.allowed() == 2
		elif cmd == 'unlimited':
			return lambda card: card.allowed() >= 3
		elif cmd in ('tcg', 'ocg', 'anime', 'any'):
			return lambda card: compare_format(card, cmd)
		elif cmd.isdigit():
			return lambda card: card.cid == cmd
		else:
			return lambda card: cmdr in card.name

def apply_filter(preds):
	def execute(cards):
		for pred in preds:
			cards = [card for card in cards if pred(card)]
		return cards
	return execute
	
def create_filter(tokens):
	tokens = list(reversed(tokens))
	fs = []
	while len(tokens) > 0:
		expr = parse_filter(tokens)
		if expr == None:
			raise RuntimeError('fuck')
		fs.append(expr)
	return apply_filter(fs)
		
def filter(cards, *tokens):
	func = create_filter(tokens)
	return func(cards)
