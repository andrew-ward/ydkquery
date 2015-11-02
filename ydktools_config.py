#!/usr/bin/env python
"""
A command line script that allows easier configuration of the ydktools package.
"""


import yugioh

import sys, os
import locale

def main(args):
	if args.validate:
		if not yugioh.core.config.DATABASE_PATH:
			sys.stdout.write('DATABASE_PATH is invalid.\n')
		else:			
			sys.stdout.write('DATABASE_PATH is ok.\n')
			
		if not yugioh.core.config.BANLIST_PATH:
			sys.stdout.write('BANLIST_PATH is invalid.\n')
		else:			
			sys.stdout.write('BANLIST_PATH is ok.\n')
			
		if not yugioh.core.config.DECK_DIRECTORY:
			sys.stdout.write('DECK_DIRECTORY is invalid.\n')
		else:			
			sys.stdout.write('DECK_DIRECTORY is ok.\n')
	
	elif args.all:
		yugioh.core.configuration.update_config(
			DATABASE_PATH = os.path.join(args.all, 'cards.cdb'),
			BANLIST_PATH = os.path.join(args.all, 'lflist.conf'),
			DECK_DIRECTORY = os.path.join(args.all, 'deck/')
		)
	else:
		if args.cards:
			yugioh.core.configuration.update_config(
				DATABASE_PATH = args.cards
			)
		if args.banlist:
			yugioh.core.configuration.update_config(
				BANLIST_PATH = args.banlist
			)
		if args.decks:
			yugioh.core.configuration.update_config(
				DECK_DIRECTORY = args.decks
			)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description="Configure the ydktools package with paths to an install of ygopro.")
	parser.add_argument('-v', '--validate', help='Check if config file is currently valid.', action='store_true')
	parser.add_argument('-a', '--all', help='Configure all paths automatically by giving a standard ygopro install directory.', nargs='?')
	parser.add_argument('-c', '--cards', help='Set path to cards.cdb database.')
	parser.add_argument('-b', '--banlist',  help='Set path to lflist.conf banlist file.')
	parser.add_argument('-d', '--decks', help='Set path to ygopro deck directory..')
	
	
	
	args = parser.parse_args()
	main(args)

