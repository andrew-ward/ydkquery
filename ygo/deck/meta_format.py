from . import ydk, ygojson, text
import os

def detect_filename_format(path):
	filename, extension = os.path.splitext(path)
	if extension == '.ydk':
		return ydk
	elif extension == '.json':
		return ygojson
	else:
		return text

def detect_text_format(path):
	if text.startswith('{'):
		return ygojson
	elif text.startswith('#') or text[0].isdigit():
		return ydk
	else:
		return text

def open_deck(path, card_source):
	return detect_filename_format(path).open_deck(path, card_source)

def load(text, card_source):
	return detect_text_format(text).load(text, card_source)

def dump(deck, fmt='text'):
	if fmt == 'ydk':
		return ydk.dump(deck)
	elif fmt == 'json':
		return ygojson.dump(deck)
	else:
		return text.dump(deck)
