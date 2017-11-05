from enums import GameTag
#from . import enums
import logging


class Manager(object):
	def __init__(self, obj):
		self.obj = obj
		self.observers = []

	def __getitem__(self, tag):
		if self.map.get(tag):
			return getattr(self.obj, self.map[tag], 0)
		raise KeyError

	def __setitem__(self, tag, value):
		try:
			#setattr(self.obj, "power", 0)
			setattr(self.obj, self.map[tag], value)
		except AttributeError:
			print("Error: cannot set attribute %r to %r for %s" %(self.map[tag], value, self.obj.__class__.__name__))
			raise AttributeError

	def __iter__(self):
		for k in self.map:
			if self.map[k]:
				yield k

	def get(self, k, default=None):
		return self[k] if k in self.map else default

	def items(self):
		for k, v in self.map.items():
			if v is not None:
				yield k, self[k]

	def register(self, observer):
		self.observers.append(observer)

	def update(self, tags):
		for k, v in tags.items():
			if self.map.get(k) is not None:
				self[k] = v

	def keys(self):
		return self.map.keys()


class GameManager(Manager):
	map = {
		GameTag.CARD_TYPE: "type",
		#GameTag.NEXT_STEP: "next_step",
		#GameTag.NUM_MINIONS_KILLED_THIS_TURN: "minions_killed_this_turn",
		#GameTag.PROPOSED_ATTACKER: "proposed_attacker",
		#GameTag.PROPOSED_DEFENDER: "proposed_defender",
		#GameTag.STATE: "state",
		#GameTag.STEP: "step",
		#GameTag.TURN: "turn",
		GameTag.ZONE: "zone",
	}

	def __init__(self, obj):
		super().__init__(obj)
		self.counter = 0
		obj.entity_id = self.counter

	def action_start(self, type, source, index, target):
		for observer in self.observers:
			observer.action_start(type, source, index, target)

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
		GameTag.POWER:			"power",
		GameTag.HEALTH:			"max_health",
		GameTag.TERRITORY:		"territory",
		GameTag.MORALE:			"morale",
		GameTag.SUPPLY:			"supply",
		GameTag.MAX_HAND_SIZE:	"max_hand_size",
	}

class CardManager(Manager):
	map = {
		GameTag.POWER:			"power",
		GameTag.HEALTH:			"max_health",
		GameTag.MORALE:			"morale",
		GameTag.SUPPLY:			"supply",

		GameTag.FURY:			"fury",
		GameTag.INSPIRE:		"inspire",
		GameTag.SPY:			"spy",
		GameTag.INFORM:			"inform",
		GameTag.MAX_HAND_SIZE:	"max_hand_size",
		GameTag.TERRITORY:		"territory",
	}

# Base class for all observers
class BaseObserver:
	def action_start(self, type, source, index, target):
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

