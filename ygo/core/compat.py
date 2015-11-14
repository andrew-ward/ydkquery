import sys
import json
import locale

locale.setlocale(locale.LC_ALL, '')

if sys.version_info.major == 2:
	from urllib import urlopen, quote_plus
elif sys.version_info.major == 3:
	from urllib.request import urlopen
	from urllib.parse import quote_plus
else:
	svi = sys.version_info
	raise NotImplementedError('Python version {0}.{1}.{3} not supported'.format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro))


def get_html(path):
	fl = urlopen(path)
	if sys.version_info.major == 3:
		text = fl.readall().decode('utf-8')
	else:
		text = fl.read()
	fl.close()
	return text

def get_json(path):
	text = get_html(path)
	return json.loads(text)

def format_money(usd):
	if usd == None:
		return '$?.??'
	else:
		return locale.currency(usd)
