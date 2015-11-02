import unittest
import os, sys
sys.path.insert(0, '..')

import yugioh
import validate

class TestYGOPro(unittest.TestCase):
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
