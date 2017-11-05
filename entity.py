import uuid
import logging
from enums import *
from manager import Manager
import sys
#import cards
#from cards import db


class BaseEntity(object):
	logger = logging.log
	type = CardType.INVALID

	def __init__(self):
		self.manager = self.Manager(self)
		#self.tags = {}
		self.tags = self.Manager(self)
		self._events = []
		self.buffs = []
		self.uuid = uuid.uuid4()
		self.source_of_death = None

	#def _getattr(self, attr, i):
		#return getattr(self, attr)
	#	i += getattr(self, "_" + attr, 0)
		#return getattr(self.data.scripts, attr, lambda s, x: x)(self, i)

	def __repr__(self):
		return "%s" % (self.__class__.__name__)

	@property
	def is_card(self):
		return self.type > CardType.PLAYER

	@property
	def events(self):
		#return self._events
		return self.base_events + self._events

	@property
	def update_scripts(self):
		if self.data:
			yield from self.data.scripts.update

	def get_actions(self, name):
		actions = getattr(self.data.scripts, name)
		if callable(actions):
			actions = actions(self)
		return actions

	def log(self, message, *args):
		self.logger.info(message, *args)

	@property
	def get_damage(self, amount: int, target):
		if target.immune:
			return 0
		return amount

	def trigger_event(self, source, event, args):
		actions = []
		for action in event.actions:
			if callable(action):
				ac = action(self, *args)
				if not ac:
					# Handle falsy returns
					continue
				if not hasattr(ac, "__iter__"):
					actions.append(ac)
				else:
					actions += action(self, *args)
			else:
				actions.append(action)
		ret = source.game.trigger(self, actions, args)
		if event.once:
			self._events.remove(event)

		return ret

	@property
	def get_damage(self, amount: int, target):
		if target.immune:
			return 0
		return amount


class BuffableEntity(BaseEntity):
	def __init__(self):
		super().__init__()
		self.buffs = []
		self.slots = []

	# Get an attribute value with buffs
	def _getattr(self, attr, value):
		value += getattr(self, "_" + attr, 0)
		for buff in self.buffs:
			value = buff._getattr(attr, value)
		#for slot in self.slots:
		#	value = slot._getattr(attr, value)
		#if self.ignore_scripts:
		#	return value
		return value;
		#return getattr(self.data.scripts, attr, lambda s, x: x)(self, value)

	def clear_buffs(self):
		if self.buffs:
			self.log("Clearing buffs from %r", self)
			for buff in self.buffs[:]:
				buff.remove()

class Entity(BuffableEntity):
	base_events = []
	type = CardType.INVALID
	Manager = Manager

	def __init__(self):
		super().__init__()
		self._events = []


def int_property(attr):
	@property
	def func(self):
		ret = self._getattr(attr, 0)
		return max(0, ret)

	@func.setter
	def func(self, value):
		setattr(self, "_" + attr, value)

	return func

