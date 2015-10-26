import re
from . import config

class ParseError(RuntimeError): pass

class Banlist(object):
	def __init__(self, name, f, l, s):
		self.name = name
		self._cards = {}
		for cid in f:
			self._cards[cid] = 0
		for cid in l:
			self._cards[cid] = 1
		for cid in s:
			self._cards[cid] = 2
	def __repr__(self):
		return 'Banlist({0})'.format(self)
	def __str__(self):
		return self.name
	def __getitem__(self, cid):
		return self._cards.get(cid, 3)
	def forbidden(self, cid):
		return self[cid] == 0
	def limited(self, cid):
		return self[cid] == 1
	def semi_limited(self, cid):
		return self[cid] == 2
	def unlimited(self, cid):
		return self[cid] == 3
		
			
		
def load_banlists(banlist_path=None):
	banlist_path = banlist_path or config.BANLIST_PATH
	with open(banlist_path, 'r') as fl:
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
