import ygo
from lxml import html
import sys
def load(url, convert=None):
	if isinstance(url, int) or url.isdigit():
		url = 'http://yugiohtopdecks.com/ygopro_deck/{}'.format(url)
	text = ygo.core.compat.get_html(url)
	try:
		deck = ygo.decks.load(text, "ydk")
		if convert == None:
			return deck
		else:
			return ygo.decks.dump(deck, convert)
	except ygo.core.database.CardNotFoundException:
		return None

if __name__ == '__main__':
	deck_id = sys.argv[1]
	deck = load(deck_id, 'ydk')
	if deck:
		sys.stdout.write(deck)
	else:
		sys.stdout.write("{} is not a valid yugiohtopdecks.py deck.\n".format(deck_id))
