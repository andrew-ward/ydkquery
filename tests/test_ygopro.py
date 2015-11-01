import unittest
import os, sys
sys.path.insert(0, '..')

import yugioh
import validate

class TestYGOPro(unittest.TestCase):
	
	def test_deck_path(self):
		self.assertEqual(
			yugioh.ygopro.deck_path(),
			yugioh.core.config.DECK_DIRECTORY)
		self.assertEqual(
			yugioh.ygopro.deck_path('AI_Mermail'),
			yugioh.core.config.DECK_DIRECTORY + 'AI_Mermail.ydk')
		self.assertEqual(
			yugioh.ygopro.deck_path('AI_DarkWorld.ydk'),
			yugioh.core.config.DECK_DIRECTORY + 'AI_DarkWorld.ydk')
			
	def test_load_card(self):
		card = yugioh.ygopro.load_card('Blue-Eyes White Dragon')
		self.assertEqual(card.cid, '89631139')
		with self.assertRaises(yugioh.core.database.CardNotFoundException):	
			yugioh.ygopro.load_card('InvalidCardName')
			
	def test_load_deck(self):
		deckpath = yugioh.ygopro.deck_path('AI_Mermail')
		deck = yugioh.ygopro.load_deck(deckpath)
		self.assertEqual(len(deck.main), 40)
		validate.validate_deck(self, deck, 'Mermail Abysslinde', 'Abyss-sphere', 'Atlantean Dragoons')
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
		
		

unittest.main()
