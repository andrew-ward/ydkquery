'''
ydktools config -a /path/to/ygopro
ydktools info --[price|info|name|sets|rarity] (deckpath|-s keywords)
ydktools price [-v] (deckpath|-s keywords)
ydktools convert (deckpath|-s keywords) [-o destpath]

'''
import os, sys
def parse_main():
	import argparse
	parser = argparse.ArgumentParser(description='ydktools')
	subparsers = parser.add_subparsers(dest='command')
	
	parse_config(subparsers)
	parse_info (subparsers)
	parse_price(subparsers)
	parse_convert(subparsers)

	args = parser.parse_args()
	return args
	
def parse_info(parent):
	parser = parent.add_parser('info')
	parser.add_argument('select', nargs='*')
	parser.add_argument('-p', '--price', action='store_true')
	parser.add_argument('-i', '--info', action='store_true')
	parser.add_argument('-s', '--sets', action='store_true')
	parser.add_argument('-r', '--rarity', action='store_true')
	parser.add_argument('-c', '--count', action='store_true')
	parser.add_argument('-a', '--ascending', action='store_true')
	parser.add_argument('-d', '--descending', action='store_true')
	parser.add_argument('-j', '--json', action = 'store_true', help='Instead of print output to stdout, write a deck list in json (.jydk)')
	
def parse_price(parent):
	parser = parent.add_parser('price')
	parser.add_argument('path', nargs='*')
	parser.add_argument('-v', '--verbose', action='store_true')
	parser.add_argument('-s', '--search', action='store_true')
	parser.add_argument('-p', '--prefer')
	parser.add_argument('-m', '--max-rarity', action='store_true')
	
def parse_convert(parent):
	parser = parent.add_parser('convert')
	parser.add_argument('-s', '--search', action='store_true')
	parser.add_argument('source', nargs='*')
	parser.add_argument('-o', '--output')
	
	
def parse_config(parent):
	parser = parent.add_parser('config')
	parser.add_argument('-a', '--all')
	parser.add_argument('-v', '--validate', action='store_true')
	parser.add_argument('-c', '--cards')
	parser.add_argument('-d', '--deck')
	parser.add_argument('-b', '--banlist')
	
	
def query_search(kws):
	from ygo import search, query
	cards = search.all_cards()
	func = query.create_filter(kws)
	return func(cards)
	
def find_cards(kws, search_mode):
	from ygo import ygojson, decks, search, query
	from ygo.core import deck
	if len(kws) == 0:
		text = sys.stdin.read()
		deck = ygojson.load(text) # either json or txt
		return deck
	elif len(kws) == 1 and search_mode == False:
		return decks.open_deck(kws[0]) # get fmt from kws[0] extension
	else:
		cards = query_search(kws)
		return deck.YugiohDeck('.tmp', 'unknown',
			main_deck=[card for card in cards if card.is_main_deck()],
			extra_deck=[card for card in cards if card.is_extra_deck()]
		)

def info_price(card):
	from ygo import prices
	from ygo.core import compat
	versions = prices.card_versions(card.name.encode('utf8', 'replace'))
	price = versions.price()
	return compat.format_money(price)
	
def info_get_price(card):
	from ygo import prices
	versions = prices.card_versions(card.name.encode('utf8', 'replace'))
	return versions.price()
	
	
def info_description(card):
	return card.description()
	
def info_rarity(card, sep=', ', prefix=''):
	from ygo import prices
	versions = prices.card_versions(card.name.encode('utf8', 'replace'))
	rarities = set([version.rarity for version in versions])
	return sep.join(prefix+str(x) for x in rarities)
	
def info_sets(card, sep='\n', prefix='  '):
	from ygo import prices
	from ygo.core import compat
	versions = prices.card_versions(card.name.encode('utf8', 'replace'))
	output = []
	for version in versions:
		p = compat.format_money(version.low) if version.has_price else '??'
		output.append('{} for ~{} from {}'.format(version.rarity, p, version.set_name))
	return sep.join(prefix+str(x) for x in output)
		
def info_main(args):
	from ygo.core import compat
	deck = find_cards(args.select, True) # None implies undecided (~AW what does this mean? I don't remember...)
	if args.json:
		raise NotImplementedError('JSON output not yet implemented.')
	elif args.count:
		a = len(deck.all())
		sys.stdout.write('{}\n'.format(a))
	elif args.descending or args.ascending:
		cards = deck.all()
		prices = [(info_get_price(card), card) for card in cards]
		prices.sort()
		if args.descending:
			prices.reverse()
		for price, card in prices:
			sys.stdout.write('{} {}\n'.format(card.name.encode('utf8', 'replace'), compat.format_money(price)))
	else:
		for card in deck.all():
			if args.info:
				sys.stdout.write('\n'+info_description(card))
			else:
				sys.stdout.write(card.name.encode('utf8', 'replace'))
			if args.price:
				sys.stdout.write(' {}'.format(info_price(card)))
			if args.rarity:
				sys.stdout.write(' (' + info_rarity(card) + ')')
			
			if args.sets:
				sys.stdout.write('\n'+info_sets(card))
			sys.stdout.write('\n')
	
