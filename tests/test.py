import unittest
import os, sys
sys.path.insert(0, '..')

import yugioh

def validate_card(self, card, **kwargs):
	self.assertIsNotNone(card)
	self.assertIsNotNone(card.name)
	self.assertIsNotNone(card.text)
	
	self.assertIsNotNone(card.category)
	self.assertIn(card.category, yugioh.core.enum.MAGIC_NUMBERS['category'])
	
	self.assertIsNotNone(card.cid)
	self.assertTrue(card.cid.isdigit())

	if card.is_monster():
		self.assertIsNotNone(card.attribute)
		self.assertIn(card.attribute, yugioh.core.enum.MAGIC_NUMBERS['attribute'])	
			
		self.assertIsNotNone(card.type)
		self.assertIn(card.type, yugioh.core.enum.MAGIC_NUMBERS['type'])
		
		self.assertIn(card.level, range(0, 13))
		self.assertIsInstance(card.attack, int)
		self.assertIsInstance(card.defense, int)
		if card.is_pendulum():
			self.assertIsInstance(card.left_scale, int)
			self.assertGreaterEqual(card.left_scale, 0)
			self.assertLessEqual(card.left_scale, 13)
			
			self.assertIsInstance(card.right_scale, int)
			self.assertGreaterEqual(card.right_scale, 0)
			self.assertLessEqual(card.right_scale, 13)
		else:
			self.assertIsNone(card.left_scale)
			self.assertIsNone(card.right_scale)
	else:
		# I can't be sure these will be None if the card isn't a monster because of trap monster bullshit.
		pass
	self.assertIn(card.banlist_status(), ['forbidden', 'limited', 'semi-limited', 'unlimited'])
	
	for attrib, exp_val in kwargs.items():
		self.assertEqual(card[attrib], exp_val)

def validate_deck(self, deck, *expected_cards):
	for card in deck.main:
		validate_card(self, card)
	for card in deck.side:
		validate_card(self, card)
	for card in deck.extra:
		validate_card(self, card)
		
	all_cards = deck.all()
	self.assertEqual(len(all_cards), len(deck.main) + len(deck.side) + len(deck.extra))
		
	# check that these don't error
	deck.as_ydk()
	deck.as_decklist()
	deck.as_markdown()
	
	self.assertIsNotNone(deck.author)
	self.assertIsNotNone(deck.name)
	
	self.assertEqual(deck.main.size(), len(deck.main.enumerate()))
	
	total = 0
	for card in deck.main:
		total += deck.main.count(card)
	self.assertEqual(total, deck.main.size())

	for cardname in expected_cards:
		self.assertIsNotNone(deck.all().get(cardname))

class TestCore(unittest.TestCase):
	def assertPath(self, path):
		try:
			self.assertIsNotNone(path)
			self.assertTrue(os.path.exists(path))
		except AssertionError:
			raise AssertionError('{0} is not an existing path.'.format(path))
		
	def test_config(self):	
		self.assertPath(yugioh.core.config.DATABASE_PATH)
		self.assertPath(yugioh.core.config.BANLIST_PATH)
		self.assertPath(yugioh.core.config.DECK_DIRECTORY)

	def test_banlist(self):
		bls = yugioh.core.banlist.load_banlists()
		self.assertIsNotNone(bls)
		self.assertGreater(len(bls), 0)
			
	def test_database(self):
		db = yugioh.core.database.YGOProDatabase(yugioh.core.config.DATABASE_PATH, yugioh.core.banlist.load_banlists(yugioh.core.config.BANLIST_PATH))
		db.open()
		
		unicore = db.find('44155002', by='id')
		validate_card(self, unicore, cid='44155002', name='The Fabled Unicore')
		
		catsith = db.find('The Fabled Catsith', by='name')
		validate_card(self, catsith, cid='56399890', name='The Fabled Catsith')
		
		fiends = list(db.find_all(['Fabled Raven', 'Fabled Kushano'], by='name'))
		self.assertEqual(len(fiends), 2)
		validate_card(self, fiends[0], cid='47217354', name='Fabled Raven')
		validate_card(self, fiends[1], cid='97439806', name='Fabled Kushano')
		
		beasts = list(db.find_all(['29905795', '82888408'], by='id'))
		self.assertEqual(len(beasts), 2)
		validate_card(self, beasts[0], cid='29905795', name='The Fabled Chawa')
		validate_card(self, beasts[1], cid='82888408', name='The Fabled Cerburrel')
		
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
			validate_card(self, card)
			
