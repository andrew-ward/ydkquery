import os
import json

class ConfigurationError(RuntimeError):
	pass

this_directory = os.path.dirname(os.path.realpath(__file__))
config_flname = os.path.join(this_directory, 'config.json')

def update_config(**kwargs):
	config = None
	with open(config_flname) as fl:
		config = json.load(fl)
		for key in kwargs:
			if key in config:
				path = os.path.abspath(kwargs[key])
				if os.path.exists(path):
					config[key] = path
				else:
					raise ConfigurationError('{0} does not exist.'.format(path))

	if config:
		with open(config_flname, 'w') as fl:
			json.dump(config, fl, indent=4)

	
