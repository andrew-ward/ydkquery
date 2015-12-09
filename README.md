# YDKTools

A set of Python libraries for reading, writing, and generally working with various decklist formats.

Primarily designed for use in statistical analysis programs involving yugioh cards. It allows you to open .ydk decks as used by YGOPro or DevPro, and manipulate the cards and deck as native python objects.

`ygo.consist` is one of the coolest things here. It is a module that will calculate the probability of drawing certain cards in your opening hand, like several hypergeometric calculators around the internet. Unlike any other I've seen, this probability calculator will allow complicated, arbitrarily complex expressions. Need to know your chance of opening Lonefire + Soulcharge? Easy. Need to know how big of an impact dropping E. Tele from your Ritual Beast deck has on being able to combo off first turn? No problem. It can even calculate complicated things, such as the likelihood that, if you drew one or more Trade-In, you also drew the same number of level 8 targets.

The `ydktool.py` application reveals an easy to use interface for doing common tasks with the library. ydktools config allows you to point the library to the files it needs to work, ydktools price allows you to calculate the price it would cost to build a particular deck, ydktools info allows you to search cards and get information about them, and ydktools convert allows you to convert between several different deck formats.
