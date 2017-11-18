
from enums import *

def prop(tag, cast=int):
	def _func(self):
		value = self.tags.get(tag, 0)
		try:
			return cast(value)
		except ValueError:
			# The enum value is most likely just missing
			return value
	return property(_func)


class CardData:
	#def __init__(self):
	#	self.name = "UNKNOWN"
	#	self.type = CardType.INVALID
	#	self.id = 1
	#	self.tags = {}

	def __init__(self, id):
		self.id = id
		self.tags = {}
		self.play_targets = []

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.id

	# Enums
	name	= prop(GameTag.NAME, str)
	text	= prop(GameTag.TEXT, str)
	tribe	= prop(GameTag.TRIBE, Tribe)
	type	= prop(GameTag.CARD_TYPE, CardType)

	# Bools
	emerge		= prop(GameTag.EMERGE, bool)
	aftermath	= prop(GameTag.AFTERMATH, bool)
	wisdom		= prop(GameTag.WISDOM, bool)
	fury		= prop(GameTag.FURY, bool)
	inform		= prop(GameTag.INFORM, bool)
	spy			= prop(GameTag.SPY, bool)
	toxic		= prop(GameTag.TOXIC, bool)

	inspire		= prop(GameTag.INSPIRE, int)

	# Tags
	power		= prop(GameTag.POWER)
	health		= prop(GameTag.HEALTH)
	morale		= prop(GameTag.MORALE)
	supply		= prop(GameTag.SUPPLY)

