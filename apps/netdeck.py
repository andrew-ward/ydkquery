import tcgplayer
import ydk
import sys

if len(sys.argv) < 2:
	print 'usage: python tcgdl url/deckid'
elif '-h' in sys.argv:
	print 'This is a command line tool for downloading decklists off of tcgplayer.com and saving them in your Devpro deck folder for editing and testing'
else:
	url = sys.argv[1]
	deck = tcgplayer.tcg_open(url)
	path = ydk.ydk_path(deck.name)
	with open(path, 'w') as fl:
		ydk.ydk_save(deck, fl)
