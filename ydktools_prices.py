#!/usr/bin/env python
"""
usage: python price.py DECKNAME/DECKPATH

Reads a .ydk deck listing and calculates the expected price of the main, extra, and side deck. Price data is from YugiohPrices.com web api.

In the future, I might add more customization to this. For now, if you need something more complicated, you'll have to use the yugioh.yugiohprices api manually.
"""

from yugioh import yugiohprices, ygopro, findpath
import sys, os
import locale

def average(ls):
	return sum(ls) / float(len(ls))
			
def _is_holo(vers):
	return vers.rarity != 'Rare' and vers.rarity != 'Common'
			
def _expected_price(card_data, mode, pref):
	card_data = [version for version in card_data if version.price != None]
	if pref == None:
		pass
	elif pref.lower() == 'holo':
		tmp = [version for version in card_data if _is_holo(version)]
		if len(tmp) > 1:
			card_data = tmp
	else:
		result = []
		for version in card_data:
			if version.rarity == pref:
				result.append(version)
		if len(result) > 0:
			card_data = result
	
	if mode == 'low':
		return min([version.price.low for version in card_data])
	elif mode == 'high':
		return max([version.price.high for version in card_data])
	elif mode == 'average':
		return min([version.price.average for version in card_data])
	else:
		raise NotImplementedError('Someone fucked up')

def _v_print_card_price(card, price, count):
	sys.stdout.write('  {0} = {1}\n'.format(card.name, locale.currency(price)))
	
def _money_fmt(usd):
	# in the future, do price conversions from usd to locale currency.
	return locale.currency(usd)

def main(args):		
	path = args.deckname
	locale.setlocale(locale.LC_ALL, '')
	
	full_path = findpath.find_deck(path)
	
	if full_path == None:
		raise RuntimeError('Invalid deck name {0}'.format(path))
	
	ydk = ygopro.load_deck(full_path)
	verbose = args.verbose
	
	pref = args.prefer
	mode = 'high' if args.high else 'average' if args.average else 'low'
	
	
	main_price = 0.00
	for card in ydk.main:
		try:
			data = yugiohprices.get_price_data(card)
		except RuntimeError:
			continue
		price = _expected_price(data, mode, pref)
		count = ydk.main.count(card)
		if verbose: _v_print_card_price(card, price, count)
		main_price += (price * count)
	
	side_price = 0.00
	for card in ydk.side:
		try:
			data = yugiohprices.get_price_data(card)
		except RuntimeError:
			continue
		price = _expected_price(data, mode, pref)
		count = ydk.side.count(card)
		if verbose: _v_print_card_price(card, price, count)
		side_price += (price * count)

	extra_price = 0.00
	for card in ydk.extra:
		try:
			data = yugiohprices.get_price_data(card)
		except RuntimeError:
			continue
		price = _expected_price(data, mode, pref)
		count = ydk.extra.count(card)
		if verbose: _v_print_card_price(card, price, count)
		extra_price += (price * count)
		
		
	sys.stdout.write(' Main Deck: ~{0}\n'.format(_money_fmt(main_price)))
	sys.stdout.write('Extra Deck: ~{0}\n'.format(_money_fmt(extra_price)))
	sys.stdout.write(' Side Deck: ~{0}\n'.format(_money_fmt(side_price)))
	sys.stdout.write('     Total: ~{0}\n'.format(_money_fmt(main_price+extra_price+side_price)))

