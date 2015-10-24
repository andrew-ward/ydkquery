from yugioh import ygopro, decklist

INPUT = {}
OUTPUT = {}

def _importer(fmt):
	def decorate(f):
		INPUT[fmt] = f
		return f
	return decorate
	
def _exporter(fmt):
	def decorate(f):
		OUTPUT[fmt] = f
		return f
	return decorate
	
def conversion(infile, src, dest):
	if src in INPUT:
		deck = INPUT[src](infile)
		if dest in OUTPUT:
			return OUTPUT[dest](deck)
	return None


@_importer('.ydk')
def from_ydk(infile):
	return ygopro.load_deck(infile)

@_importer('.txt')
def from_decklist(infile):
	return decklist.load_deck(infile)

@_exporter('.txt')
def as_decklist(deck):
	return deck.as_decklist()
	
@_exporter('.ydk')
def as_ydk(deck):
	return deck.as_ydk()

@_exporter('.md')
def as_markdown(deck):
	return deck.as_markdown()