class TestYGOPro(unittest.TestCase):
	
	def test_deck_path(self):
		self.assertEqual(
			yugioh.ygopro.deck_path(),
			yugioh.core.config.DECK_DIRECTORY)
		self.assertEqual(
			yugioh.ygopro.deck_path('AI_Mermail'),
			os.path.join(yugioh.core.config.DECK_DIRECTORY, 'AI_Mermail.ydk'))
		self.assertEqual(
			yugioh.ygopro.deck_path('AI_DarkWorld.ydk'),
			os.path.join(yugioh.core.config.DECK_DIRECTORY, 'AI_DarkWorld.ydk'))
			
	def test_load_card(self):
		card = yugioh.ygopro.load_card('Blue-Eyes White Dragon')
		self.assertEqual(card.cid, '89631139')
		with self.assertRaises(yugioh.core.database.CardNotFoundException):	
			yugioh.ygopro.load_card('InvalidCardName')
			
	def test_load_deck(self):
		deckpath = yugioh.ygopro.deck_path('AI_Mermail')
		deck = yugioh.ygopro.load_deck(deckpath)
		self.assertEqual(len(deck.main), 40)
		validate_deck(self, deck, 'Mermail Abysslinde', 'Abyss-sphere', 'Atlantean Dragoons')
		with self.assertRaises(IOError):
			yugioh.ygopro.load_deck('InvalidDeckPath')	
		
	def test_findpath(self):
		self.assertEqual(
			yugioh.findpath.find_deck('tests/dummy_deck'),
			os.path.abspath('tests/dummy_deck.ydk'))
		self.assertEqual(
			yugioh.findpath.find_deck('tests/dummy_deck.ydk'),
			os.path.abspath('tests/dummy_deck.ydk'))
		self.assertEqual(
			yugioh.findpath.find_deck('AI_Mermail'),
			yugioh.ygopro.deck_path('AI_Mermail'))
		self.assertEqual(
			yugioh.findpath.find_deck('AI_Mermail.ydk'),
			yugioh.ygopro.deck_path('AI_Mermail'))
			
		with self.assertRaises(IOError):
			yugioh.findpath.find_deck('InvalidDeckPath')

		self.assertEqual(yugioh.findpath.find_format('AI_Mermail'), '.ydk')
		self.assertEqual(yugioh.findpath.find_format('AI_Mermail.ydk'), '.ydk')
		self.assertEqual(yugioh.findpath.find_format('tests/dummy_deck'), '.ydk')
		self.assertEqual(yugioh.findpath.find_format('tests/dummy_deck.ydk'), '.ydk')
		self.assertEqual(yugioh.findpath.find_format('tests/dummy_deck2.txt'), '.txt')
		with self.assertRaises(IOError):
			yugioh.findpath.find_format('tests/dummy_deck2')
		
		
class TestYugiohPrices(unittest.TestCase):
	def test_requests(self):
		bewd = yugioh.ygopro.load_card('Blue-Eyes White Dragon', by='name')
		p = yugioh.yugiohprices.get_price(bewd)
		self.assertIsNotNone(p)
		self.assertGreater(p, 0.0)
		
		pdat = yugioh.yugiohprices.get_price_data('Blue-Eyes White Dragon')
		pdat = yugioh.yugiohprices.get_price_data(bewd)
		pdat = yugioh.yugiohprices.get_price_data(bewd.cid)
		pdat = yugioh.yugiohprices.get_price_data('SDK-001')

		some_card = yugioh.yugiohprices.load_card('SDK-001')
		
		self.assertEqual(bewd, some_card)
		
unittest.main()
