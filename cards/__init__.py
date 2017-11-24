
from cards.card_data import CardData
from cards.octopi import *
from cards.aard import *
from cards.mole import *
from cards.slug import *
from enums import *
import sys
import inspect
import os
import card_details

class CardScripts:
	pass

class CardDatabase(dict):
	def __init__(self):
		self.initialized = False

	def initialize(self):
		print("Initializing card database")
		self.initialized = True

	def create_card(self, id, card_class):
		#card = card_class()
		card = CardData(card_class.__name__)
		card.id = id
		#card.id = card_class.__name__
		#print("Setting up card %s" %(card.id))

		details = card_details.find(id)
		if details:
			card.tags.update(details.tags)

		card_info = type(card_class.__name__, (card_class, ), {})

		# Create the scripts object
		card.scripts = type(card_class.__name__, (card_class, ), {})

		scriptnames = [
			"update", "emerge", "aftermath", "corrupt", "play", "draw",
			"events"
		]

		# Convert card members to tags.
		members = [attr for attr in dir(card_info) if not callable(getattr(card_info, attr)) and not attr.startswith("__") and not attr == "tags" and not attr in scriptnames]
		for member in members:
			tag = getattr(GameTag, member.upper(), None)
			if tag != None:
				card.tags[tag] = getattr(card_info, member)

		# Setup the card's scripts
		for script in scriptnames:
			actions = getattr(card_info, script, None)
			if actions is None:
				# Set the action by default to avoid runtime hasattr() calls
				setattr(card.scripts, script, [])
			elif not callable(actions):
				if not hasattr(actions, "__iter__"):
					# Ensure the actions are always iterable
					setattr(card.scripts, script, [actions])
					#setattr(card.scripts, script, [actions, ))

		card.tags[GameTag.CARD_ID] = id

		# Step the card's type
		card.tags[GameTag.CARD_TYPE] = getattr(card_info, "type", CardType.INVALID)

		# Set defaults for string tags.
		if not GameTag.TEXT in card.tags.keys():
			card.tags[GameTag.TEXT] = ""
		if not GameTag.NAME in card.tags.keys():
			card.tags[GameTag.NAME] = "UNKNOWN"

		# Decompose some special compound attributes .
		if hasattr(card_info, "stats"):
			card.tags[GameTag.POWER] = card_info.stats[0]
			card.tags[GameTag.HEALTH] = card_info.stats[1]
		if hasattr(card_info, "cost"):
			card.tags[GameTag.MORALE] = card_info.cost[0]
			card.tags[GameTag.SUPPLY] = card_info.cost[1]
		if hasattr(card_info, "targets"):
			card.play_targets = list(card_info.targets)
		if hasattr(card_info, "tags"):
			card.tags.update(card_info.tags)

		# Add the special keyword scripts.
		if card.fury:
			card.scripts.events.append(Attack(SELF, ALL_PLAYERS).on(
				Buff(SELF, "Buff_Fury")))
		if card.muddle:
			card.scripts.events.append(Attack(SELF, ALL_PLAYERS).on(
				Choose(Attack.DEFENDER, ENEMY_HAND).then(Discard(Choose.CHOICE))))
		#if card.inspire:
		#	card.scripts.events.append(Attack(SELF, ALL_PLAYERS).on(GiveMorale(CONTROLLER, INSPIRE(SELF))))
		#if card.spy:
		#	card.scripts.events.append(Attack(SELF, ALL_PLAYERS).on(GiveMorale(OPPONENT, -1)))
		#if card.inform:
		#	card.scripts.events.append(Attack(SELF, ALL_PLAYERS).on(Draw(CONTROLLER)))
		if hasattr(card_info, "heroic"):
			card.scripts.update.append((Count(ALLIED_UNITS - SELF) == 0) & Refresh(SELF, buff=card_info.heroic))
		if hasattr(card_info, "swarm"):
			card.scripts.update.append((Count(ALLIED_UNITS - SELF) >= 3) & Refresh(SELF, buff=card_info.swarm))

		# Set choose one cards
		if hasattr(card_info, "choose"):
			card.choose_cards = card_info.choose[:]
		else:
			card.choose_cards = []


		db[id] = card
		#print(card.name)



if "db" not in globals():
	card_details.initialize()
	db = CardDatabase()

	# Load all cards into the database.
	modules = ["aard", "octopi", "mole", "slug"]
	for module in modules:
		for name, obj in inspect.getmembers(sys.modules["cards.%s" %(module)]):
			#if inspect.isclass(obj):
			#if os.path.basename(inspect.getsourcefile(obj)) == "%s.py" %(module):
			#if inspect.isclass(obj):
			#	print("%s %s %s %s" %(name, obj.__name__, inspect.isclass(obj), os.path.basename(inspect.getsourcefile(obj))))
			if inspect.isclass(obj):
				obj_module = os.path.basename(inspect.getsourcefile(obj))
				if obj_module == "%s.py" %(module) or obj.__name__ == "Buff":
					db.create_card(name, obj)
				#db[obj.__name__] = obj()
				#db[obj.__name__].id = obj.__name__
				#db[obj.__name__].setup()

				#print(obj.__name__)
				#print(os.path.basename(inspect.getsourcefile(obj)))

	#print(dict([(name, cls) for name, cls in octopi.__dict__.items() if isinstance(cls, type)]))

