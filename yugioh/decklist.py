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
from .core import database, deck
import re

def load_deck(flname, db_path=None):
	"""Reads the file and returns a new deck representing the contents.

	:param flname: the absolute path to the deck
	:type flname: string
	:returns: the deck
	:rtype: core.deck.YugiohDeck"""
	lines = None
	with open(flname) as fl:
		lines = fl.readlines()
	if lines == None or len(lines) == 0:
		return None
	return _parse_deck(lines, db_path)
	db = database.database(db_path)
	blank_deck = deck.YugiohDeck(lines[0].strip(), '', [], [], [])
	current = blank_deck.main
	
	leading_number = re.compile('^\w*(1|2|3) +(.*)$')
	trailing_number = re.compile('^(.*) +\w*(1|2|3)$')
	exactly_one  = re.compile('^(.*)$')
	extract_author = re.compile('^by +(.*)')
	
	for line in lines:
		line = line.strip()
		if line.strip().startswith('#') or line.strip().startswith('//'):
			continue
		elif extract_author.match(line.strip().lower()):
			result = extract_author.match(line.strip().lower())
			blank_deck.author = result.group(1)
		
		elif line.strip().lower().startswith('main'):
			current = blank_deck.main
		elif line.strip().lower().startswith('extra'):
			current = blank_deck.extra
		elif line.strip().lower().startswith('side'):
			current = blank_deck.side
		else:
			lead = leading_number.match(line.strip())
			trail = trailing_number.match(line.strip())
			no_x = exactly_one.match(line.strip())
			if not lead and not trail and not no_x:
				continue
			elif lead:
				count = lead.group(1)
				name = lead.group(2)
			elif trail:
				count = trail.group(2)
				name = trail.group(1)
			elif no_x:
				count = 1
				name = no_x.group(1)
			card = db.find(name, by='name')
			if card:
				current.add_card(card, int(count))
			else:
				raise database.CardNotFoundError('Unknown card {0}'.format(name))
	return blank_deck
	
def save_deck(deck, fl):
	"""Write the given deck to file as a text decklist.
	
:param deck: the deck
:type deck: core.deck.YugiohDeck
:param fl: the output file
:type fl: file
:returns: None"""
	fl.write(deck.as_decklist())
