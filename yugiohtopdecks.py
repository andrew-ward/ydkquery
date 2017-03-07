"""
Download and print a deck from yugiohtopdecks

Does not currently work after they changed their ydk format
"""
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
		deck = session.load(text, "ydk")
		return session.dump(deck, 'txt')+'\n'


if __name__ == '__main__':
	deck_id = sys.argv[1]
	deck = download(deck_id)
	sys.stdout.write(deck)
