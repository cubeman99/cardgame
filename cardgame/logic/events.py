from ..enums import *


class EventListener:
	ON = 1
	AFTER = 2

	def __init__(self, trigger, actions, at):
		self.trigger = trigger
		self.actions = actions
		self.at = at
		self.once = False

	def __repr__(self):
		return "On %r: %r" %(self.trigger, self.actions)
		#return "<EventListener %r>" % (self.trigger)


