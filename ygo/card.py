"""Holds datatype for yugioh cards"""

class YugiohCard(object):
	
	def __init__(self, name, text, cid, category, attribute, race, attack, defense, level, lscale, rscale):
		self.properties = {
			"uname": name,
			"utext": text,
			"category_code": category,
			"category": CATEGORY(category),
			"id": cid,
			"attribute": attribute,
			"type": race,
			"level": level,
			"attack": attack,
			"defense": defense,
			"scale": lscale
		}

	def clone(self, other):
		assert(isinstance(other, YugiohCard))
		self.properties = {
			"uname": other['name'],
			"utext": other['text'],
			"category": other['category'],
			"id": other['id'],
			"attribute": other['attribute'],
			"type": other['type'],
			"level": other['level'],
			"attack": other['attack'],
			"defense": other['defense'],
			"scale": other['scale']
		}

	def __iter__(self):
		raise TypeError("'{}' object is not iterable".format(self.__class__.__name__))

	def __getitem__(self, key):
		if key == 'name':
			return self.properties['uname']
		elif key == 'text':
			return self.properties['utext']
		elif key in self.properties:
			return self.properties[key]
		else:
			raise KeyError(key)

	def __getattr__(self, key):
		if key == 'name':
			return self.properties['uname']
		elif key == 'text':
			return self.properties['utext']
		elif key in self.properties:
			return self.properties[key]
		else:
			raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__.__name__, key))

	def __hash__(self):
		return hash(self['id'])

	def __eq__(self, other):
		return isinstance(other, YugiohCard) and self['id'] == other['id']
		
	def __lt__(self, other):
		return self['id'] < other['id']
	def __gt__(self, other):
		return self['id'] > other['id']
		
	def __repr__(self):
		return 'YugiohCard({0})'.format(str(self))
	def __str__(self):
		return self.name

		
	def is_monster(self):
		return (self['category_code'] & 1) > 0

	def is_spell(self):
		return (self['category_code'] & 2) > 0

	def is_trap(self):
		return (self['category_code'] & 4) > 0

	#def is_tuner(self):
	#	return (self['category_code'] & 8) > 0

	def is_normal_monster(self):
		return (self['category_code'] & 16) > 0

	def is_effect_monster(self):
		return (self['category_code'] & 32) > 0

	def is_fusion(self):
		return (self['category_code'] & 64) > 0

	def is_ritual(self):
		return (self['category_code'] & 128) > 0

	def is_spirit(self):
		return (self['category_code'] & 512) > 0

	def is_union(self):
		return (self['category_code'] & 1024) > 0

	def is_gemini(self):
		return (self['category_code'] & 2048) > 0

	def is_tuner(self):
		return (self['category_code'] & 4096) > 0

	def is_synchro(self):
		return (self['category_code'] & 8192) > 0

	def is_quickplay(self):
		return (self['category_code'] & 65536) > 0

	def is_continuous(self):
		return (self['category_code'] & 131072) > 0

	def is_equip(self):
		return (self['category_code'] & 262144) > 0

	def is_field(self):
		return (self['category_code'] & 524288) > 0

	def is_counter_trap(self):
		return (self['category_code'] & 1048576) > 0

	def is_flip_effect(self):
		return (self['category_code'] & 2097152) > 0

	def is_toon(self):
		return (self['category_code'] & 4194304) > 0

	def is_xyz(self):
		return (self['category_code'] & 8388608) > 0

	def is_pendulum(self):
		return (self['category_code'] & 16777216) > 0
		
	def in_extra_deck(self):
		return self.is_xyz() or self.is_fusion() or self.is_synchro()
	def in_main_deck(self):
		return not self.in_extra_deck()

	def sort_key(self):
		return (self['category_code'], self['level'], self['attack'], self['defense'], self['id'])

def CATEGORY(number):
	output = []
	if number & (1 << 0):
		output.append('Monster')
	if number & (1 << 1):
		output.append('Spell')
	if number & (1 << 2):
		output.append('Trap')

	if number & (1 << 4):
		output.append('Normal') # monster
	if number & (1 << 5):
		output.append('Effect')

	if number & (1 << 6):
		output.append('Fusion')
	if number & (1 << 7):
		output.append('Ritual')

	if number & (1 << 9):
		output.append('Spirit')
	if number & (1 << 10):
		output.append('Union')
	if number & (1 << 11):
		output.append('Gemini')
	if number & (1 << 12):
		output.append('Tuner')
	if number & (1 << 13):
		output.append('Synchro')
	if number & (1 << 14):
		output.append('Token')
	if number & (1 << 16):
		output.append('Quick-Play')
	if number & (1 << 17):
		output.append('Continuous')
	if number & (1 << 18):
		output.append('Equip')
	if number & (1 << 19):
		output.append('Field')
	if number & (1 << 20):
		output.append('Counter')
	if number & (1 << 21):
		output.append('Flip')
	if number & (1 << 22):
		output.append('Toon')
	if number & (1 << 23):
		output.append('Xyz')
	if number & (1 << 24):
		output.append('Pendulum')
	output.reverse()
	return ' '.join(output)

