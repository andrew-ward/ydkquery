from consistlib import Cardset
from api import ygopro
from api import yugioh

"""
A demonstration of how to use consistlib to calculate the consistency of
your opening hand in a deck. See the comments in consistlib.describe
for more implementation details.

"""

if __name__ == '__main__':
	# load the deck you want to work with using ydkopen
	# ydk.deck_path automatically converts deck names to a path
	# to a deck in your ygopro/deck/ folder.
	# deck_path depends on you having ydklib.conf set up
	# to point to the ygopro directory
	mermail = ygopro.load_deck(ygopro.deck_path('AI_Mermail'))

	# create sets of cards. These are treated as variables, that calculate
	# how many of any of these cards are in a hand.
	discarder = Cardset(mermail.main.get_all([
		'Mermail Abyssleed',
		'Mermail Abyssmegalo',
		'Mermail Abyssteus',
		'Mermail Abyssturge',
		'Mermail Abysspike']))
	discard_fodder = Cardset(mermail.main.get_all([
		'Atlantean Dragoons',
		'Atlantean Marksman',
		'Atlantean Heavy Infantry',
		'Mermail Abyssgunde',
		'Neptabyss the Atlantean Prince']))
		
	# create an expression that determines if a hand is good
	# this one is asking the probability of opening
	# with at least one of each of the two sets
	# Note: you must have a Cardset, or an expression containing a Cardset,
	#          on the left hand side of every operator.
	#          i.e. (0 < discarder) would fail.
	good_hand = ((discarder > 0) & (discard_fodder > 0))

	# other supported operations include
	# or(|) which is true if any of the sub terms are true
	# less than(<) and equal(==) which do what their names would suggest
	# and add(+), which adds the number of occurences of several cardsets.
	# i.e. ((discarder + discard_fodder) > 2) is the same as above.

	# calculate the chance of opening with a hand that
	# fulfills the above requirements
	# hand_size is optional, by default it's 5.
	print( good_hand.probability(mermail, hand_size=5) )
