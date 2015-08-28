import ygoenum
import ygocard
import collections
import os
import devpro

class YDK(ygocard.YugiohDeck):
	@staticmethod	
	def open(ydk_path):
		name = os.path.basename(ydk_path)[:-4]
		db = devpro.database()
		main = []
		side = []
		extra = []
		author = ''
		current = main
		db.open()
		with open(ydk_path) as fl:
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
		return YDK(name, author, main, side, extra)
		
	def save(self):
		output = '#created by {0}\n'.format(self.author)
		output += '#main\n'
		for card in self.main():
			output += '{0}\n'.format(card.cid())
		output += '#extra\n'
		for card in self.extra():
			output += '{0}\n'.format(card.cid())
		output += '!side\n'
		for card in self.side():
			output += '{0}\n'.format(card.cid())
		

	

# api stuff

def ydk_open(path):
	return YDK.open(path)

