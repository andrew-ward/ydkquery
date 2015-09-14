import urllib2
import json

'''
An alternate back end using the Yugiohprices.com public API

Currently does not correctly get category and pendulum scales
Also does not support querying by card id, or getting the card id of a card

In all, just bad. Use something else. The idea is sound, but until I
get up the nerve to scrap and parse yugioh.wikia.com, ygopro is the only
real card database available.
'''

def find(name):
	'''[Unstable] Given a name, return the YugiohCard with that name using yugiohprices.com for card data'''
	response = urllib2.urlopen("http://yugiohprices.com/api/card_data/{0}".format(name))
	html = response.read()
	response.close()
	info = json.loads(html)
	if info['status'] != 'success':
		raise RuntimeError('YugiohPrices.com API response was invalid.')
	data = info['data']
	
	name = data['name']
	text = data['text']
	attribute = data['family'].capitalize()
	attack = data['atk']
	defense = data['def']
	level = data['level']
	race = data['type'].split('/')[0].strip()
	category = 'unknown'
	cid = 'unknown'
		
	return ygocard.YugiohCard(name, text, 'unknown', 'unknown', attribute, race, attack, defense, level, 'unknown', 'unknown')
