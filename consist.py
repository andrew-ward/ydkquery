import mapquery
import db
import time
import itertools


command = 'any ( attack >= 1500 )'

def consistency(ydk, evalfun):
	hands = itertools.combinations(ydk, 5)
	good = 0
	total = 0
	start = time.time()
	for hand in hands:
		if evalfun(hand):
			good += 1
		total += 1
		if (time.time() - start) > 3:
			print('looked at {0} hands'.format(total))
			start = time.time()
	return float(good) / total
		

fun = mapquery.Evaluator.ofString(command)

hand = [
	db.card_by_name('Satellarknight Deneb'),
	db.card_by_name('Mind Crush'),
	db.card_by_name('Satellarknight Vega'),
	db.card_by_name('Pot of Duality'),
	db.card_by_name('Mirror Force')
]

for card in hand:
	print(card)

print(fun(hand))
