# YDKquery

A set of Python libraries for reading, writing, and generally working with various decklist formats.

Primarily designed for use in statistical analysis programs involving yugioh cards. It allows you to open .ydk decks as used by YGOPro or DevPro, and manipulate the cards and deck as native python objects.

It also contains several other modules, including yugioh.tcgplayer that loads decks from the tcgplayer.com decklist archives, and yugioh.yugiohprices, which uses the yugiohprices.com web api for pricing information.

There are also some example applications using the library.

`netdeck` is a command line application that will automatically download tcgplayer.com decklists and save it into your ygopro deck folder - allowing you to immediately start playing with the deck, or modifying it as you see fit.

`pricecheck` is a command line application that will calculate the expected price of building a given ydk deck, using price data from yugiohprices.com.

`consistlib` is one of the coolest things here. It is a module that will calculate the probability of drawing certain cards in your opening hand, like several hypergeometric calculators around the internet. Unlike any other I've seen, this probability calculator will allow complicated, arbitrarily complex expressions. Need to know your chance of opening Lonefire + Soulcharge? Easy. Need to know how big of an impact dropping E. Tele from your Ritual Beast deck has on being able to combo off first turn? No problem. It can even calculate complicated things, such as the likelihood that, if you drew one or more Trade-In, you also drew the same number of level 8 targets.

Some additions I plan to add in the future:
	- an alternate backend using the yugioh wikia, instead of ygopro, for card data.
	- a crawler for yugiohtopdecks.com, to make some of that information available programmatically.
	- a more powerful search/query language, so users can search for cards without using sql queries or a `[x for x in database.all() if ...]` form.

Also, for more great yugioh sources, check out yugiohprices.com, yugiohtopdecks.py, and yugiohdeckbuilder.com. They have a lot of stuff similar to what I've made, albeit as a website.
