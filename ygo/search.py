from .core import database

def get_source():
	# automatically choose the best yugioh card source.
	# currently only supports YGOPro
	try:
		return database.YGOProDatabase()
	except:
		raise NotImplementedError('No alternate card source available.')

def find(card_key):
	with database.YGOProDatabase() as db:
		return db.find(card_key)
		
def all_cards():
	with database.YGOProDatabase() as db:
		return db.all_cards()
	
def select(f):
	for card in all_cards():
		if f(card):
			yield card

class SmartYugiohCard(database.YGOProCard):
	def __init__(self, card_key):
		with database.YGOProDatabase() as db:
			row = db.get_row(card_key)
		database.YGOProCard.__init__(self, row)