def smart_price(card, prefer, max_rarity):
	# preference currently does not work
	from ygo import prices
	versions = prices.card_versions(card)
	if max_rarity:
		selected = versions.select_max_rarity()
	elif not prefer:
		selected = versions
	elif prefer.lower() == 'holo':
		selected = versions.holos()
	else:
		selected = versions.select_at_least(prefer)
	if len(selected) == 0:
		selected = versions
	if not selected.has_price:
		return None
	else:
		return selected.price()
	
def price_main(args):
	from ygo.core import compat
	deck = find_cards(args.path, args.search)
	output = 'Main Deck {main_total}\n'
	main_price = 0.0
	if args.verbose:
		output += '  Monsters\n'
	for card in deck.main.monsters():
		price = smart_price(card, args.prefer, args.max_rarity)
		if args.verbose:
			output += '    {}{} - {}\n'.format(
				card.name.encode('utf8', 'replace'),
				' x'+str(deck.main.count(card)) if not args.search else '',
				compat.format_money(price) if price else '??'	
			)
		if price != None:
			main_price += (price * deck.main.count(card))
		
	if args.verbose:
		output += '  Spells\n'
	for card in deck.main.spells():
		price = smart_price(card, args.prefer, args.max_rarity)
		if args.verbose:
			output += '    {}{} - {}\n'.format(
				card.name.encode('utf8', 'replace'),
				' x'+str(deck.main.count(card)) if not args.search else '',
				compat.format_money(price) if price else '??'	
			)
		if price != None:
			main_price += (price * deck.main.count(card))
			
	if args.verbose:		
		output += '  Traps\n'
	for card in deck.main.traps():
		price = smart_price(card, args.prefer, args.max_rarity)
		if args.verbose:
			output += '    {}{} - {}\n'.format(
				card.name.encode('utf8', 'replace'),
				' x'+str(deck.main.count(card)) if not args.search else '',
				compat.format_money(price) if price else '??'	
			)
		if price != None:
			main_price += (price * deck.main.count(card))
			
	output += 'Extra Deck {extra_total}\n'
	extra_price = 0.0
	for card in deck.extra:
		price = smart_price(card, args.prefer, args.max_rarity)
		if args.verbose:
			output += '  {}{} - {}\n'.format(
				card.name.encode('utf8', 'replace'),
				' x'+str(deck.extra.count(card)) if not args.search else '',
				compat.format_money(price) if price else '??'	
			)
		if price != None:
			extra_price += (price * deck.extra.count(card))
			
	output += 'Side Deck {side_total}\n'
	side_price = 0.0
	for card in deck.side:
		price = smart_price(card, args.prefer, args.max_rarity)
		if args.verbose:
			output += '  {}{} - {}\n'.format(
				card.name.encode('utf8', 'replace'),
				' x'+str(deck.side.count(card)) if not args.search else '',
				compat.format_money(price) if price else '??'	
			)
		if price != None:
			side_price += (price * deck.side.count(card))
	output += 'Total {final_total}\n'
	final_price = main_price + side_price + extra_price
	output = output.format(
		main_total = compat.format_money(main_price),
		extra_total = compat.format_money(extra_price),
		side_total = compat.format_money(side_price),
		final_total = compat.format_money(final_price)
	)
	sys.stdout.write(output)
	
def convert_main(args):
	from ygo import decks
	deck = find_cards(args.source, args.search)
	if args.output:
		decks.save(deck, args.output) # get fmt from args.output extension
	else:
		decks.save(deck, 'txt') #no dest path, so write to stdout
	

def config_main(args):
	from ygo.core import reconfigure
	if args.all:
		reconfigure.update_config(
			DECK_DIRECTORY=os.path.join(args.all, 'deck/'),
			DATABASE_PATH=os.path.join(args.all, 'cards.cdb'),
			BANLIST_PATH=os.path.join(args.all, 'lflist.conf')
		)
	if args.validate:
		data = reconfigure.summary()
		for var, value, valid in data:
			sys.stdout.write('[{}] {} = {}\n'.format('ok' if valid else 'XX', var, value))
	if args.cards:
		reconfigure.update_config(DATABASE_PATH=args.cards)
	if args.deck:
		reconfigure.update_config(DECK_DIRECTORY=args.deck)
	if args.banlist:
		reconfigure.update_config(BANLIST_PATH=args.banlist)

if __name__ == '__main__':
	args = parse_main()
	if args.command == 'config':
		config_main(args)
	elif args.command == 'info':
		info_main(args)
	elif args.command == 'price':
		price_main(args)
	elif args.command == 'convert':
		convert_main(args)
