"""This module is for managing the banlist (lflist.conf) files supplied by ygopro."""
import re
from . import config, compat

class ParseError(RuntimeError):
	pass
	
def load_banlists():
	if config.BANLIST_PATH:
		return load_lflist_banlists(config.BANLIST_PATH)
	else:
		return load_web_banlist()

class Banlist(dict):
	"""Holds all the information for a single banlist.
	
	:ivar name: the name of the banlist
	:vartype name: string"""
	def __init__(self, name, f, l, s):
		self.name = name
		for thing in f:
			self[thing] = 0
		for thing in l:
			self[thing] = 1
		for thing in s:
			self[thing] = 2
	def __repr__(self):
		return 'Banlist({0})'.format(self.name)
	def __str__(self):
		return 'Banlist({0})'.format(self.name)
	
	def allowed(self, name, cid):
		"""Return how many copies of the card are allowed to be run under this ban list.
		
		:param card: the card you are checking.
		:type card: core.YugiohCard
		:returns: how many copies you can run.
		:rtype: int
		"""
		return self.get(cid, 3)
			
		
def load_lflist_banlists(lflist_path):
	"""Get every banlist available as a list. Used by yugioh.core.database.
	
	:param banlist_path: the path to the lflist.conf supplied by ygopro.
	:type banlist_path: string
	
	:returns: list of all the banlists information available.
	:rtype: list of Banlist	"""
	if lflist_path == None:
		raise IOError('Cannot access banlist. Check your configuration.')
	with open(lflist_path, 'r') as fl:
		lines = [x.rstrip() for x in fl.readlines()]
		banlists = []
		
		forbidden = []
		limited = []
		semi_limited = []
		name = None
		current = None
		
		row_re = re.compile('^(\d+) *[012] *--(.*?)$')
		
		for line in lines[1:]:
			if line.startswith('!'):
				if current != None:
					bl = Banlist(name, forbidden, limited, semi_limited)
					banlists.append(bl)
				name = line[1:]
				forbidden = []
				limited = []
				semi_limited = []
				current = None
			elif line.startswith('#forbidden'):
				current = forbidden
			elif line.startswith('#limit'):
				current = limited
			elif line.startswith('#semi limit'):
				current = semi_limited
			elif len(line.strip()) == 0:
				continue
			else:
				match = row_re.match(line)
				cid = match.group(1)
				current.append(cid)
		if current != None:
			bl = Banlist(name, forbidden, limited, semi_limited)
			banlists.append(bl)
		return banlists


"""
An alternate banlist backend that uses the official Konami forbidden/limited list website.

Requires lxml
"""
class KBanlist(Banlist):
	def allowed(self, name, cid):
		for kname, count in self.items():
			if name.encode('utf8', 'replace').upper() == re.sub(' +', ' ', kname.upper()):
				return count

def load_web_banlist():
	"""Returns a Banlist object for the tcg, from the konami official website. Currently does not work, as the card names are in uppercase making it difficult to get the card id."""
	from lxml import html
	text = compat.get_html('http://www.yugioh-card.com/en/limited/')
	tree = html.fromstring(text)
	content = tree.xpath("/html/body/div[@id='wrapper']/div[@id='content_colfull']")[0]

	tables = content.xpath("div[@id='colfull_main']/table")
	f = []
	forbidden = tables[0]
	for row in forbidden.xpath("tr"):
		columns = row.xpath('td')
		if columns[1].text:
			f.append(columns[1].text)

	l = []	
	limited = tables[1]
	for row in limited.xpath('tr'):
		columns = row.xpath('td')
		if columns[1].text:
			l.append(columns[1].text)

	s = []
	semi_limited = tables[2]
	for row in semi_limited.xpath('tr'):
		columns = row.xpath('td')		
		if columns[1].text:
			s.append(columns[1].text)

	return [KBanlist('TCG', f, l, s)]
