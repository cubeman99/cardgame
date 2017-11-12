from enum import IntEnum



# GameTag
class GameTag(IntEnum):
	"GAME_TAG"

	INVALID			= -1
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
	ENTITY_ID		= 18
	ZONE			= 19
	DAMAGE			= 20
	OWNER			= 21

	DECLARED_ATTACK		= 22
	DECLARED_INTERCEPT	= 23


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
	DECLARE			= 3 # Commit allied units to attacking enemy units, play battle cards
	RESPONSE		= 4 # Choose units to intercept, play battle cards
	COMBAT			= 5 # All combat resolves
	PLAY			= 6 # Play spells and units from your hand

class OptionType(IntEnum):
	INVALID				= 0
	DONE				= 1
	DECLARE				= 2 # Declare an attack/intercept
	FLIP				= 3 # Flip/unflip a unit
	PLAY				= 4 # Play a card


class Type(IntEnum):
	"TAG_TYPE"

	UNKNOWN		= 0
	BOOL		= 1
	NUMBER		= 2
	COUNTER		= 3
	ENTITY		= 4
	PLAYER		= 5
	TEAM		= 6
	ENTITY_DEFINITION = 7
	STRING		= 8

	# Not present at the time
	LOCSTRING = -2




TAG_TYPES = {
	GameTag.CARD_ID: Type.STRING,
	GameTag.NAME: Type.STRING,
	GameTag.TEXT: Type.STRING,

	GameTag.CARD_TYPE: CardType,
	GameTag.ZONE: Zone,
	GameTag.TRIBE: Tribe,
	GameTag.STEP: Step,

	GameTag.CONTROLLER: Type.PLAYER,

	GameTag.DECLARED_ATTACK: Type.ENTITY,
	GameTag.DECLARED_INTERCEPT: Type.ENTITY,
}


if __name__ == "__main__":
	import sys

	enums = {
		k: dict(v.__members__) for k, v in globals().items() if (
			isinstance(v, type) and issubclass(v, IntEnum) and k != "IntEnum"
		)
	}

	def _print_enums(enums, format):
		ret = []
		linefmt = "\t%s = %i,"
		for enum in sorted(enums):
			sorted_pairs = sorted(enums[enum].items(), key=lambda k: k[1])
			lines = "\n".join(linefmt % (name, value) for name, value in sorted_pairs)
			ret.append(format % (enum, lines))
		print("\n\n".join(ret))

	#if len(sys.argv) >= 2:
	#	format = sys.argv[1]
	#else:
	#	format = "--json"

	#if format == "--ts":
	#_print_enums(enums, "export const enum %s {\n%s\n}")

	print(GameTag(GameTag.CONTROLLER).type)
	#elif format == "--cs":
	#_print_enums(enums, "public enum %s {\n%s\n}")
	#else:
	#print(json.dumps(enums, sort_keys=True))



