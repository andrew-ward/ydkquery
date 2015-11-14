# future proofs the checker for changes to the deck api
def all_cards(deck):
	# return set of cards in your main deck.
	# if you have multiple copies of a card, it only returns one.
	return set(deck.main)
	
def count_all(deck, cards):
	# return the number of each card in the deck
	return deck.main.count_all(cards)
	
def size(deck):
	# returns the number of cards in the deck
	return len(deck.main)
