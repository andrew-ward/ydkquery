import os, sys
import argparse
import ygo
import yql
"""
Functionality
	each card
		show price for each card
		show rarities available for each card
	all cards
		sort cards by key
		count cards retrieved	
"""

def construct_parser():
	parser = argparse.ArgumentParser(description='ydktools')

	# Card Query
	parser.add_argument('-q', '--query', help='Use a yql query to specify cards')
	parser.add_argument('-i', '--stdin', '--input', nargs='?', const='ydk', help='read in a decklist from stdin using the given format. Default is ydk.')
	parser.add_argument('-d', '--deck', help='Open a decklist and use those cards')

	# Card Info
	parser.add_argument('-p', '--price', action='store_true', help='Show price of each card')
	parser.add_argument('-r', '--rarity', action='store_true', help='Show available rarities of all cards')


	# Output Format
	parser.add_argument('-o', '--output', nargs='?', const='ydk', help='Write result to file. Determine format by filename. Alternately, just give the format to write result to stdout. If no args are given, will write ydk to stdout.')
	return parser

def get_cards(args):
	cards = None
	if args.deck != None:
		path = args.deck
		cards = ygo.decks.open_deck(path)
	elif args.stdin != None:
		txt = sys.stdin.read()
		cards = ygo.decks.loads(text, fmt=args.stdin)
	if args.query != None:
		query = args.query
		cards = ygo.core.deck.YugiohSet(yql.select(query, cards.all()))
	return cards

def get_info(cards, args):
	deck = {
		'main_monsters' : [],
		'main_spells' : [],
		'main_traps' : [],
		'side' : [],
		'extra' : []
	}
	if isinstance(cards, ygo.core.deck.YugiohDeck):
		for (name, yset) in [
		                     ('main_monsters', cards.main.monsters()),
		                     ('main_spells', cards.main.spells()),
		                     ('main_traps', cards.main.traps()),
		                     ('side', cards.side),
		                     ('extra', cards.extra)
		]:
			for card in yset:
				info = {}
				info['card'] = card
				info['count'] = yset.count(card)
				if args.price or args.rarity:
					info['price_info'] = ygo.prices.card_versions(card)
				deck[name].append(info)
	elif isinstance(cards, ygo.core.deck.YugiohSet):
		for card in cards:
			info = {}
			info['card'] = card
			info['count'] = cards.count(card)
			if args.price or args.rarity:
				info['price_info'] = ygo.prices.card_versions(card)
			if card.in_main_deck() and card.is_monster():
				deck['main_monsters'].append(info)
			if card.in_main_deck() and card.is_spell():
				deck['main_spells'].append(info)
			if card.in_main_deck() and card.is_trap():
				deck['main_traps'].append(info)
			elif card.in_extra_deck():
				deck['extra'].append(info)
	return deck
		
def generate_listing(prefix, cardlist, args):
	output = ''
	total_cost = 0
	for info in cardlist:
		output += '{}{} x{}'.format(prefix, info['card'].name, info['count'])
		if args.rarity and args.price:
			for version in sorted(info['price_info'], key=lambda c: c.low):
				output += '\n{}    {} from {} for ${}'.format(prefix, version.rarity, version.set_name, version.low * info['count'] if version.low else '??')
		elif args.rarity:
			rarity = set()
			for version in info['price_info']:
				rarity.add(version.rarity)
			rarity = list(sorted(rarity, key=ygo.prices.rarity_score))
			output += ' ({})'.format(', '.join(rarity))
		elif args.price:
			cost = info['price_info'].cheapest_price()
			if cost != None:
				cost = cost * info['count']
				output += ' (${})'.format(cost)
				total_cost += cost
			else:
				output += ' ($??)'
		output += '\n'
	return output, total_cost
			

def create_infodump(deck_info, args):
	mmlisting, mmcost = generate_listing(' '*6, deck_info['main_monsters'], args)
	mslisting, mscost = generate_listing(' '*6, deck_info['main_spells'], args)
	mtlisting, mtcost = generate_listing(' '*6, deck_info['main_traps'], args)
	slisting, scost = generate_listing(' '*6, deck_info['side'], args)
	elisting, ecost = generate_listing(' '*6, deck_info['extra'], args)
	
	if args.price and not args.rarity:
		mdcost = mmcost + mscost + mtcost
		total = mdcost + scost + ecost
		return ('Main Deck (${})\n' + 
		        '  Monsters (${})\n' +
		        '{}\n' +
		        '  Spells (${})\n' +
		        '{}\n' +
		        '  Traps (${})\n' +
		        'Side Deck (${})\n' +
		        '{}\n' +
		        'Extra Deck (${})\n' +
		        '{}\n' +
		        'TOTAL: ${}\n').format(mdcost, mmcost,
		mmlisting, mscost, mslisting, mtcost, mtlisting,
		scost, slisting, ecost, elisting, total)
	else:
		return ('Main Deck\n' + 
		        '  Monsters\n' +
		        '{}\n' +
		        '  Spells\n' +
		        '{}\n' +
		        '  Traps\n' +
		        'Side Deck\n' +
		        '{}\n' +
		        'Extra Deck\n' +
		        '{}\n').format(mmlisting, mslisting, mtlisting, slisting, elisting)


if __name__ == '__main__':
	parser = construct_parser()
	args = parser.parse_args()
	cards = get_cards(args)
	if cards == None:
		sys.stdout.write('No cards found.\n')
	elif args.output:
		outpath = args.output
		if isinstance(cards, ygo.core.deck.YugiohSet):
			cards = cards.as_deck()
		ygo.decks.save_deck(cards, outpath)
	else:
		info = get_info(cards, args)	
		sys.stdout.write(create_infodump(info, args))

