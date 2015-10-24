#!/usr/bin/env python
"""
usage: python netdeck.py

A command line tool that allows you to download decklists from tcgplayer.com
Give it a deckid or a url, and it will download the deck, convert it to ydk
and save it to your ygopro decks folder, making it instantly available\
in the deck editor.

Uses ydklib.tcgplayer and ydklib.ydk
"""

from yugioh import tcgplayer, ygopro
import sys
if __name__ == '__main__':
	if len(sys.argv) < 2:
		sys.out.write('usage: python netdeck.py url/deckid [deck_name]\n')
	elif '-h' in sys.argv:
		sys.out.write('This is a command line tool for downloading decklists off of tcgplayer.com and saving them in your Devpro deck folder for editing and testing\n')
	else:
		url = sys.argv[1]
		deck = tcgplayer.tcgopen(url)
		if len(sys.argv) > 2:
			deck.name = sys.argv[2]
		path = ygopro.deck_path(deck.name)
		with open(path, 'w') as fl:
			ygopro.save_deck(deck, fl)
