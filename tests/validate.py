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
