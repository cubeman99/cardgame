from collections import OrderedDict
from abc import ABCMeta, abstractmethod
from logging import action_log
from enums import *
from logic.selector import *
from logic.lazynum import *

def _eval_card(source, card):
	"""
	Return a Card instance from \a card
	The card argument can be:
	- A Card instance (nothing is done)
	- The string ID of the card (the card is created)
	- A LazyValue (the card is dynamically created)
	"""
	if isinstance(card, LazyValue):
		card = card.evaluate(source)

	if isinstance(card, Action):
		card = card.trigger(source)[0]

	if not isinstance(card, list):
		cards = [card]
	else:
		cards = card

	ret = []
	for card in cards:
		if isinstance(card, str):
			ret.append(source.controller.card(card, source))
		else:
			ret.append(card)

	return ret


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

class ActionMeta(type):
	def __new__(metacls, name, parents, namespace):
		cls = type.__new__(metacls, name, parents, dict(namespace))
		# Compile the argument list
		argslist = []
		for key, value in namespace.items():
			if not isinstance(value, ActionArg):
				continue
			value._setup(len(argslist), key, cls)
			argslist.append(value)
		cls.ARGS = tuple(argslist)
		return cls

	@classmethod
	def __prepare__(metacls, name, bases):
		return OrderedDict()

class ActionArg(LazyValue):
	def _setup(self, index, name, owner):
		self.index = index
		self.name = name
		self.owner = owner

	def __repr__(self):
		return "<%s.%s>" % (self.owner.__name__, self.name)

	def evaluate(self, source):
		# This is used when an event listener triggers and the callback
		# Action has arguments of the type Action.FOO
		# XXX we rely on source.event_args to be set, but it's very racey.
		# If multiple events happen on an entity at once, stuff will go wrong.
		assert source.event_args
		return source.event_args[self.index]

class CardArg(ActionArg):
	# Type hint
	pass

class IntArg(ActionArg, LazyNum):
	def evaluate(self, source):
		ret = super().evaluate(source)
		return self.num(ret)

class Action(metaclass=ActionMeta):
	def __init__(self, *args, **kwargs):
		self._args = args
		self._kwargs = kwargs
		self.callback = ()
		self.times = 1
		self.event_queue = []

	def __repr__(self):
		#args = ["%s=%r" % (k, v) for k, v in zip(self.ARGS, self._args)]
		#return "<Action: %s(%s)>" % (self.__class__.__name__, ", ".join(args))
		args = ["%s" % (v) for k, v in zip(self.ARGS, self._args)]
		return "%s(%s)" % (self.__class__.__name__, ", ".join(args))

	def after(self, *actions):
		return EventListener(self, actions, EventListener.AFTER)

	def on(self, *actions):
		return EventListener(self, actions, EventListener.ON)

	def then(self, *args):
		"""
		Create a callback containing an action queue, called upon the
		action's trigger with the action's arguments available.
		"""
		ret = self.__class__(*self._args, **self._kwargs)
		ret.callback = args
		ret.times = self.times
		return ret

	# Notify a single entity
	def notify(self, entity, source, at, *args):
		for event in entity.events:
			if event.at != at:
				continue
			if isinstance(event.trigger, self.__class__) and event.trigger.matches(entity, args):
				action_log.log("%r triggers %s %r from %r", entity, "on" if at == EventListener.ON else "after", self, source)
				entity.trigger_event(source, event, args)

	# Broadcast an event to all entities
	def broadcast(self, source, at, *args):
		# Notify all entities in play
		for entity in source.game.entities:
			self.notify(entity, source, at, *args)
		# TODO: notify entities in other places
		#for entity in source.game.board:
		#	self.notify(entity, source, at, *args)

	def queue_broadcast(self, obj, args):
		self.event_queue.append((obj, args))

	def resolve_broadcasts(self):
		for obj, args in self.event_queue:
			obj.broadcast(*args)
		self.event_queue = []

	def get_args(self, source):
		return self._args

	def matches(self, source, args):
		for arg, match in zip(args, self._args):
			if match is None:
				# Allow matching Action(None, None, z) to Action(x, y, z)
				continue
			if arg is None:
				# We got an arg of None and a match not None. Bad.
				return False
			if callable(match):
				res = match(arg)
				if not res:
					return False
			else:
				# this stuff is stupidslow
				res = match.eval([arg], source)
				if not res or res[0] is not arg:
					return False
		return True

