from enum import IntEnum
import inspect


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

	TURN_NUMBER		= 24
	TURN_PLAYER		= 25
	STEP_PLAYER		= 26


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
	TOXIC		= 109
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
	ATTACK	= 1
	CHOICE	= 2
	POWER	= 3
	TRIGGER	= 4
	DEATHS	= 5
	PLAY	= 6

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
	CHOOSE				= 5 # Must choose one out of different options

class ChoiceType(IntEnum):
	INVALID		= 0
	GENERAL		= 1
	TARGET		= 2

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

	ENUM		= 9

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
	GameTag.OWNER: Type.PLAYER,

	GameTag.DECLARED_ATTACK: Type.ENTITY,
	GameTag.DECLARED_INTERCEPT: Type.ENTITY,
}



def format_template(template, tag, tag_formatter):
	index = 1
	while True:
		first = "{%s_begin}" %(tag)
		last = "{%s_end}" %(tag)
		try:
			start = template.index(first)
			end = template.index(last, start) + len(last)

			inside = template[start + len(first) : end - len(last)]
			inside = tag_formatter(inside)

			template = template[:start] + inside + template[end:]
			index += 1
		except ValueError:
			break
	return template


def format_items(template, enum):
	result = ""
	max_name_length = 0
	max_value_length = 0
	for name, value in enum.__members__.items():
		max_name_length = max(max_name_length, len(name))
		max_value_length = max(max_value_length, len(str(int(value))))
	for name, value in enum.__members__.items():
		result += template\
			.replace("{item_name}", name)\
			.replace("{item_name:upper}", name.upper())\
			.replace("{item_value}", str(int(value)))\
			.replace("{padding}", " " * (max_name_length - len(name)))\
			.replace("{name_padding}", " " * (max_name_length - len(name)))\
			.replace("{value_padding}", " " * (max_value_length - len(str(int(value)))))
	return result

def format_enums(template, enums):
	result = ""
	for enum in enums:
		result += format_template(template, "items",
			lambda x: format_items(x, enum))\
			.replace("{enum_name}", enum.__name__)\
			.replace("{enum_name:upper}", enum.__name__.upper())
	return result

if __name__ == "__main__":
	import sys
	import re
	import inspect

	enums = {
		k: dict(v.__members__) for k, v in globals().items() if (
			isinstance(v, type) and issubclass(v, IntEnum) and k != "IntEnum"
		)
	}

	# Get a list of all enums.
	enums = []
	for name, obj in inspect.getmembers(sys.modules[__name__]):
		if inspect.isclass(obj) and issubclass(obj, IntEnum) and obj != IntEnum:
			enums.append(obj)

	paths = [
		("codegen/Enums.template.h",   "C:/Workspace/C++/CardGame/src/Client/Enums.h"),
		("codegen/Enums.template.cpp", "C:/Workspace/C++/CardGame/src/Client/Enums.cpp"),
	]

	for template_path, output_path in paths:
		# Read the template file.
		template_file = open(template_path, "r")
		template = template_file.read()
		template_file.close()

		# Format the template file.
		output = format_template(template, "enums",
			lambda x: format_enums(x, enums))

		# Save the formatted result to the output path.
		#print(output)
		output_file = open(output_path, "w")
		output_file.write(output)
		output_file.close()
		print("Saved to %s" %(output_path))

