import ygoenum
import ygocard
import collections
import os
import devpro

def ydk_save(deck, fl):
	output = '#created by {0}\n'.format(deck.author)
	output += '#main\n'
	for card in deck.main():
		output += '{0}\n'.format(card.cid())
	output += '#extra\n'
	for card in deck.extra():
		output += '{0}\n'.format(card.cid())
	output += '!side\n'
	for card in deck.side():
		output += '{0}\n'.format(card.cid())
	fl.write(output)

def ydk_open(path):
	name = os.path.basename(path)[:-4]
	db = devpro.database()
	main = []
	side = []
	extra = []
	author = ''
	current = main
	db.open()
	with open(path) as fl:
		for line in fl:
			if line.startswith('#created by '):
				author = (line.rstrip())[11:]
			elif line.startswith('#main'):
				current = main
			elif line.startswith('#extra'):
				current = extra
			elif line.startswith('!side'):
				current = side
			else:
				cid = int(line.rstrip())
				card = db.card_by_id(cid)
				current.append(card)
	db.close()
	return ygocard.YugiohDeck(name, author, main, side, extra)

