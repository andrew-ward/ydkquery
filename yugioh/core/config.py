import json, os
"""
This module handles finding the ygopro directory.

Since the directory could be anywhere, and there is no one standard
place for it, this uses a configuration file in the same folder as
the package, called ydklib.conf. There should be an example ydklib.conf
supplied with the package. It needs to be edited so that
ygopro is pointing at the correct directory. The other variables most
likely won't need adjusting.

"""

# this part looks for the conf file and initializes PATH_MAP
# accordingly if found.
PATH_MAP = {}

this_directory = os.path.dirname(os.path.realpath(__file__))
if 'ydklib.conf' in os.listdir(this_directory):
	with open(os.path.join(this_directory, 'ydklib.conf')) as fl:
		confmap = json.loads(fl.read())
		if 'paths' not in confmap:
			raise RuntimeError('Incorrectly formatted ydklib.conf. It should be a json file with at least one object named "paths", containing keys "ygopro", "cards", and "decks", in your {0} directory'.format(this_directory))
		ygpath = confmap['paths']['ygopro']
		
		PATH_MAP['ygopro'] = ygpath
		
		if confmap['paths']['cards'] != None:
			PATH_MAP['database'] = os.path.join(ygpath, confmap['paths']['cards'])
		else:
			PATH_MAP['database'] = os.path.join(ygpath, 'cards.cdb')
			
		if confmap['paths']['decks'] != None:
			PATH_MAP['decks'] = os.path.join(ygpath, confmap['paths']['decks'])
		else:
			PATH_MAP['decks'] = os.path.join(ygpath, 'deck/')

	
# these are the potentially useful functions. Each returns the path to
# the appropriate aspect of ygopro.
def ygopro():
	""" get path to ygopro directory as set in ydklib.conf """
	if 'ygopro' in PATH_MAP:	
		return PATH_MAP['ygopro']
	else:
		raise RuntimeError('Please set "ygopro" in your ydklib.conf. It should be in "{0}".'.format(this_directory))
	
def database():
	""" get path to cards.cdb database as set in ydklib.conf """
	if 'database' in PATH_MAP:	
		return PATH_MAP['database']
	else:
		raise RuntimeError('Please set "ygopro" and "cards" in your ydklib.conf. It should be in "{0}".'.format(this_directory))

def decks():
	""" get path to ygopro deck directory as set in ydklib.conf """
	if 'decks' in PATH_MAP:	
		return PATH_MAP['decks']
	else:
		raise RuntimeError('Please set "ygopro" and "decks" in your ydklib.conf. It should be in "{0}".'.format(this_directory))
