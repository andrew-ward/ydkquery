from base_test import Test
import unittest
import sys

sys.path.insert(0, '..')
class TestQuery(Test):
	def test_banlist(self):
		from yugioh.core import banlist
		bls = banlist.load_banlists()
		self.assertIsNotNone(bls)
		self.assertGreater(len(bls), 0)
		for ls in bls:
			if 'tcg' in ls.name.lower():
				f = [name for name in ls if ls[name] == 0]
				l = [name for name in ls if ls[name] == 1]
				s = [name for name in ls if ls[name] == 2]
				self.assertGreater(len(f), 65)
				self.assertGreater(len(l), 60)
				self.assertGreater(len(s), 10)
				
	def test_database(self):
		from yugioh.core import database
		
		with database.YGOProDatabase() as db:
		
			unicore = db.find_id('44155002')
			self.validate_card(unicore, cid='44155002', name='The Fabled Unicore')
			
			catsith = db.find_name('The Fabled Catsith')
			self.validate_card(catsith, cid='56399890', name='The Fabled Catsith')

			all_fabled = db.find_sql('name like "%Fabled%"')
			self.assertEqual(len(all_fabled), 27)
			
			all_dragon_ruler_cards = db.find_sql('desc like "%Dragon Ruler%"')
			self.assertEqual(len(all_dragon_ruler_cards), 8)
			
			all_cards = db.find_all()
			self.assertGreaterEqual(len(all_cards),  7402) # as of YGOPro Percy 1.033.6, Oct 31
			
			with self.assertRaises(database.CardNotFoundException):
				db.find_id('7')
			
			
	def test_query(self):
		from yugioh import decklist, ydk, ygojson, search
		with search.get_source() as src:
			with open('tests/AI_BattlinBoxer.ydk') as fl:
				text = fl.read()
				deck = ydk.load(text, src)
				self.validate_deck(deck)
				
				#deck = decklist.load(text, src)
				#self.validate_deck(deck)
				
				#deck = ygojson.load(text, src)
				#self.validate_deck(deck)
			
unittest.main()
