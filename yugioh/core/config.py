"""
this file stores constants that tell the library where to find
certain files on your computer.

:var DATABASE_PATH: path to the ygopro cards.cdb database.

:var BANLIST_PATH: path to the ygopro lflist.conf banlist file

:var DECK_DIRECTORY: path to the ygopro deck directory.
"""
import os
import json
from .reconfigure import ConfigurationError
	
DATABASE_PATH = None
BANLIST_PATH = None
DECK_DIRECTORY = None


this_directory = os.path.dirname(os.path.realpath(__file__))
config_flname = os.path.join(this_directory, 'config.json')
if not os.path.exists(config_flname):
	raise IOError('Cannot locate the yugioh.core configuration file (config.json)')

with open(config_flname) as fl:
	info = json.load(fl)
	
	if os.path.exists(info['DATABASE_PATH']):
		DATABASE_PATH = info['DATABASE_PATH']
	else:
		DATABASE_PATH = None
		
	if os.path.exists(info['BANLIST_PATH']):
		BANLIST_PATH = info['BANLIST_PATH']
	else:
		BANLIST_PATH = None
		
	if os.path.exists(info['DECK_DIRECTORY']):
		DECK_DIRECTORY = info['DECK_DIRECTORY']
	else:
		DECK_DIRECTORY = None

