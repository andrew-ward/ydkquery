#!/usr/bin/env python
"""
A command line application for viewing information about individual cards.
"""

import yugioh
import sys, locale, re

ACTIONS = {}

def action(v):
	def decorator(f):
		ACTIONS[v] = f
		return f
	return decorator

def _money_fmt(usd):
	# in the future, do price conversions from usd to locale currency.
	return locale.currency(usd)

@action('quickprice')
def quickprice(price_data):
	low = min(version.price.low for version in price_data if version.price)
	return _money_fmt(low)
	
@action('info')
def card_information(price_data):
	if len(price_data) > 0:	
		card = yugioh.ygopro.load_card(price_data[0].name, by='name')
		return card.description()
	else:
		raise yugioh.yugiohprices.APIError('No price information available')
	
@action('prints')
def get_reprints(price_data, verbose=False):
	printruns = []
	for version in price_data:
		if version.price:
			text = '({}) {} (~{}) from "{}"'.format(version.print_tag, version.rarity, _money_fmt(version.price.low), version.set_name)
		else:		
			text = '({}) {} from "{}"'.format(version.print_tag, version.rarity, version.set_name)
		printruns.append(text)
	return price_data[0].name + '\n' + ('\n'.join(printruns))



if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="Get information about a yugioh card.")
	parser.add_argument('cardname', help='The full name of the card. Spelling and punctuation is important. Alternately can be the Card Number or Card ID (printed on the lower left hand corner of most cards).')
	parser.add_argument('-q', '--quickprice', help='Get a quick price check summary of all the releases of the card.', action='store_true')
	parser.add_argument('-p', '--prints', help='Get all the print runs of the card.', action='store_true')
	parser.add_argument('-i', '--info', help='Get the text and stats of the card.', action='store_true')
	parser.add_argument('-t', '--timeline', help='Look at how prices are changing.', action='store_true')
		
	
	args = parser.parse_args()
	locale.setlocale(locale.LC_ALL, '')
	
	price_data = yugioh.yugiohprices.get_price_data(args.cardname)
		
	for flag in ACTIONS:
		if hasattr(args, flag) and getattr(args, flag):
			sys.stdout.write(ACTIONS[flag](price_data) + '\n')	
