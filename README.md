# YDKquery

A set of Python libraries for reading, writing, and generally working with various decklist formats.

Primarily designed for use in statistical analysis programs involving yugioh cards. It allows you to open .ydk decks as used by YGOPro or DevPro, and manipulate the cards and deck as native python objects.

It also supports opening decklists from tcgplayer.com, and converting your decks to several different formats.

There are also some example applications using the library.
netdeck.py is a command line application that will automatically download tcgplayer.com decklists and save it into your ygopro deck folder - allowing you to immediately start playing with the deck, or modifying it as you see fit.

consistlib is one of the coolest things here. It is a module that will calculate the probability of drawing certain cards in your opening hand, like several hypergeometric calculators around the internet. Unlike any other I've seen, this probability calculator will allow complicated, arbitrarily complex expressions. Need to know your chance of opening Lonefire + Soulcharge? Easy. Need to know how big of an impact dropping E. Tele from your Ritual Beast deck has on being able to combo off? No problem. It can even calculate the likelihood that, if you drew one or more Trade-In, you also drew the same number of level 8 targets.

Example usage: (see consistency.py for more explanation)

```python
from consistlib import Cardset
from ydklib import ydk

mermail = ydk.ydkopen(ydk.deck_path('AI_Mermail'))

discarder = Cardset(mermail.get([
	'Mermail Abyssleed',
	'Mermail Abyssmegalo',
	'Mermail Abyssteus',
	'Mermail Abyssturge',
	'Mermail Abysspike']))
	
discard_fodder = Cardset(mermail.get([
	'Atlantean Dragoons',
	'Atlantean Marksman',
	'Atlantean Heavy Infantry',
	'Mermail Abyssgunde',
	'Neptabyss the Atlantean Prince']))
	
good_hand = ((discarder > 0) & (discard_fodder > 0))

print( good_hand.probability(mermail, hand_size=5) )
```

For more information on how things work, look at api.txt or the comments in each module.
