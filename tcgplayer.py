import urllib2
from bs4 import BeautifulSoup as bsoup
import ygocard
import devpro
import re
		
PRINTABLE_URL_TEMPLATE="http://yugioh.tcgplayer.com/db/deck_print.asp?deck_id="
STANDARD_URL_TEMPLATE="http://yugioh.tcgplayer.com/db/deck.asp?deck_id="
def tcg_open(print_url):
	# supports opening two kinds of url, as well as raw deck id.
	if isinstance(arg, int):
		url = PRINTABLE_URL_TEMPLATE+str(arg)
	elif arg.startswith(STANDARD_URL_TEMPLATE):
		match = re.search('\?deck_id=([0-9]+)', arg)
		if match == None:
			raise RuntimeError('URL does not point to a yugioh.TCGPlayer.com decklist')
		else:
			url = PRINTABLE_URL_TEMPLATE + match.group(1)
	elif arg.startswith(PRINTABLE_URL_TEMPLATE):
		url = arg

	# grab the html to scrape
	conn = urllib2.urlopen(url)
	html = conn.read()
	conn.close()
	
	dom = bsoup(html, 'lxml')
	
	heading = dom.div.b
	assert(heading != None)
	
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
	# uses devpro backend.
	db = devpro.database()

	main = []
	# loop through main deck cards, extract the card count n
	# query devpro for the card instance, and add that instance n times.
	for line in mdeck:
		count = int(line[0])
		text = line[2:]
		cards = list(db.cards_by_pattern(text))
		if len(cards) > 0:
			card = cards[0]
			for i in range(count):
				main.append(card)
		else:
			raise RuntimeError('Could not find card with name "{0}"'.format(text))

	side = []
	for line in sdeck:
		count = int(line[0])
		text = line[2:]
		cards = list(db.cards_by_pattern(text))
		if len(cards) > 0:
			card = cards[0]
			for i in range(count):
				side.append(card)
		else:
			raise RuntimeError('Could not find card with name "{0}"'.format(text))

	extra = []
	for line in edeck:
		count = int(line[0])
		text = line[2:]
		cards = list(db.cards_by_pattern(text))
		if len(cards) > 0:
			card = cards[0]
			for i in range(count):
				extra.append(card)
		else:
			raise RuntimeError('Could not find card with name "{0}"'.format(text))
	return ygocard.YugiohDeck(name, author, main, side, extra)

def tcg_save(deck, fl):
	# this is just here for symmetry
	raise NotImplementedError('TCGPlayer does not support uploading decks.')
