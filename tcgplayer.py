import urllib2
from bs4 import BeautifulSoup as bsoup
import ygocard
import devpro
import re
		
class TCGDeck(ygocard.YugiohDeck):
	@staticmethod
	def open(print_url):
		conn = urllib2.urlopen(print_url)
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
		
		side_deck = dom.find('b', string='Sideboard:').find_next_sibling('font')
		for line in side_deck.children:
			if line.name == 'b' and line.string == 'Extra Deck:':
				current = extra
			elif line.name != 'br':
				data = str(line.string.strip())
				if data != '':
					current.append(data)
		return TCGDeck.from_scrape(name, author, main, side, extra)
	@staticmethod
	def from_scrape(name, author, mdeck, sdeck, edeck):
		db = devpro.database()
		main = []
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

		return TCGDeck(name, author, main, side, extra)


# api stuff

def tcg_open(arg):
	if isinstance(arg, int):
		url = "http://yugioh.tcgplayer.com/db/deck_print.asp?deck_id="+str(arg)
	elif arg.startswith('http://yugioh.tcgplayer.com/db/deck.asp'):
		match = re.search('\?deck_id=([0-9]+)', arg)
		if match == None:
			raise RuntimeError('URL does not point to a yugioh.TCGPlayer.com decklist')
		else:
			url = "http://yugioh.tcgplayer.com/db/deck_print.asp?deck_id=" + match.group(1)
	elif arg.startswith('http://yugioh.tcgplayer.com/db/deck_print.asp'):
		url = arg
	return TCGDeck.open(url)
