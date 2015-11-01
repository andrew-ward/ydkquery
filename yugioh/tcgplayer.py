"""
This provides an interface for opening decks from tcgplayer.com.
This module does not use the official tcgplayer api, because reasons.
load_deck accepts a deck id or a url from tcgplayer.com

DEPRECATED
"""

import sys, re
from bs4 import BeautifulSoup as bsoup

if sys.version_info.major == 2:
	from urllib2 import urlopen
elif sys.version_info.major == 3:
	from urllib.request import urlopen
else:
	svi = sys.version_info
	raise NotImplementedError('Python version {0}.{1}.{3} not supported'.format(svi.major, svi.minor, svi.micro))
	
import urllib2
from . import core

		
PRINTABLE_URL_TEMPLATE="http://yugioh.tcgplayer.com/db/deck_print.asp?deck_id="
STANDARD_URL_TEMPLATE="http://yugioh.tcgplayer.com/db/deck.asp?deck_id="

def load_deck(arg):
	"""Gets a YugiohDeck of the deck at the given url. Also 
	
:param arg: The url or deck id of the deck. Supports opening two kinds of url, as well as raw deck id.
:type arg: string or int
:returns: the deck
:rtype: core.deck.YugiohDeck
	"""
	if isinstance(arg, int) or arg.isdigit():
		url = PRINTABLE_URL_TEMPLATE+str(arg)
	elif arg.startswith(STANDARD_URL_TEMPLATE):
		match = re.search('\?deck_id=([0-9]+)', arg)
		if match == None:
			raise RuntimeError('URL does not point to a yugioh.TCGPlayer.com decklist')
		else:
			url = PRINTABLE_URL_TEMPLATE + match.group(1)
	elif arg.startswith(PRINTABLE_URL_TEMPLATE):
		url = arg
	else:
		raise RuntimeError('URL {0} does not point to a yugioh.TCGPlayer.com decklist'.format(arg))

	# grab the html to scrape
	conn = urlopen(url)
	html = conn.read()
	conn.close()
	
	dom = bsoup(html, 'lxml')
	
	heading = dom.div.b
	if heading == None:
		return None
	
	name = str(heading.contents[0].strip())
	author = str(heading.contents[2].strip())

	main = []
	main_deck = dom.find('b', string='Main Deck:').find_next_sibling('font')
	for line in main_deck.children:
		if line.name != 'br':
			data = str(line.string.strip())
			if data != '':
				main.append(data)

	side = []
	extra = []
	current = side
	# side and extra are both in a tag together
	side_deck = dom.find('b', string='Sideboard:').find_next_sibling('font')
	for line in side_deck.children:
		if line.name == 'b' and line.string == 'Extra Deck:':
			current = extra
		elif line.name != 'br':
			data = str(line.string.strip())
			if data != '':
				current.append(data)
	return __from_scrape(name, author, main, side, extra)

def __from_scrape(name, author, mdeck, sdeck, edeck):
	# converts raw card names from the scrape to actual YugiohCard instances.
	# uses ygopro backend.
	db = core.database.database()

	main = []
	# loop through main deck cards, extract the card count n
	# query ygopro for the card instance, and add that instance n times.
	for line in mdeck:
		count = int(line[0])
		text = line[2:]
		card = db.find(text, by='name')
		if card != None:
			for i in range(count):
				main.append(card)
		else:
			# this is a kind of nasty hack. A few cards have different
			# names between tcgplayer and ygopro, whether from an
			# out of date database or just random weirdness.
			# this uses the levenshtein algorithm to find the most
			# similar name. Likely to fail, will replace ASAP.
			new_card = core.database.levenshtein_match(text, db.all_cards())
			if new_card != None:
				for i in range(count):
					main.append(new_card)
			else:
				raise RuntimeError('Could not find card with name "{0}"'.format(text))

	side = []
	for line in sdeck:
		count = int(line[0])
		text = line[2:]
		card = db.find(text, by='name')
		if card != None:
			for i in range(count):
				side.append(card)
		else:
			new_card = core.database.levenshtein_match(text, db.all_cards())
			if new_card != None:
				for i in range(count):
					side.append(new_card)
			else:
				raise RuntimeError('Could not find card with name "{0}"'.format(text))

	extra = []
	for line in edeck:
		count = int(line[0])
		text = line[2:]
		card = db.find(text, by='name')
		if card != None:
			for i in range(count):
				extra.append(card)
		else:
			new_card = core.database.levenshtein_match(text, db.all_cards())
			if new_card != None:
				for i in range(count):
					extra.append(new_card)
			else:
				raise RuntimeError('Could not find card with name "{0}"'.format(text))
	return core.deck.YugiohDeck(name, author, main, side, extra)

