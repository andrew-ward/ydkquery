"""
An alternate banlist backend that uses the official Konami forbidden/limited list website.
To use:

.. code:: python

with database.YGOProDatabase(banlists=konami_banlist.load_tcg_banlist()) as db:
	# do things
	
	
This puts ydktools one step closer to eliminating the dependency on ygopro.
Does not work on python3, because lxml does not exist?
"""
from  .banlist import Banlist, ParseError
from lxml import html
import sys

if sys.version_info.major == 2:
	from urllib import urlopen
elif sys.version_info.major == 3:
	from urllib.request import urlopen
else:
	svi = sys.version_info
	raise NotImplementedError('Python version {0}.{1}.{3} not supported'.format(svi.major, svi.minor, svi.micro))

class KBanlist(Banlist):
	def allowed(self, card):
		for cardname, value in self.items():
			if card.name.upper() == cardname:
				return value
		return 3

def load_tcg_banlist():
	"""Returns a Banlist object for the tcg, from the konami official website. Currently does not work, as the card names are in uppercase making it difficult to get the card id."""
	fl = urlopen('http://www.yugioh-card.com/en/limited/')
	text = fl.read()
	tree = html.fromstring(text)
	content = tree.xpath("/html/body/div[@id='wrapper']/div[@id='content_colfull']")[0]

	tables = content.xpath("div[@id='colfull_main']/table")
	
	f = []
	forbidden = tables[0]
	for row in forbidden.xpath("tr"):
		columns = row.xpath('td')
		f.append(columns[1].text)
	
	l = []	
	limited = tables[1]
	for row in limited.xpath('tr'):
		columns = row.xpath('td')
		l.append(columns[1].text)

	s = []
	semi_limited = tables[2]
	for row in limited.xpath('tr'):
		columns = row.xpath('td')
		s.append(columns[1].text)
		
	raise NotImplementedError("yugioh.core.konami_banlist.load_tcg_banlist Currently does not work, as the card names are in uppercase making it difficult to get the card id.")
	return [Banlist('TCG', f, l, s)]
