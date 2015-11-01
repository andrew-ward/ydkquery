import sys
"""
runs some tests. You can look in here for advice on how to use features
of the library, but mostly you can ignore it. The tests are not comprehensive.
"""

test_dict = {}

def invalid_test():
	print('Invalid Test')

def test(name):
	def decorate(f):
		test_dict[name] = f
		return f
	return decorate

@test('all')
def run_all_tests():
	for test in test_dict:
		if test != 'all':
			print('==[{0}]=='.format(test))
			test_dict[test]()
			print('')

@test('hello')
def hello_world():
	print('   Hello, World!')

@test('ygopro')
def load_decklist():
	from yugioh import ygopro
	darkworld = ygopro.deck_path('AI_DarkWorld')
	print('   loading {0}'.format(darkworld))
	deck = ygopro.load_deck(darkworld)
	print('  length={0}'.format(len(deck)))

@test('ydk')
def print_ydk_format():
	from yugioh import ygopro
	darkworld = ygopro.deck_path('AI_DarkWorld')
	deck = ygopro.load_deck(darkworld)
	print(deck.as_ydk())
	
@test('markdown')
def print_markdown_decklist():
	from yugioh import ygopro
	darkworld = ygopro.deck_path('AI_DarkWorld')
	deck = ygopro.load_deck(darkworld)
	print(deck.as_markdown())
	
@test('decklist')
def print_markdown_decklist():
	from yugioh import ygopro
	darkworld = ygopro.deck_path('AI_DarkWorld')
	deck = ygopro.load_deck(darkworld)
	print(deck.as_decklist())
	
@test('search')
def ygopro_load_card(cardname = "Blue-Eyes White Dragon"):
	from yugioh import ygopro
	card = ygopro.load_card(cardname)
	print('  card <{0}>'.format(card))
	print('    amount allowed {0}'.format(card.allowed()))
	print('    card id {0}'.format(card.cid))

	
@test('yugiohprices')
def get_yugiohprices_data(cardname = "Gradius"):
	from yugioh import yugiohprices
	pdat = yugiohprices.get_price_data(cardname)
	print('  price data: {0}'.format(pdat))
	
@test('konami_banlist')
def get_banlist():
	from yugioh.core import konami_banlist
	bl = konami_banlist.load_tcg_banlist()
	print bl

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Please name a test to run. Options are {0}'.format(', '.join(test_dict.keys())))
	else:
		test_dict.get(sys.argv[1], invalid_test)(*sys.argv[2:])