class GameAction(Action):
	def trigger(self, source):
		args = self.get_args(source)
		self.invoke(source, *args)


class TargetedAction(Action):
	TARGET = ActionArg()

	def __init__(self, *args, **kwargs):
		self.source = kwargs.pop("source", None)
		super().__init__(*args, **kwargs)
		self.trigger_index = 0

	#def __repr__(self):
	#	args = ["%s=%r" % (k, v) for k, v in zip(self.ARGS[1:], self._args[1:])]
	#	return "<TargetedAction: %s(%s)>" % (self.__class__.__name__, ", ".join(args))

	def __mul__(self, value):
		self.times = value
		return self

	def eval(self, selector, source):
		if isinstance(selector, Entity):
			return [selector]
		else:
			return selector.eval(source.game, source)

	def get_target_args(self, source, target):
		ret = []
		for k, v in zip(self.ARGS[1:], self._args[1:]):
			if isinstance(v, Selector):
				# evaluate Selector arguments
				v = v.eval(source.game, source)
			elif isinstance(v, LazyValue):
				v = v.evaluate(source)
			elif isinstance(k, CardArg):
				v = _eval_card(source, v)
			ret.append(v)
		return ret

	def get_targets(self, source, t):
		if isinstance(t, Entity):
			ret = t
		elif isinstance(t, LazyValue):
			ret = t.evaluate(source)
		else:
			ret = t.eval(source.game, source)
		if not ret:
			return []
		if not hasattr(ret, "__iter__"):
			# Bit of a hack to ensure we always get a list back
			ret = [ret]
		return ret

	def trigger(self, source):
		ret = []

		if self.source is not None:
			source = self.source.eval(source.game, source)
			assert len(source) == 1
			source = source[0]

		times = self.times
		#if isinstance(times, LazyValue):
		#	times = times.evaluate(source)
		#elif isinstance(times, Action):
		#	times = times.trigger(source)[0]

		for i in range(times):
			self.trigger_index = i
			args = self.get_args(source)
			targets = self.get_targets(source, args[0])
			args = args[1:]
			#action_log.log("%r triggering %r targeting %r", source, self, targets)
			for target in targets:
				target_args = self.get_target_args(source, target)
				ret.append(self.invoke(source, target, *target_args))

				#for action in self.callback:
				#	log.info("%r queues up callback %r", self, action)
				#	ret += source.game.queue_actions(source, [action], event_args=[target] + target_args)

		#self.resolve_broadcasts()

		return ret

#==============================================================================
# Actions
#==============================================================================

class Attack(GameAction):
	ATTACKER = ActionArg()
	DEFENDER = ActionArg()

	text = "{attacker} attacks {defender}"

	def invoke(self, source, attacker, defender):
		action_log.log("%r attacks %r", attacker, defender)
		attacker.defender = defender
		defender.attacker = attacker
		self.broadcast(source, EventListener.ON, attacker, defender)

		defender_power = defender.power
		attacker_power = attacker.power

		# If the defender is a player, then do not trigger any Hit actions.
		if defender.type == CardType.PLAYER:
			action_log.log("%s gains %d territory", defender.opponent, attacker_power)
			attacker.controller.territory += attacker_power
			if attacker.inspire > 0:
				attacker.controller.morale += attacker.inspire
			if attacker.spy > 0:
				defender.controller.morale -= 1
			if attacker.inform > 0:
				source.game.queue_actions(attacker, [Draw(attacker.controller)])
		else:
			source.game.queue_actions(attacker, [Hit(defender, attacker.power)])
			if defender_power > 0:
				source.game.queue_actions(defender, [Hit(attacker, defender_power)])

		self.broadcast(source, EventListener.AFTER, attacker, defender)

		attacker.defender = None
		defender.attacker = None

class Hit(TargetedAction):
	TARGET = ActionArg()
	AMOUNT = IntArg()

	def invoke(self, source, target, amount):
		action_log.log("Hitting %r for %d damage", target, amount)
		source.game.queue_actions(source, [Damage(target, amount)])

class Damage(TargetedAction):
	TARGET = ActionArg()
	AMOUNT = IntArg()

	def invoke(self, source, target, amount):
		action_log.log("Damaging %r by %d", target, amount)
		target.hit(source, amount)

