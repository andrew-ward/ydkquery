from .core import database

def get_source():
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
	
