"""
This module supports reading and writing to text deck lists. The first line is the deck title. An author can by set by a line beginning with "by", and then the author's name. Card names are entered one per line, and either followed or preceded by the number of copies. Any line beginning with Main, Extra, or Side begins the appropriate section. Line comments can be added by starting a line with # or //

Example: ::

	Yugi's Deck
	by Yugi Moto
	Main Deck
		Alpha, The Magnet Warrior x1
		Gamma, The Magnet Warrior x1
		// this one has the most attack
		Beta, The Magnet Warrior x1
	Extra Deck
		Number 39: Utopia x1
	Side Deck
		# mst negates
		Mystical Space Typhoon x3


"""
from .core.deck import YugiohDeck
import re

def load(text, card_source):
	"""Reads the file and returns a new deck representing the contents.

	:param flname: the absolute path to the deck
	:type flname: string
	:returns: the deck
	:rtype: core.deck.YugiohDeck"""
	lines = text.splitlines()
	
	leading_number = re.compile('^\w*(1|2|3) +(.*)$')
	trailing_number = re.compile('^(.*) +\w*(1|2|3)$')
	extract_author = re.compile('^by +(.*)')
	
	main = []
	side = []
	extra = []
	current = main
	author = ''
	title = ''
	
	for line in lines:
		line = line.strip()
		if line.strip().startswith('#') or line.strip().startswith('//'):
			continue
		elif extract_author.match(line.strip().lower()):
			result = extract_author.match(line.strip().lower())
			author = result.group(1)
		
		elif line.strip().lower().startswith('main'):
			current = main
		elif line.strip().lower().startswith('extra'):
			current = extra
		elif line.strip().lower().startswith('side'):
			current = side
		else:
			lead = leading_number.match(line.strip())
			trail = trailing_number.match(line.strip())
			if not lead and not trail:
				continue
			elif lead:
				count = lead.group(1)
				name = lead.group(2)
			elif trail:
				count = trail.group(2)
				name = trail.group(1)
				
			card = card_source.find(name)		
			for i in count:
				current.append(card)
				
	return YugiohDeck(title, author, main, side, extra)

def dump(deck):
	"""
	:returns: the deck as an easy-to-read raw text format.
	:rtype: string"""
	output = []
	output.append(deck.name)
	output.append(deck.author)
	output.append('Main Deck')
	output.append('  Monsters ({})'.format(len(deck.main.monsters())))
	for monster in deck.main.monsters():
		output.append("    {0} x{1}".format(monster.name, deck.main.count(monster)))

	output.append('  Spells ({})'.format(len(deck.main.spells())))
	for spell in deck.main.spells():
		output.append("    {0} x{1}".format(spell.name, deck.main.count(spell)))

	output.append('  Traps ({})'.format(len(deck.main.traps())))
	for trap in deck.main.traps():
		output.append("    {0} x{1}".format(trap.name, deck.main.count(trap)))
	
	output.append("Extra Deck ({0})".format(len(deck.extra)))
	for monster in deck.extra:
		output.append("    {0} x{1}".format(monster.name, deck.extra.count(monster)))
		
	output.append("Side Deck ({0})".format(len(deck.side)))
	for card in deck.side:
		output.append("    {0} x{1}".format(card.name, deck.side.count(card)))
	return '\n'.join(output)
