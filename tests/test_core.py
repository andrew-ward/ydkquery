import unittest
import validate
import os, sys
sys.path.insert(0, '..')

import yugioh
class TestCore(unittest.TestCase):
	def assertPath(self, path):
		self.assertTrue(os.path.exists(path))
		
	def test_config(self):	
		self.assertPath(yugioh.core.config.DATABASE_PATH)
		self.assertPath(yugioh.core.config.BANLIST_PATH)
		self.assertPath(yugioh.core.config.DECK_DIRECTORY)

	def test_banlist(self):
		bls = yugioh.core.banlist.load_banlists()
		self.assertTrue(bls != None)
		self.assertTrue(len(bls) > 0)
		for banlist in bls:
			if 'Traditional' in banlist.name:
				self.assertTrue(len(banlist.forbidden_cards()) == 0)
			else:
				self.assertTrue(len(banlist.forbidden_cards()) > 0)
			self.assertTrue(len(banlist.limited_cards()) > 0)
			self.assertTrue(len(banlist.semi_limited_cards()) > 0)
			
	def test_database(self):
		db = yugioh.core.database.YGOProDatabase(yugioh.core.config.DATABASE_PATH, yugioh.core.config.BANLIST_PATH)
		db.open()
		
		unicore = db.find('44155002', by='id')
		validate.validate_card(self, unicore, cid='44155002', name='The Fabled Unicore')
		
		catsith = db.find('The Fabled Catsith', by='name')
		validate.validate_card(self, catsith, cid='56399890', name='The Fabled Catsith')
		
		fiends = list(db.find_all(['Fabled Raven', 'Fabled Kushano'], by='name'))
		self.assertEqual(len(fiends), 2)
		validate.validate_card(self, fiends[0], cid='47217354', name='Fabled Raven')
		validate.validate_card(self, fiends[1], cid='97439806', name='Fabled Kushano')
		
		beasts = list(db.find_all(['29905795', '82888408'], by='id'))
		self.assertEqual(len(beasts), 2)
		validate.validate_card(self, beasts[0], cid='29905795', name='The Fabled Chawa')
		validate.validate_card(self, beasts[1], cid='82888408', name='The Fabled Cerburrel')
		
		all_fabled = list(db.search('%Fabled%', by='name'))
		self.assertEqual(len(all_fabled), 27)
		
		all_dragon_ruler_cards = list(db.search('%Dragon Ruler%', by='text'))
		self.assertEqual(len(all_dragon_ruler_cards), 8)
		
		all_cards = db.all_cards()
		self.assertGreaterEqual(len(all_cards),  7402) # as of YGOPro Percy 1.033.6, Oct 31
		
		new_id = db.get_new_id()
		with self.assertRaises(yugioh.core.database.CardNotFoundException):
			card = db.find(new_id, by='id')
		
	def test_cards(self):
		db = yugioh.core.database.database()
		all_cards = db.all_cards()
		for card in all_cards:
			validate.validate_card(self, card)
unittest.main()
