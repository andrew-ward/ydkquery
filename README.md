# YDKTools

A set of Python libraries for reading, writing, and generally working with various decklist formats.

Primarily designed for use in statistical analysis programs involving yugioh cards. It allows you to open .ydk decks as used by YGOPro or DevPro, and manipulate the cards and deck as native python objects.

`ydktools.py` is a command line application that lets you query cards, request price information, and convert decklists to various formats. For example, `ydktools.py -d "deckname" -p` will display detailed price information about the deck. `ydktools.py -q /hieratic/` will get you a list of all cards with "Hieratic" in their name, and `ydktools.py -d deckname -o txt` will write out a text decklist that you can copy and paste.

(price information available through free yugiohprices.com api)

Supports reading and writing from .ydk files, and lets you search cards using the ygopro database.

`yql` is a module that lets you query cards using an expression based language. Currently unreliable and undocumented, but its getting better.

`ygo.consist` is a module that will calculate the probability of drawing certain cards in your opening hand, like several hypergeometric calculators around the internet. Unlike any other I've seen, this probability calculator will allow complicated, arbitrarily complex expressions. Need to know your chance of opening Lonefire + Soulcharge? Easy. Need to know how big of an impact dropping E. Tele from your Ritual Beast deck has on being able to combo off first turn? No problem. It can even calculate complicated things, such as the likelihood that, if you drew one or more Trade-In, you also drew the same number of level 8 targets.

