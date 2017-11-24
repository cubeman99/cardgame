from enums import GameTag
#from . import enums
import logging


class Manager(object):
	"""Maps tags to attributes of an entity"""

	def __init__(self, obj):
		self.obj = obj
		self.observers = []

	def __getitem__(self, tag):
		"""Get the value of a tag. Raises KeyError if the tag is not defined """
		if self.map.get(tag, None) != None:
			return getattr(self.obj, self.map[tag], 0)
		elif self.obj.data != None:
			return self.obj.data.tags[tag]
		else:
			return None

	def get(self, tag, default=None):
		"""Get the value of a tag or return the default if it is not defined"""
		if tag in self.map:
			return self[tag]
		elif self.obj.data != None:
			return self.obj.data.tags.get(tag, default)
		else:
			return default

	def __setitem__(self, tag, value):
		"""Set the value of a tag"""
		try:
			setattr(self.obj, self.map[tag], value)
		except AttributeError:
			print("Error: cannot set attribute %r to %r for %s" %(self.map[tag], value, self.obj.__class__.__name__))
			raise AttributeError

	def __iter__(self):
		"""Iterate non-zero tags"""
		for k in self.map:
			if self.map[k]:
				yield k

	def items(self):
		"""Return a list of tag key/value pairs"""
		for k, v in self.map.items():
			if v is not None:
				yield k, self[k]

	def register(self, observer):
		"""Register an observer"""
		self.observers.append(observer)

	def update(self, tags):
		"""Update tags with values from a dictionary"""
		for k, v in tags.items():
			if self.map.get(k) is not None:
				self[k] = v

	def keys(self):
		"""Return the list of tags that are mapped to attributes"""
		return self.map.keys()


class GameManager(Manager):
	map = {
		GameTag.CARD_TYPE: "type",
		#GameTag.NEXT_STEP: "next_step",
		#GameTag.NUM_MINIONS_KILLED_THIS_TURN: "minions_killed_this_turn",
		#GameTag.PROPOSED_ATTACKER: "proposed_attacker",
		#GameTag.PROPOSED_DEFENDER: "proposed_defender",
		#GameTag.STATE: "state",
		GameTag.STEP: "step",
		GameTag.TURN_NUMBER: "turn",
		GameTag.TURN_PLAYER: "current_player",
		GameTag.STEP_PLAYER: "step_player",
		GameTag.ZONE: "zone",
	}

	def __init__(self, obj):
		super().__init__(obj)
		self.counter = 0
		obj.entity_id = self.counter

	def action_start(self, type, source, index, targets):
		for observer in self.observers:
			observer.action_start(type, source, index, targets)

	def action_end(self, type, source):
		for observer in self.observers:
			observer.action_end(type, source)

	def new_entity(self, entity):
		self.counter += 1
		entity.entity_id = self.counter
		#logging.entity.log("New entity ID %d (%s)", entity.entity_id, str(entity))
		for observer in self.observers:
			observer.new_entity(entity)

	def start_game(self):
		for observer in self.observers:
			observer.start_game()

	def step(self, step, next_step=None):
		for observer in self.observers:
			observer.game_step(step, next_step)
		self.obj.step = step
		if next_step is not None:
			self.obj.next_step = next_step

	def turn(self, player):
		for observer in self.observers:
			observer.turn(player)

class PlayerManager(Manager):
	map = {
		GameTag.CARD_ID:		"id",
		GameTag.CARD_TYPE:		"type",
		GameTag.NAME:			"name",
		GameTag.POWER:			"power",
		GameTag.HEALTH:			"max_health",
		GameTag.TERRITORY:		"territory",
		GameTag.MORALE:			"morale",
		GameTag.SUPPLY:			"supply",
		GameTag.MAX_HAND_SIZE:	"max_hand_size",
		GameTag.CONTROLLER:		"controller",
		#GameTag.ZONE:			"zone",
		GameTag.TEXT:			None,
	}


class CardManager(Manager):
	map = {
		GameTag.CARD_ID:		"id",
		GameTag.CARD_TYPE:		"type",
		#GameTag.NAME:			"name",
		#GameTag.TEXT:			"text",

		GameTag.POWER:			"power",
		GameTag.HEALTH:			"max_health",
		GameTag.MORALE:			"morale",
		GameTag.SUPPLY:			"supply",
		GameTag.DAMAGE:			"damage",
		GameTag.OWNER:			"owner",

		GameTag.FURY:			"fury",
		GameTag.INSPIRE:		"inspire",
		GameTag.SPY:			"spy",
		GameTag.INFORM:			"inform",
		GameTag.TOKEN:			"token",
		GameTag.MAX_HAND_SIZE:	"max_hand_size",
		GameTag.TERRITORY:		"territory",
		GameTag.CONTROLLER:		"controller",
		GameTag.ZONE:			"zone",

		GameTag.DECLARED_ATTACK:	"declared_attack",
		GameTag.DECLARED_INTERCEPT:	"declared_intercept",
	}

# Base class for all observers
class BaseObserver:
	def action_start(self, type, source, index, targets):
		pass

	def action_end(self, type, source):
		pass

	def game_step(self, step, next_step):
		pass

	def new_entity(self, entity):
		pass

	def start_game():
		pass

	def turn(self, player):
		pass

