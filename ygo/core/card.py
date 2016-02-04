"""Holds datatype for yugioh cards"""
import collections
from . import banlist

class YugiohCard(object):
	banlist_cache = banlist.load_banlists()
	
	def __init__(self, name, text, cid, category, attribute, race, attack, defense, level, lscale, rscale):
		self.__uname = name
		self.__utext = text
		
		self.__category = category
		
		self.__cid = cid		
		
				
		# only exist for monsters
		self.__attribute = attribute if attribute != "N/A" else None
		
		self.__type = race if race != "N/A" else None
		
		self.__level = level
		
		self.__attack = attack
		
		self.__defense = defense
		
		self.__left_scale = lscale
		
		self.__right_scale = rscale

	@property
	def name(self):
		return self.__uname.encode('utf8', 'replace')

	@property
	def uname(self):
		return self.__uname

	@property
	def text(self):
		return self.__utext.encode('utf8', 'replace')

	@property
	def utext(self):
		return self.__utext

	@property
	def category(self):
		return self.__category

	@property
	def cid(self):
		return self.__cid

	@property
	def attribute(self):
		return self.__attribute
	
	@property
	def type(self):
		return self.__type

	@property
	def level(self):
		return self.__level

	@property
	def attack(self):
		return self.__attack

	@property
	def defense(self):
		return self.__defense

	@property
	def lscale(self):
		return self.__lscale

	@property
	def rscale(self):
		return self.__lscale

	def __hash__(self):
		return hash(self.cid)
	def __eq__(self, other):
		return isinstance(other, YugiohCard) and self.cid == other.cid
		
	def __lt__(self, other):
		return self.cid < other.cid
	def __gt__(self, other):
		return self.cid > other.cid
		
	def __repr__(self):
		return 'YugiohCard({0})'.format(str(self))
	def __str__(self):
		return self.name
		
	def is_monster(self):
		return (self.category & 1) > 0

	def is_spell(self):
		return (self.category & 2) > 0

	def is_trap(self):
		return (self.category & 4) > 0

	#def is_tuner(self):
	#	return (self.category & 8) > 0

	def is_normal_monster(self):
		return (self.category & 16) > 0

	def is_effect_monster(self):
		return (self.category & 32) > 0

	def is_fusion(self):
		return (self.category & 64) > 0

	def is_ritual(self):
		return (self.category & 128) > 0

	def is_spirit(self):
		return (self.category & 512) > 0

	def is_union(self):
		return (self.category & 1024) > 0

	def is_gemini(self):
		return (self.category & 2048) > 0

	def is_tuner(self):
		return (self.category & 4096) > 0

	def is_synchro(self):
		return (self.category & 8192) > 0

	def is_quickplay(self):
		return (self.category & 65536) > 0

	def is_continuous(self):
		return (self.category & 131072) > 0

	def is_equip(self):
		return (self.category & 262144) > 0

	def is_field(self):
		return (self.category & 524288) > 0

	def is_counter_trap(self):
		return (self.category & 1048576) > 0

	def is_flip_effect(self):
		return (self.category & 2097152) > 0

	def is_toon(self):
		return (self.category & 4194304) > 0

	def is_xyz(self):
		return (self.category & 8388608) > 0

	def is_pendulum(self):
		return (self.category & 16777216) > 0
		
	def in_extra_deck(self):
		return self.is_xyz() or self.is_fusion() or self.is_synchro()
	def in_main_deck(self):
		return not self.in_extra_deck()

	def allowed(self, banlist='TCG'):
		"""
		:param banlist: what banlist you are asking about.
		:type banlist: string
		:returns: How many copies are allowed on the given banlist.
		:rtype: int"""
		return 3
