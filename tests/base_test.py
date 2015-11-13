import unittest
import os, sys

class Test(unittest.TestCase):
	def validate_card(self, card, **kwargs):
		from yugioh.core import enum
		from yugioh.core.card import YugiohCard
		self.assertIsInstance(card, YugiohCard)
		self.assertIsNotNone(card)
		self.assertIsNotNone(card.name)
		self.assertIsNotNone(card.text)
		
		self.assertIsNotNone(card.category)
		self.assertIn(card.category, enum.MAGIC_NUMBERS['category'])
		
		self.assertIsNotNone(card.cid)
		self.assertTrue(card.cid.isdigit())

		if card.is_monster():
			self.assertIsNotNone(card.attribute)
			self.assertIn(card.attribute, enum.MAGIC_NUMBERS['attribute'])	
				
			self.assertIsNotNone(card.type)
			self.assertIn(card.type, enum.MAGIC_NUMBERS['type'])
			
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
		self.assertIn(card.allowed(), (0,1,2,3))
		
		for attrib, exp_val in kwargs.items():
			self.assertEqual(card[attrib], exp_val)
			
	def validate_deck(self, deck, *expected_cards):
		for card in deck.main:
			self.validate_card(card)
		for card in deck.side:
			self.validate_card(card)
		for card in deck.extra:
			self.validate_card(card)
			
		all_cards = deck.all()
		self.assertEqual(len(all_cards), len(deck.main) + len(deck.side) + len(deck.extra))
					
		self.assertIsNotNone(deck.author)
		self.assertIsNotNone(deck.name)
		
		self.assertEqual(deck.main.size(), len(deck.main.enumerate()))
		
		total = 0
		for card in deck.main:
			total += deck.main.count(card)
		self.assertEqual(total, deck.main.size())

		for cardname in expected_cards:
			self.assertIsNotNone(deck.all().get(cardname))


	def assertPath(self, path):
		try:
			self.assertIsNotNone(path)
			self.assertTrue(os.path.exists(path))
		except AssertionError:
			raise AssertionError('{0} is not an existing path.'.format(path))

