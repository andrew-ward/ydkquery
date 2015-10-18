import urllib2
import json
import yugioh

'''
A frontend for the yugiohprices api. Gets price data on a card.

May eventually create a more in-depth query library that uses this api.
'''

def get_price_data(card):
	if isinstance(card, yugioh.card.YugiohCard):
		cardname = card.name()
	else:
		cardname = card
	url = 'http://yugiohprices.com/api/get_card_prices/{0}'.format(cardname)
	fl = urllib2.urlopen(url)
	info = json.loads(fl.read())
	fl.close()
	if info['status'] == 'fail':
		raise RuntimeError(info['message'])
	else:
		versions = []
		for version in info['data']:
			set_name = version['name']
			print_tag = version['print_tag']
			rarity = version['rarity']
			price_data = None
			if version['price_data']['status'] == 'success':
				price_info = version['price_data']['data']['prices']
				price_data = yugioh.price.PriceHistory(
					price_info['high'],
					price_info['average'],
					price_info['low'],
					{
						  1 : price_info['shift'],
						  3 : price_info['shift_3'],
						  7 : price_info['shift_7'],
						 21 : price_info['shift_21'],
						 30 : price_info['shift_30'],
						 90 : price_info['shift_90'],
						180 : price_info['shift_180'],
						365 : price_info['shift_365']
					}
				)
			release = yugioh.price.CardVersion(set_name, print_tag, rarity, price_data)
			
			versions.append(release)
		return versions
			
def get_low_price(card):
	data = get_price_data(card)
	return min([version.price.average for version in data])
	
def get_high_price(card):
	return max([version.price.average for version in data])
