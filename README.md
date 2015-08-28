# YDKquery
A set of Python libraries for reading, writing, and generally working with various decklist formats.


devpro.py provides an easy interface for finding and working with cards using the devpro cards.cdb database.

ydk.py provides a convenient front end for opening, manipulating, and saving .ydk files, as used by devpro/ygopro.

tcgplayer.py allows you to load decks off of the yugioh.tcgplayer.com online deck listings, and loads information from your devpro database so you can manipulate and treat them using the same interface from ydk.py.

ToDo
  * If you don't have devpro, use online yugioh database as alternate backend.
  * Unify tcgplayer and ydk Deck objects, so any conversion/loading functions are shared
  * Per User config files for nicknames, tags, etc.
  * Crawl internet for more per-card data - i.e. prices, etc.
  * Proof of concepts
    - Crawl the tcgplayer decklist databases and calculate statistics on card choices
    - Hypergeometric Probability consistency checker
    - Price Checker?
