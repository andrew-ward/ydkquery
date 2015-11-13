class CardRetriever(object):
	def find(self, card_key):
		raise NotImplementedError('Abstract Interface')
		
	def all_cards(self):
		raise NotImplementedError('Abstract Interface')
		
