from enum import IntEnum



# GameTag
class GameTag(IntEnum):
	"GAME_TAG"

	INVALID			= -1
	ZONE			= 0
	POWER			= 1
	HEALTH			= 2
	TRIBE			= 3
	CARD_TYPE		= 4
	REQUIREMENT		= 5
	CONTROLLER		= 6
	RESOURCE_TYPE	= 7
	MORALE			= 8
	SUPPLY			= 9
	BATTLE			= 10
	NAME			= 11
	TEXT			= 12
	TERRITORY		= 13
	MAX_HAND_SIZE	= 14

	STEP			= 15
	NEXT_STEP		= 16

	CARD_ID			= 17

	# Keywords
	MUDDLE		= 100
	AFTERMATH	= 101
	STING		= 102
	CORRUPT		= 103
	INSPIRE		= 104
	EMERGE		= 105
	SPY			= 106
	INFORM		= 107
	CONDUIT		= 108
	TOXIC		= 108
	WISDOM		= 110
	RENEW		= 111
	FURY		= 112
	SWARM		= 113
	HEROIC		= 114

	@property
	def type(self):
		return TAG_TYPES.get(self, Type.NUMBER)

	@property
	def string_type(self):
		return self.type == Type.STRING

STRING_TAGS = [
	GameTag.NAME,
	GameTag.TEXT,
	GameTag.CARD_ID,
]

# Create dictionary of tag names.
# NOTE: Client and Server message IDs do not intersect.
TAG_NAMES = {}
tags = [(getattr(GameTag, attr), attr) for attr in dir(GameTag) if not callable(getattr(GameTag, attr)) and not attr.startswith("__")]
for tag, name in tags:
	TAG_NAMES[tag] = name

# Action Block Type
class BlockType(IntEnum):
	ATTACK = 1
	#JOUST = 2
	POWER = 3
	TRIGGER = 5
	DEATHS = 6
	PLAY = 7
	#FATIGUE = 8
	#RITUAL = 9

# Card Type
class CardType(IntEnum):
	"TAG_CARD_TYPE"

	INVALID		= 0
	GAME		= 1
	PLAYER		= 2
	UNIT		= 3
	SPELL		= 4
	EFFECT		= 5
	TOKEN		= 6

# Resource type
class ResourceType(IntEnum):
	INVALID	= 0
	MORALE	= 1
	SUPPLY	= 2

# Requirement
class Requirement(IntEnum):
	"TAG_REQUIREMENT"

	INVALID				= -1
	REQ_UNIT_TARGET		= 0
	REQ_ALLIED_TARGET	= 1
	REQ_ENEMY_TARGET	= 2
	REQ_				= 3

# Tribe
class Tribe(IntEnum):
	INVALID		= 0
	SLUG		= 1
	OCTOPI		= 2
	MOLE		= 3
	DRAKE		= 4
	EEL			= 5
	AARD		= 6
	PHEASANT	= 7

TRIBES = [
	Tribe.SLUG,
	Tribe.OCTOPI,
	Tribe.MOLE,
	Tribe.DRAKE,
	Tribe.EEL,
	Tribe.AARD,
	Tribe.PHEASANT,
]

# Zone
class Zone(IntEnum):
	INVALID				= 0
	PLAY				= 1
	DECK				= 2
	HAND				= 3
	DISCARD				= 4
	SET_ASIDE			= 5
	REMOVED_FROM_GAME	= 6

# Step
class Step(IntEnum):
	INVALID			= 0
	UNFLIP			= 1 # All flipped units are now unflipped
	RESOURCE		= 2 # Choose to gain either 1 morale or 1 supply
	DECLARE			= 3 # Commit allied units to attacking enemy units
	RESPONSE		= 4 # Chooes units to intercept
	COMBAT			= 5 # All combat resolves




class Type(IntEnum):
	"TAG_TYPE"

	UNKNOWN = 0
	BOOL = 1
	NUMBER = 2
	COUNTER = 3
	ENTITY = 4
	PLAYER = 5
	TEAM = 6
	ENTITY_DEFINITION = 7
	STRING = 8

	# Not present at the time
	LOCSTRING = -2