class Destroy(TargetedAction):
	def invoke(self, source, target):
		if target.delayed_destruction:
			#  If the card is in PLAY, it is instead scheduled to be destroyed
			# It will be moved to the graveyard on the next Death event
			action_log.log("%r marks %r for imminent death", source, target)
			if not target.to_be_destroyed:
				target.to_be_destroyed = True
				target.source_of_death = source
		else:
			action_log.log("%r destroys %r", source, target)
			target.zone = Zone.DISCARD

class Death(GameAction):
	ENTITY = ActionArg()

	def invoke(self, source, target):
		action_log.log("Processing Death for %r", target)
		self.broadcast(source, EventListener.ON, target)
		if target.aftermaths:
			source.game.queue_actions(source, [Aftermath(target)])

class Summon(TargetedAction):
	TARGET = ActionArg()
	CARD = CardArg()

	def get_args(self, source):
		ret = super().get_args(source)
		return ret

	def invoke(self, source, target, cards):
		#log.info("%s summons %r", target, cards)
		cards = _eval_card(source, cards)
		if isinstance(target, AttrValue):
			target = target.eval(source)

		for card in cards:
			action_log.log("Summoning %s for %s", card.name, target)

			# Set the card's controller
			if card.controller != target:
				card.controller = target

			# Move the card into play
			if card.zone != Zone.PLAY:
				card.zone = Zone.PLAY

			# Broadcast the summon event.
			self.queue_broadcast(self, (source, EventListener.ON, target, card))
			self.broadcast(source, EventListener.AFTER, target, card)

		return cards

class Play(GameAction):
	PLAYER = ActionArg()
	CARD = CardArg()
	TARGET = ActionArg()

	def invoke(self, source, card, target):
		#log.info("%s summons %r", target, cards)
		player = source
		action_log.log("%s plays %r", player, card)

		card.target = target

		# Move the card into play
		card.zone = Zone.PLAY

		# Broad cast the "On Play" event
		self.broadcast(player, EventListener.ON, player, card)
		self.resolve_broadcasts()

		# Trigger the card's emerge
		emerge_actions = []
		if card.type == CardType.UNIT:
			emerge_actions = card.get_actions("emerge")
		elif card.type == CardType.SPELL:
			emerge_actions = card.get_actions("play")
		print(card.type)
		if len(emerge_actions) > 0:
			source.game.queue_actions(card, [Emerge(card, card.target)])

		# Broad cast the "After Play" event
		self.broadcast(player, EventListener.AFTER, player, card)


class Draw(TargetedAction):
	TARGET = ActionArg()
	CARD = CardArg()

	# Return the topmost card from the target's dack
	def get_target_args(self, source, target):
		if target.deck.empty():
			card = None
		else:
			card = target.deck[-1]
		return [card]

	def invoke(self, source, target, card):
		if card is None:
			action_log.log("%r cannot draw (deck is empty)", target)
			return []
		#action_log.log("%r draws a card", target)
		card.draw()
		self.broadcast(source, EventListener.ON, target)
		return [card]


class BeginTurn(GameAction):
	PLAYER = ActionArg()

	def invoke(self, source, player):
		#source.manager.step(source.next_step, Step.MAIN_READY)
		source.turn += 1
		source.log("%s begins turn %i", player, source.turn)
		source.current_player = player
		#source.manager.step(source.next_step, Step.MAIN_START_TRIGGERS)
		#source.manager.step(source.next_step, source.next_step)
		self.broadcast(source, EventListener.ON, player)
		#source._begin_turn(player)

# Aftermath = Triggered when a unit dies.
class Aftermath(TargetedAction):
	TARGET = ActionArg()

	def invoke(self, source, target):
		action_log.log("Triggering aftermath for %r", target)
		print(target.aftermaths)
		for aftermath in target.aftermaths:
			if callable(aftermath):
				actions = aftermath(target)
			else:
				actions = aftermath
			actions = aftermath
			source.game.queue_actions(target, actions)

# Corrupt = Triggered upon playing the card.
class Emerge(TargetedAction):
	TARGET = ActionArg()

	def invoke(self, source, target):
		action_log.log("Triggering emerge for %r", target)

		emerge_actions = []
		if target.type == CardType.UNIT:
			emerge_actions = target.get_actions("emerge")
		elif target.type == CardType.SPELL:
			emerge_actions = target.get_actions("play")

		for emerge in emerge_actions:
			if callable(emerge):
				actions = emerge(target)
			else:
				actions = emerge
			actions = emerge
			source.game.queue_actions(target, actions)

