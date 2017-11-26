
from .card_data import CardData
from .octopi import *
from .aard import *
from .mole import *
from .slug import *
from .eel import *
from .drake import *
from .pheasant import *
from ..enums import *
import sys
import inspect
import os
from .. import card_details

class CardScripts:
	pass

class CardDatabase(dict):
	def __init__(self):
		self.initialized = False

	def initialize(self):
		print("Initializing card database")
		self.initialized = True

		card_details.initialize()

		modules = ["aard", "octopi", "mole", "slug", "eel", "drake", "pheasant"]
		for i in range(0, len(modules)):
			modules[i] = modules[i] + ".py"

		all_globals = globals().copy().items()
		for name, obj in all_globals:
			if inspect.isclass(obj):
				obj_module = os.path.basename(inspect.getsourcefile(obj))
				if obj_module in modules or obj.__name__ == "Buff":
					self.create_card(name, obj)
					#print(name)

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
			"update", "emerge", "aftermath", "corrupt", "corrupt_fail",
			"play", "draw", "events"
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
			card.scripts.events.append(
				Attack(SELF, ALL_PLAYERS).on(Buff(SELF, "Buff_Fury")))
		if card.muddle:
			card.scripts.events.append(
				Attack(SELF, ALL_PLAYERS).on(
					ChooseAndDiscard(Attack.DEFENDER)))
		if card.toxic:
			card.scripts.events.append(
				Attack(SELF, ALL_UNITS).after(
					IfThen(Alive(Attack.DEFENDER), Toxic(Attack.DEFENDER))))
		if hasattr(card_info, "heroic"):
			card.scripts.update.append(
				IfThen(Count(ALLIED_UNITS - SELF) == 0,
					Refresh(SELF, buff=card_info.heroic)))
		if hasattr(card_info, "swarm"):
			card.scripts.update.append(
				IfThen(Count(ALLIED_UNITS - SELF) >= 3,
					Refresh(SELF, buff=card_info.swarm)))
		if hasattr(card_info, "wisdom"):
			card.scripts.emerge.append(
				IfThen(Count(ALLIED_HAND) >= 4,
					Buff(SELF, card_info.wisdom)))

		# Set choose one cards
		if hasattr(card_info, "choose"):
			card.choose_cards = card_info.choose[:]
		else:
			card.choose_cards = []


		db[id] = card
		#print(card.name)



if "db" not in globals():
	db = CardDatabase()


