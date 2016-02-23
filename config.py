import argparse
import sys, os

from ygo.core import reconfigure

def main():
	parser = argparse.ArgumentParser(description='configure the ydktools library')
	parser.add_argument('-a', '--all', help="give path to ygopro directory, and configure everything else based on standard directory layout.")
	parser.add_argument('-v', '--validate', action='store_true', help="Check which paths are invalid.")
	parser.add_argument('-c', '--cards', help="Give path to the ygopro database. (cards.cdb)")
	parser.add_argument('-d', '--deck', help="Give path to the folder ygopro stores your .ydk decks.")
	parser.add_argument('-b', '--banlist', help="Give path to ygopro lflist.conf banlist file.")
	args = parser.parse_args()

	if args.validate:
		sys.stdout.write(validate())
	elif args.cards != None:
		reconfigure.update_config(DATABASE_PATH=args.cards)
	elif args.deck != None:
		reconfigure.update_config(DECK_DIRECTORY=args.deck)
	elif args.banlist != None:
		reconfigure.update_config(BANLIST_PATH=args.banlist)
	elif args.all:
		reconfigure.update_config(
			DATABASE_PATH=os.path.join(args.all, "cards.cdb"),
			DECK_DIRECTORY=os.path.join(args.all, "deck"),
			BANLIST_PATH=os.path.join(args.all, "lflist.conf")
		)
def validate():
	info = reconfigure.summary()
	lines = []
	all_good = True
	for row in info:
		valid = row[2]
		if not valid:
			all_good = False
		head = "[X]" if not valid else "[]"
		line = '{} {}="{}"'.format(head, row[0], row[1])
		lines.append(line)
	output = "\n".join(lines) + "\n"
	if all_good:
		output += "Configuration appears to be valid\n"
	else:
		output += "Invalid Configuration\n"
	return output

if __name__ == '__main__':
	main()		
