from yugioh import yugiohprices, ygopro
import sys, os
import locale

def average(ls):
	return sum(ls) / float(len(ls))

def median(ls):
	if len(ls) == 0:
		return 0
	elif len(ls) == 1:
		return ls[0]
	elif len(ls) == 2:
		return (ls[0] + ls[1]) / 2.0
	elif len(ls) == 3:
		return ls[1]
	else:
		lss = sorted(ls)
		n = len(ls) / 2.0
		i = int(n)
		if n > i:
			return (ls[i] + ls[i+1]) / 2.0
		else:
			return ls[i]

if len(sys.argv) < 2:
	print 'usage: python price.py DECKNAME/DECKPATH'
else:
	path = sys.argv[1]
	if os.path.exists(path):
		full_path = path
	else:
		ypath = ygopro.deck_path(path)
		if os.path.exists(ypath):
			full_path = ypath
		else:
			raise IOError('No such path {0} or {1}'.format(path, ypath))
	ydk = ygopro.load_deck(full_path)
	
	main_price = 0.00
	for card in ydk.main:
		try:
			data = yugiohprices.get_price_data(card)
		except RuntimeError:
			continue
		price = median([version.price.average for version in data if version.price != None])
		main_price += (price * ydk.main.count(card))
	
	side_price = 0.00
	for card in ydk.side:
		try:
			data = yugiohprices.get_price_data(card)
		except RuntimeError:
			continue
		price = median([version.price.average for version in data])
		side_price += (price * ydk.side.count(card))

	extra_price = 0.00
	for card in ydk.extra:
		try:
			data = yugiohprices.get_price_data(card)
		except RuntimeError:
			continue
		price = median([version.price.average for version in data])
		extra_price += (price * ydk.extra.count(card))
		
	locale.setlocale(locale.LC_ALL, '')
		
	main_d = locale.currency( main_price )
	side_d = locale.currency( side_price )
	extra_d = locale.currency( extra_price )
		
	sys.stdout.write(
	'''Main Deck: ~{0}
Extra Deck: ~{1}
Side Deck: ~{2}
'''.format(main_d, extra_d, side_d))
