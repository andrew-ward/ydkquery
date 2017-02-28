import sys
sys.dont_write_bytecode = True
import ygo
from ygopro_config import YGOPRO_PATH
from lxml import html

def download(url):
	if isinstance(url, int) or url.isdigit():
		url = 'http://yugiohtopdecks.com/ygopro_deck/{}'.format(url)
	with ygo.Session(YGOPRO_PATH) as session:
		text = ygo.abstract.get_html(url)
		try:
			deck = session.load(text, "ydk")
			return session.dump(deck, 'txt')+'\n'
		except ygo.ygopro.CardNotFoundException:
			return None

if __name__ == '__main__':
	deck_id = sys.argv[1]
	deck = download(deck_id)
	if deck:
		sys.stdout.write(deck)
	else:
		sys.stdout.write("{} is not a valid yugiohtopdecks.py deck.\n".format(deck_id))
