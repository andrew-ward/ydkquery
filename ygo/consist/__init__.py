"""
A module that provides functions for calculating the consistency of a yugioh deck.
"""

from .describe import Cardset

def probability(expr, deck, hand_size=5):
	return expr.probability(deck, hand_size)
