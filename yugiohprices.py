import urllib2
import json

'''
An alternate back end using the Yugiohprices.com public API
'''

def card_by_name(name):
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
