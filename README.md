# YDKquery

A set of Python libraries for reading, writing, and generally working with various decklist formats.

Primarily designed for use in statistical analysis programs involving yugioh cards. It allows you to open .ydk decks as used by YGOPro or DevPro, and manipulate the cards and deck as native python objects.

It also contains several other modules, including yugioh.yugiohprices, which uses the yugiohprices.com web api for pricing information, and yugioh.decklist that allows reading and writing to human readable text deck lists, following a loose format that most people naturally use.

`yugioh.consist` is one of the coolest things here. It is a module that will calculate the probability of drawing certain cards in your opening hand, like several hypergeometric calculators around the internet. Unlike any other I've seen, this probability calculator will allow complicated, arbitrarily complex expressions. Need to know your chance of opening Lonefire + Soulcharge? Easy. Need to know how big of an impact dropping E. Tele from your Ritual Beast deck has on being able to combo off first turn? No problem. It can even calculate complicated things, such as the likelihood that, if you drew one or more Trade-In, you also drew the same number of level 8 targets.

There are also some example applications using the library.

`pricecheck` is a command line application that will calculate the expected price of building a given ydk deck, using price data from yugiohprices.com.

`ygo-convert` is a command line application that converts deck lists from one format to another. Supports converting to and from ydk, text, and markdown. Also will automatically look for decks in the ygopro deck folder, allowing you to use the raw deck name, instead of a full path.

Some additions I plan to add in the future:
	- an alternate backend using the yugioh wikia, instead of ygopro, for card data.
	- a crawler for yugiohtopdecks.com, to make some of that information available programmatically.
	- a more powerful search/query language, so users can search for cards without using sql queries or a `[x for x in database.all() if ...]` form.

Also, for more great yugioh sources, check out yugiohprices.com, yugiohtopdecks.py, and yugiohdeckbuilder.com. They have a lot of stuff similar to what I've made, albeit as a website.
