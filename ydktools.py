#!/usr/bin/python

"""
YdkTools
A command line application that finds and displays yugioh cards and related information.
The general workflow works like this:

First, select one or more cards. a filename will open that decklist and read in the cards, --stdin will do the same from stdin, --name will get a single card by name, and --query will select all cards that match a yql query.

Then, determine what you want to do with the cards. You can display the price of the deck with --price, display the various printings and rarities of each card using --rarity, or write the cards out to a decklist using --output.

Some basic usages:

# print out a deck as text (for copy and pasting?)
ydktools AI_Yugi.ydk --output txt

# display the prices and print runs of a specific card
ydktools --name Card --price --rarity

# display the prices of all cards in an archetype
ydktools --query 'name Darklord' --price


Coming Eventually!
  select decks from online sites like yugiohtopdecks or tcgplayer
  display card text and stats
  check if cards are forbidden or limited,
"""


import argparse
import os, sys
import ygo
from ygopro_config import YGOPRO_PATH

def construct_parser():
	parser = argparse.ArgumentParser(description="A command line application that finds and displays yugioh cards and related information.")

	# Get Cards
	parser.add_argument('filename', nargs="?", help='Open a decklist and use those cards')
	parser.add_argument('-n', '--name', help="Find a single card by name")
	parser.add_argument('-q', '--query', action="append", help='Use a yql query to specify cards')
	parser.add_argument('-i', '--stdin', nargs='?', const="ydk", help='read in a decklist from stdin using the given format. Default is ydk.')

	# Card Info
	parser.add_argument('-p', '--price', action='store_true', help='Show price of each card')

	parser.add_argument('-r', '--rarity', action='store_true', help='Show available rarities of all cards')

	# Output Format
	parser.add_argument('-o', '--output', nargs='?', const='ydk', help='Write result to file. Determine format by filename. Alternately, just give the format to write result to stdout.')
	return parser


def get_input(session, args):
	if args.input is not None:
		fmt = args.input
		text = sys.stdin.read()
		return session.load(text, fmt)

	elif args.filename is not None and args.filename == '-':
		text = sys.stdin.read()
		# no fmt means session will auto-detect format based on contents
		return session.load(text)

	elif args.filename is not None:
		flname = args.filename
		# no fmt means session will auto-detect format based on file extension
		return session.open_deck(flname)

	elif args.query is not None:
		cards = session.yql(args.query)
		return ygo.deck.YugiohDeck(main=ygo.deck.YugiohSet(cards))

	elif args.name is not None:
		cards = session.find_name(args.name)
		return ygo.deck.YugiohDeck(main=ygo.deck.YugiohSet([cards]))

	else:
		return ygo.deck.YugiohDeck()

def write_output(session, args, deck):
	if args.output is None:
		return
	elif args.output in ['ydk', 'txt', 'text', 'json']:
		out = session.dump(deck, args.output)
		sys.stdout.write(out)
	elif args.output == '-':
		sys.stdout.write(session.dump(deck, 'ydk'))
	else:
		session.save_deck(deck, args.output)
	
def display_info(session, args, deck):
	if args.price is None and args.rarity is None:
		return

	if len(deck.side) == 0 and len(deck.extra) == 0:
		rarity = args.rarity is not None
		display_set_price(session, deck.main, _cheapest, rarity)
	else:
		rarity = args.rarity is not None
		display_deck_price(session, deck, _cheapest, rarity)

def _default_sort_key(card):
	return (card.category_code, card.level, card.attack, card.id)

def _cheapest(cards):
	least = None
	for card in cards:
		if least == None or (card.price.average is not None and card.price.average < least):
			least = card.price.average
	return least

def display_card_price(session, lines, indent, card, get_price, rarity):
	price_data = session.price_data(card)
	price = get_price(price_data)
	price_str = ygo.abstract.format_money(price)
	if rarity:
		lines.append('{} {}'.format(indent*' ', card.name))
		for print_run in price_data:
			tag = print_run.print_tag
			rarity = print_run.rarity
			print_price = print_run.price.average
			if print_price is not None:
				print_price_str = ygo.abstract.format_money(print_price)
				lines.append('{} [{}] {} - {}'.format((indent+4)*' ', print_price_str, tag, rarity))
			else:
				lines.append('{}         {} - {}'.format((indent+4)*' ', tag, rarity))
	else:
		lines.append('{}[{}] {}'.format(indent*' ', price_str, card.name))
	return price

def display_set_price(session, cardset, get_price, rarity):
	total = 0
	lines = ['All Cards ({price})']
	for card in sorted(cardset, key=_default_sort_key):
		total += display_card_price(session, lines, 4, card, get_price, rarity)
	output = os.linesep.join(lines)
	output = output.format(price=ygo.abstract.format_money(total))
	sys.stdout.write(output+'\n')

def display_deck_price(session, deck, get_price, rarity):
	rarity = False
	info = {
		'main' : 0,
		'monster': 0,
		'spell': 0,
		'trap': 0,
		'side': 0,
		'extra': 0,
		'total': 0
	}

	lines = ['Main Deck ({main})']
	lines.append('    Monsters ({monster})')
	for monster in deck.main.monsters():
		info['monster'] += display_card_price(session, lines, 8, monster, get_price, rarity)

	lines.append('    Spells ({spell})')
	for spell in deck.main.spells():
		info['spell'] += display_card_price(session, lines, 8, spell, get_price, rarity)
	
	lines.append('    Traps ({trap})')
	for trap in deck.main.traps():
		info['trap'] += display_card_price(session, lines, 8, trap, get_price, rarity)

	lines.append('Extra ({extra})')
	for monster in deck.extra:
		info['extra'] += display_card_price(session, lines, 4, monster, get_price, rarity)

	lines.append('Side ({side})')
	for card in deck.side:
		info['side'] += display_card_price(session, lines, 4, card, get_price, rarity)
	lines.append('Total ({total})')

	info['main'] = info['monster'] + info['spell'] + info['trap']
	info['total'] = info['main'] + info['side'] + info['extra']
	info = dict((key, ygo.abstract.format_money(value)) for (key, value) in info.items())
	output = os.linesep.join(lines)
	output = output.format(**info)
	sys.stdout.write(output+'\n')

if __name__ == '__main__':
	session = ygo.Session(YGOPRO_PATH)
	parser = construct_parser()
	args = parser.parse_args()

	deck = get_input(session, args)

	display_info(session, args, deck)
	
	write_output(session, args, deck)
	
