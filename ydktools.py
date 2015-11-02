#!/usr/bin/env python
"""
A command line application for doing things with yugioh cards.
"""

import yugioh
import sys, locale, re

import ydktools_config
import ydktools_convert
import ydktools_prices
import ydktools_search

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="Use the yugioh python library to do things.")

	sub = parser.add_subparsers(dest='command')

	config = sub.add_parser('config', description="Configure the ydktools package with paths to an install of ygopro.", help='Configure the ydktools package.')	
	config.add_argument('-v', '--validate', help='Check if config file is currently valid.', action='store_true')
	config.add_argument('-a', '--all', help='Configure all paths automatically by giving a standard ygopro install directory.', nargs='?')
	config.add_argument('-c', '--cards', help='Set path to cards.cdb database.')
	config.add_argument('-b', '--banlist',  help='Set path to lflist.conf banlist file.')
	config.add_argument('-d', '--decks', help='Set path to ygopro deck directory..')
	

	convert = sub.add_parser('convert', description='A command line program for converting between deck formats.', help='Convert between deck formats')
	convert.add_argument('input_path', help="a path to a properly formatted .ydk or .txt deck. If you do not give an extension, it will be assumed to be .ydk. If the deck does not exist, it will search the ygopro/deck directory as specified in yugioh.core.config")
	convert.add_argument('output_path', help="The location to save the newly created deck file. You may also simply give a file format (ydk, md, txt), where instead the output will be printed to stdout. If it is merely a deck name, with no extension or path, it will be assumed .ydk, and saved in the ygopro deck directory.")
	
	price = sub.add_parser('price', description="Reads a .ydk deck listing and calculates the expected price of the main, extra, and side deck. Price data is from YugiohPrices.com web api.", help='Check the prices of decks.')
	price.add_argument('deckname', help='Path to a .ydk deck, or just the name of the deck in the ygopro deck folder.')
	price.add_argument('-v', '--verbose', help='print individual card prices', action='store_true')
	group = price.add_mutually_exclusive_group()
	group.add_argument('--low', help='[default] find the lowest price for the deck', action='store_true')
	group.add_argument('--high', help='find the highest price for the deck', action='store_true')
	group.add_argument('--average', help='find the price of a deck if you blindly picked cards from the set of all printings.')
	price.add_argument('-p', '--prefer', help='find the price while preferring copies of card of a particular rarity. Also suports Holo as a rarity, which prefers anything that isn\'t Common or Rare.')


	search = sub.add_parser('search', description='Search for yugioh cards, and look at various print information about them.', help='Get information on single cards.')
	search.add_argument('cardname', help='The full name of the card. Spelling and punctuation is important. Alternately can be the Card Number or Card ID (printed on the lower left hand corner of most cards).')
	search.add_argument('-v', '--verbose', help='Show more information than normal', action='store_true')
	search.add_argument('-q', '--quickprice', help='Get a quick price check summary of all the releases of the card.', action='store_true')
	search.add_argument('-p', '--prints', help='Get all the print runs of the card.', action='store_true')
	search.add_argument('-i', '--info', help='Get the text and stats of the card.', action='store_true')
	search.add_argument('-f', '--find', help='Find a card using sql expressions.', action='store_true')


	args = parser.parse_args()
	
	if args.command == 'config':
		ydktools_config.main(args)
	elif args.command == 'search':
		ydktools_search.main(args)
	elif args.command == 'price':
		ydktools_prices.main(args)
	elif args.command == 'convert':
		ydktools_convert.main(args)
