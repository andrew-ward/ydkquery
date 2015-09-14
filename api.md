consistency.py: An example on how to use consistlib.
	
netdeck.py: A command line application that downloads tcgplayer.com decks and saves them to your ygopro decks folder.
	
ydklib/
	paths.py: reads the ydklib.conf file and gives you paths to your ygopro folder.
		database()
			returns path to cards.cdb in ygopro.
			
		decks()
			returns path to your ygopro decks.
			
		ygopro()
			returns path to your ygopro directory
			
			
	ydk.py: Handles the loading and saving of .ydk formatted decks.
		deck_path(deck_name)
			Takes a deck name, as the ygopro deck editor uses, and returns the absolute path to that deck.
			
		ydkopen(path)
			Opens a .ydk deck and gives you a YugiohDeck of its contents.
			
		ydksave(deck, fl)
			Converts a deck into .ydk format, and saves it to the file fl.
			
			
	tcgplayer.py: Handles the loading of tcgplayer.com decklists.
		tcgopen(url)
			Scrapes the url and converts the decklist found there into a YugiohDeck.

		tcgsave(deck, fl)
			Does nothing.
		
		
	ygopro.py: The module that handles interfacing with the ygopro database and searching it for cards.
		all_cards()
			return list of every card in the database, excluding anime-only cards.
		
		database()
			returns a new database instance to use to search for cards.
	
		class YGOProDatabase: handles querying the database.
		
			all_cards(anime=False)
				Get every card in the database as a list. If anime is true, get anime-only cards too.
				
			find(arg, by='id')
				Find a card in the database. Returns a YGOProCard as below.
				id: find the card with the given card id
				name: find the card with the given name. If multiple match, return the first. Supports using SQL patterns.
				
			find_all(args, by='id')
				As find, but a list of args.
				
			search(pattern, by='name')
				Gets multiple cards that fulfill the pattern. Returns multiple YGOProCards as below.
				name: Use SQL patterns to find all cards that match.
				text: Use SQL patterns to find all cards that match.
				 sql: Use arbitrary sql expressions to find cards. Only for people who know what they're doing.
				
			get_new_id()
				Returns a new, previously unused card id.
				
			open()
				opens a new connection to the database. rarely neccesary.
				
			close()
				close your current connection to the database				       
				       
		class YGOProCard: an extension of YugiohCard with ygopro specific data. Most of the extra data is irrelevant, but it is listed here anyway.
			alias()
				A database row that deals with cards with multiple artworks.
				
			availability()
				Get the banlist the card is playable on (TCG, OCG, TCG/OCG, Anime)
				
			setcode()
				Special number that marks what Archtype the card belongs to. Alternately, you could just look at the name.
			
			
			
	ygocard.py: Holds the data structures that make up yugioh cards and decks.	
		YugiohCard: never try to construct one of these - let the database or ydkopen/tcgopen do it for you.
			attack()
				returns the attack of the monster as an integer. If the card is not a monster, returns 0. If the monster has ? attack, returns a negative number.
				
			attribute()
				returns the attribute of the monster as a string. Non-monsters return "N/A"

			category()
				returns a text string that says what kind of card it is (i.e. Normal Spell, Counter Trap, Synchro Monster, etc).
	
			cid()
				returns the card id of the card as an integer.
		
			defense()
				returns the defense of the monster as an integer. If the card is not a monster, returns 0. If the monster has ? defense, returns a negative number.
		
			is_effect_monster()
				returns True if card is a monster with an effect
		
			is_monster()
				returns True if card is a monster card
		
			is_normal_monster()
				returns True if card is a Normal monster. This is not the same as a monster without an effect.

			is_pendulum()
				returns True if card is a pendulum monster card

			is_ritual_monster()
				returns True if card is a Ritual Monster

			is_spell()
				returns True if card is a spell card
	
			is_synchro()
				returns True if card is a synchro monster card
			
			is_trap()
				returns True if card is a trap card
			
			is_tuner()
				returns True if card is a tuner
			
			is_xyz()
				returns True if card is an xyz monster card
			
			left_scale()
				returns the left pendulum scale of the monster as a string. Non-pendulums return None
			
			level()
				returns the level of the monster as an integer. Non-monsters return 0
			
			monster_type()
				returns the type of the monster as a string. Non-monsters return "N/A"
			
			name()
				returns the full name of the card.
			
			right_scale()
				returns the right pendulum scale of the monster as a string. Non-pendulums return None
			
			text()
				returns the text on the card.
				
		YugiohDeck: holds a main deck, side deck, and extra deck of yugioh cards.
			add_card(card, group='main')
				add a card to the deck. "group" specifies whether to add it to main, side, or extra.
			
			add_cards(cards, group='main')
				add multiple cards to the deck. "group" specifies whether to add it to main, side, or extra.
			
			as_decklist()
				convert the deck to a simple, easy-to-read decklist without the formatting markdown has
			
			as_markdown()
				convert the deck to a decklist string formatted for reddit-style markdown
			
			as_ydk()
				convert the deck to a .ydk formatted string.
				return how many instances of that card are in the deck. "group" specifies whether to add it to main, side, or extra.
			
			count_all(cards, group='main')
				Count multiple cards at once. "group" specifies whether to add it to main, side, or extra.
			
			find(predicate, group='main')
				get a set of all cards for which the function "predicate" is true. "group" specifies whether to add it to main, side, or extra.
			
			get(name, group='main')
				get the card named from the deck. "group" specifies whether to add it to main, side, or extra.
			
			get_all(names, group='main')
				get all the cards named from the deck as a set. "group" specifies whether to add it to main, side, or extra.
			
			main()
				returns a set of all the cards in the main deck. This ignores duplicates.
			
			extra()
				returns a set of all the cards in the extra deck. This ignores duplicates.
			
			side()
				returns a set of all the cards in the side deck. This ignores duplicates.
			
			size(group='main')
				return how many cards are in the deck. "group" specifies whether to add it to main, side, or extra.
	
