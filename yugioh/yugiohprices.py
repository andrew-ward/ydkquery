import urllib, json
import sys
import core, price

class APIError(RuntimeError): pass

'''
A frontend for the yugiohprices api. Gets price data on a card.

May eventually create a more in-depth query library that uses this api.
'''

def get_price_data(card):
	if isinstance(card, core.card.YugiohCard):
		cardname = card.name()
	else:
		cardname = card
		
	cname = urllib.quote_plus(cardname)
	url = 'http://yugiohprices.com/api/get_card_prices/{0}'.format(cname)
	
	fl = urllib.urlopen(url)
	text = fl.read()
	
	info = json.loads(text)
	
	fl.close()
	if info['status'] == 'fail':
		raise APIError(info['message'])
	else:
		versions = []
		for version in info['data']:
			set_name = version['name']
			print_tag = version['print_tag']
			rarity = version['rarity']
			price_data = None
			if version['price_data']['status'] == 'success':
				price_info = version['price_data']['data']['prices']
				price_data = price.PriceHistory(
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
			release = price.CardVersion(set_name, print_tag, rarity, price_data)
			
			versions.append(release)
		return versions
			
def get_low_price(card):
	sys.stderr.write('Deprecated: yugiohprices.get_low_price')
	data = get_price_data(card)
	return min([version.price.average for version in data if version.price])
	
def get_high_price(card):
	sys.stderr.write('Deprecated: yugiohprices.get_low_price')
	data = get_price_data(card)
	return max([version.price.average for version in data if version.price])
	
def get_average_price(card):
	sys.stderr.write('Deprecated: yugiohprices.get_low_price')
	data = get_price_data(card)
	ls = [version.price.average for version in data if version.price]
	return sum(ls) / float(len(ls))
