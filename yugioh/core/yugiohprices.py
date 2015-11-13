import sys, re
from ..core import compat
	
def _api_call_url(request, arg=None):
	url = 'http://yugiohprices.com/api/'+request
	if arg:
		return url + '/'+compat.quote_plus(arg)
	else:
		return url
	
class APIError(RuntimeError):
	pass
	
def _get_price_data(price_data):
	if price_data['status'] == 'success':
		data = price_data['data']['prices']
		return {
			'low' : data['low'],
			'average' : data['average'],
			'high' : data['high'],
			'shift' : {
				1 : data['shift'],
				3 : data['shift_3'],
				7 : data['shift_7'],
				30 : data['shift_30'],
				90 : data['shift_90'],
				180 : data['shift_180'],
				365 : data['shift_365'],
			}
		}
	
def get_card_prices(card_name):
	url = _api_call_url('get_card_prices', card_name)
	result = compat.get_json(url)
	if result['status'] != 'success':
		raise APIError('Got error {} while getting card prices for {}'.format(result['message'], card_name))
	else:
		versions = []
		for version in result['data']:
			versions.append({
				'set_name' : version['name'],
				'print_tag' : version['print_tag'],
				'rarity' : version['rarity'],
				'price_data' : _get_price_data(version['price_data'])
			})
		return versions
		
def price_for_print_tag(print_tag):
	url = _api_call_url('price_for_print_tag', print_tag)
	result = compat.get_json(url)
	if result['status'] != 'success':
		raise APIError('Got error {} while get card prices for {}'.format(result['message'], print_tag))
	else:
		data = result['data']
		return {
			'name' : data['name'],
			'set_name' : data['price_data']['name'],
			'print_tag' : data['price_data']['print_tag'],
			'rarity' : data['price_data']['rarity'],
			'price_data' : _get_price_data(data['price_data']['price_data'])
		}
	
def set_data(set_name):
	url = _api_call_url('set_data', set_name)
	result = compat.get_json(url)
	if result['status'] != 'success':
		raise APIError('Got error {} while getting set data for {}'.format(result['message'], set_name))
	else:
		rdata = result['data']
		info = {
			'rarities' : rdata['rarities'],
			'total_set' : {
				'average' : rdata['average'],
				'high' : rdata['lowest'],
				'low' : rdata['highest'],
			},
			'tcg_booster' : {
				'average' : rdata['tcg_booster_values']['average'],		
				'high' : rdata['tcg_booster_values']['high'],		
				'low' : rdata['tcg_booster_values']['low']
			},
			'cards' : []
		}
		for card in rdata['cards']:
			if len(card['numbers']) > 1:
				raise RuntimeError('huh')
			info['cards'].append({
				'name' : card['name'],
				'set_name' : card['numbers'][0]['name'],
				'print_tag' : card['numbers'][0]['print_tag'],
				'rarity' : card['numbers'][0]['print_tag'],
				'price_data' : _get_price_data(card['numbers'][0]['price_data'])
			})
		return info
				
def card_sets():
	url = _api_call_url('card_sets')
	return compat.get_json(url)

def card_versions(card_name):
	url = _api_call_url('card_versions', card_name)
	result = compat.get_json(url)
	if result['status'] != 'success':
		raise APIError('Got error {} while getting card prices for {}'.format(result['message'], card_name))
	else:
		versions = []
		for card in result['data']:
			versions.append({
				'set_name' : card['name'],
				'print_tag' : card['print_tag'],
				'rarity' : card['rarity']
			})
		return versions

def card_support(card_name):
	url = _api_call_url('card_versions', card_name)
	return compat.get_json(url)
	
