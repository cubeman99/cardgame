
import inspect
import sys
import cards.aard
import cards.octopi
import cards.mole
import cards.slug
import cards.eel
import os
from enums import *
from enum import IntEnum


cards = []

class CardDetails:
	def __init__(self, id, tags):
		self.id = id
		self.tags = tags

def create_card(name, card_class):
	print(name, card_class)

	card_info = type(card_class.__name__, (card_class, ), {})

	scriptnames = [
		"update", "emerge", "aftermath", "corrupt", "play", "draw",
		"events"
	]

	tags = {}

	# Convert card members to tags.
	members = [attr for attr in dir(card_info) if not callable(getattr(card_info, attr)) and not attr.startswith("__") and not attr == "tags" and not attr in scriptnames]
	for member in members:
		tag = getattr(GameTag, member.upper(), None)
		if tag != None:
			#print("  * %s = %s" %(tag, getattr(card_info, member)))
			tags[tag] = getattr(card_info, member)

	# Decompose some special compound attributes .
	if hasattr(card_info, "stats"):
		tags[GameTag.POWER] = card_info.stats[0]
		tags[GameTag.HEALTH] = card_info.stats[1]
	if hasattr(card_info, "cost"):
		tags[GameTag.MORALE] = card_info.cost[0]
		tags[GameTag.SUPPLY] = card_info.cost[1]

	if hasattr(card_info, "aftermath"):
		tags[GameTag.AFTERMATH] = 1
	if hasattr(card_info, "emerge"):
		tags[GameTag.EMERGE] = 1
	if hasattr(card_info, "corrupt"):
		tags[GameTag.CORRUPT] = 1

	tags[GameTag.CARD_TYPE] = getattr(card_info, "type", CardType.INVALID)

	if hasattr(card_info, "tags"):
		tags.update(card_info.tags)

	for key, value in tags.items():
		print("  * %s = %s" %(key, value))

	return CardDetails(name, tags)

# Load all cards into the database.
modules = ["aard", "octopi", "mole", "slug", "eel", "drake", "pheasant"]
for module in modules:
	for name, obj in inspect.getmembers(sys.modules["cards.%s" %(module)]):
		#if inspect.isclass(obj):
		#if os.path.basename(inspect.getsourcefile(obj)) == "%s.py" %(module):
		#if inspect.isclass(obj):
		#	print("%s %s %s %s" %(name, obj.__name__, inspect.isclass(obj), os.path.basename(inspect.getsourcefile(obj))))
		if inspect.isclass(obj):
			obj_module = os.path.basename(inspect.getsourcefile(obj))
			if name != "Buff" and (obj_module == "%s.py" %(module) or \
				obj.__name__ == "Buff"):
				cards.append(create_card(name, obj))



# Save cards to file
with open("card_details.json", "w") as json_file:
	json_file.write('{\n')
	for i in range(0, len(cards)):
		card = cards[i]
		json_file.write('\t"%s": {\n' %(card.id))
		items = list(card.tags.items())
		for j in range(0, len(items)):
			key, value = items[j]
			if isinstance(value, str):
				value = '"' + value + '"'
			if isinstance(value, bool):
				value = int(value)
			if isinstance(value, IntEnum):
				value = '"%s"' %(value.name.lower())
			comma = "," if j + 1 < len(items) else ""
			json_file.write('\t\t"%s": %s%s\n' %(key.name.lower(), value, comma))
		comma = "," if i + 1 < len(cards) else ""
		json_file.write('\t}%s\n' %(comma))
	json_file.write('}\n')

with open("card_details.json", "r") as json_file:
	print(json_file.read())


