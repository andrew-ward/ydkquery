# YQL

workshop.yql is the module that implements the Ygo Query Language, a simple tool for selecting cards.



Yql can also be used directly from YgoproPercyDatabase

    import workshop
    ygopro = workshop.deck.YgoproPercyDatabase("path/to/cards.cdb")
    deck = ygopro.open_deck("path/to/deck.ydk")

    # compiles text to a YqlQuery object
    query = workshop.yql.compile_yql("level 7 synchro")

    # apply the query to a sequence of cards
    # returns an iterator of all the cards that matched the query
    selected = query.filter(deck['extra'])

    # alternately, YgoproPercyDatabase has yql available
    # if "cards" parameter is not given, assumes all cards
    selected = ygopro.yql("level 7 synchro", cards=deck['extra'])
    
Yql has a number of variables available. There are a number that evaluate to the value from the Card's dictionary. These are name, text, category, level, scale, attack, defense, type, and attribute.

There are also a number of variables that evaluate to true or false, depending on whether the card has the given trait. These are monster, spell, trap, normal, effect, fusion, xyz, synchro, ritual, union, spirit, gemini, toon, tuner, flip, pendulum, continuous, equip, quick-play, counter, and field.

Double-Quoted strings and numbers also evaluate to their respected values. Any words (alphabetic characters, no spaces) also evaluate to strings. For example,

    type = "Fiend"

and

    type = Fiend

mean the same thing. Boolean values true and false can also be used as literals.


Variables can be compared with binary operators. "=", "<", and ">" do what you would expect. You can also use the match operator "~" to compare strings. It will return true if the regex represented by the right-hand operand appears anywhere within the left-hand operand. For example,

    "Elemental HERO Shadow Mist" ~ "HERO"

returns true.

By default, if two variablers are placed next together, it will be assumed that you meant to compare them with match or equals, as appropriate for the operand types. For example,

    type Fiend

will see two strings next to each other, and implicitly attempt to match them. If this wasn't what you meant, you could instead use

    type and Fiend

which would simply evaluate them both and return true if neither of them were empty.

    level 7

behaves in much the same way, but will use equality instead of matching.

These constraint expressions can be combined with "and" and "or". However, by default constraint expressions are assumed to be combined with "and". For example

    name HERO fusion level > 6

is a perfectly valid query that is functionally identical to

    name ~ "HERO" and fusion and level > 6