# Wisdom = Gain an effect only if you have 5 or more cards in your hand when
#          you play this card
class Wisdom(TargetedAction):
	TARGET = ActionArg()

	def invoke(self, source, target):
		action_log.log("Triggering wisdom for %r", target)
		for emerge in target.wisdoms:
			actions = wisdom
			source.game.queue_actions(target, actions)

# Corrupt = Destroy an allied unit to trigger an effect.
class Corrupt(TargetedAction):
	CORRUPTOR = ActionArg()
	TARGET = ActionArg()

	def invoke(self, source, corruptor, target):
		action_log.log("%r corrupts %r", corruptor, target)

		corruptor.target = target

		# Destroy the target.
		source.game.queue_actions(corruptor, [Destroy(target)])

		# Perform the corrupt actions.
		corrupt_actions = corruptor.get_actions("corrupt")
		for action in corrupt_actions:
			source.game.queue_actions(corruptor, action)

		corruptor.target = None

# Inspire = Gain X Morale when this unit attacks a player
class Inspire(TargetedAction):
	TARGET = ActionArg()

	def invoke(self, source, target):
		action_log.log("Triggering inspire for %r", target)
		#target.tags["inspire"]




class Copy(LazyValue):
	"""
	Lazily return a list of copies of the target
	"""
	def __init__(self, selector):
		self.selector = selector

	def __repr__(self):
		return "%s(%r)" % (self.__class__.__name__, self.selector)

	def copy(self, source, entity):
		"""
		Return a copy of \a entity
		"""
		action_log.log("Creating a copy of %r", entity)
		return source.controller.card(entity.id, source)

	def evaluate(self, source) -> [str]:
		if isinstance(self.selector, LazyValue):
			entities = [self.selector.evaluate(source)]
		else:
			entities = self.selector.eval(source.game, source)

		return [self.copy(source, e) for e in entities]


class ExactCopy(Copy):
	"""
	Lazily create an exact copy of the target.
	An exact copy will include buffs and all tags.
	"""
	def copy(self, source, entity):
		ret = super().copy(source, entity)
		#for k in entity.silenceable_attributes:
		#	v = getattr(entity, k)
		#	setattr(ret, k, v)
		#ret.silenced = entity.silenced
		ret.damage = entity.damage
		#for buff in entity.buffs:
		#	# Recreate the buff stack
		#	entity.buff(ret, buff.id)
		return ret


class Buff(TargetedAction):
	"""
	Buff character targets with Enchantment \a id
	NOTE: Any Card can buff any other Card. The controller of the
	Card that buffs the target becomes the controller of the buff.
	"""
	TARGET = ActionArg()
	BUFF = ActionArg()

	def get_target_args(self, source, target):
		buff = self._args[1]
		buff = source.controller.card(buff)
		buff.source = source
		return [buff]

	def invoke(self, source, target, buff):
		kwargs = self._kwargs.copy()
		for k, v in kwargs.items():
			if isinstance(v, LazyValue):
				v = v.evaluate(source)
				print("Evaluated buff arg %s to %r" %(k, v))
			setattr(buff, k, v)
		return buff.apply(target)


class GiveMorale(TargetedAction):
	"""
	Give \a morale to a player.
	"""
	TARGET = ActionArg()
	AMOUNT = IntArg()

	def invoke(self, source, target, amount):
		print("Giving %d morale to %r" %(amount, target))
		target.morale += amount




class Refresh:
	"""
	Refresh a buff or a set of tags on an entity
	"""
	def __init__(self, selector, tags=None, buff=None):
		self.selector = selector
		self.tags = tags
		self.buff = buff

	def trigger(self, source):
		entities = self.selector.eval(source.game, source)
		for entity in entities:
			if self.buff:
				entity.refresh_buff(source, self.buff)
			else:
				tags = {}
				for tag, value in self.tags.items():
					if not isinstance(value, int) and not callable(value):
						value = value.evaluate(source)
					tags[tag] = value

				entity.refresh_tags(source, tags)

	def __repr__(self):
		return "Refresh(%r, %r, %r)" % (self.selector, self.tags or {}, self.buff or "")



