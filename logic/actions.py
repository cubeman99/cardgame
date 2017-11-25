from collections import OrderedDict
from abc import ABCMeta, abstractmethod
from logging import action_log
from enums import *
from logic.events import *
from logic.lazynum import *
from logic.selector import *
from exceptions import *
from manager import Manager, CardManager


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
	"""Input parameter that is evaluated upon invoking the action."""

	def _setup(self, index, name, owner):
		self.index = index
		self.name = name
		self.owner = owner

	def __repr__(self):
		return "<%s.%s>" % (self.owner.__name__, self.name)

	def evaluate(self, source):
		"""Returns the value of this argument that was passed in to the
		previous action, when referenced as Action.FOO from a predicate action.
		Example:
		Summon(CONTROLLER, "Card").then(Damage(Summon.CARD, 2))"""

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
		self.name = None

	def __repr__(self):
		if self.name != None:
			return self.name
		#args = ["%s=%r" % (k, v) for k, v in zip(self.ARGS, self._args)]
		#return "<Action: %s(%s)>" % (self.__class__.__name__, ", ".join(args))
		args = ["%r" % (v) for k, v in zip(self.ARGS, self._args)]
		return "%s(%s)" % (self.__class__.__name__, ", ".join(args))

	def after(self, *actions):
		"""
		Return an event listener that triggers after an action matching this
		one is triggered
		"""
		return EventListener(self, actions, EventListener.AFTER)

	def on(self, *actions):
		"""
		Return an event listener that triggers during an action matching this
		one is triggered
		"""
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
		"""
		Check if the arguments from this action match the arguments from
		another action.
		"""
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
		self.invoke(source, *args, **self._kwargs.copy())

		for action in self.callback:
			action_log.log("%r queues up callback %r", self, action)
			#action_log.log("%r queues up callback %r with args %r", self, action, str([target] + target_args))
			source.game.queue_actions(source, [action], event_args=args)


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

	"""def eval(self, selector, source):
		if isinstance(selector, Entity):
			return [selector]
		else:
			return selector.eval(source.game, source)"""

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
		elif t == None:
			return [None]
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
		if isinstance(times, LazyValue):
			times = times.evaluate(source)
		#elif isinstance(times, Action):
		#	times = times.trigger(source)[0]

		for i in range(times):
			self.trigger_index = i
			args = self.get_args(source)
			targets = self.get_targets(source, args[0])
			args = args[1:]
			action_log.log("%r triggering %r targeting %r", source, self, targets)
			for target in targets:
				target_args = self.get_target_args(source, target)
				ret.append(self.invoke(source, target, *target_args, **self._kwargs.copy()))

				for action in self.callback:
					action_log.log("%r queues up callback %r with args %r", self, action, str([target] + target_args))
					ret += source.game.queue_actions(source, [action], event_args=[target] + target_args)

		#self.resolve_broadcasts()

		return ret

#==============================================================================
# Actions
#==============================================================================

class Attack(TargetedAction):
	"""
	Creates an attack from \a source to \a target.
	"""
	ATTACKER = ActionArg()
	DEFENDER = ActionArg()

	text = "{attacker} attacks {defender}"

	def invoke(self, source, attacker, defender):
		if isinstance(defender, list):
			defender = defender[0]
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
	"""
	Cause a hit on \a targets for \a amount.
	"""
	TARGET = ActionArg()
	AMOUNT = IntArg()

	def invoke(self, source, target, amount):
		action_log.log("Hitting %r for %d damage", target, amount)
		source.game.queue_actions(source, [Damage(target, amount)])

class Damage(TargetedAction):
	"""
	Damage \a targets by \a amount. The event will not broadcast if the final amount is 0.
	"""
	TARGET = ActionArg()
	AMOUNT = IntArg()

	def invoke(self, source, target, amount):
		action_log.log("Damaging %r by %d", target, amount)
		target.hit(source, amount)
		self.broadcast(source, EventListener.ON, target, amount, source)

class Destroy(TargetedAction):
	"""
	Destroy \a targets.
	"""

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

class Discard(TargetedAction):
	"""
	Discard card targets in a player's hand.
	"""
	def invoke(self, source, target):
		self.broadcast(source, EventListener.ON, target)
		target.discard()

class Summon(TargetedAction):
	"""
	Summons \a card for each target.
	"""
	TARGET = ActionArg()
	CARD = CardArg()

	def get_args(self, source):
		ret = super().get_args(source)
		return ret

	def invoke(self, source, target, cards, token=False):
		#log.info("%s summons %r", target, cards)
		cards = _eval_card(source, cards)
		if isinstance(target, AttrValue):
			target = target.eval(source)

		#summon_as_token = self._kwargs.get("token", False)

		for card in cards:
			action_log.log("Summoning %r for %s", card, target)

			# Set the card's controller
			if card.controller != target:
				card.controller = target

			# Move the card into play
			if card.zone != Zone.PLAY:
				card.zone = Zone.PLAY

			#if summon_as_token:
			if token:
				card.token = True

			# Broadcast the summon event.
			self.queue_broadcast(self, (source, EventListener.ON, target, card))
			self.broadcast(source, EventListener.AFTER, target, card)

		return cards

class Play(GameAction):
	"""
	Plays the card \a card on the targets \a targets if specified.
	"""
	PLAYER	= ActionArg()
	CARD	= CardArg()
	TARGETS	= ActionArg()

	def invoke(self, source, card, targets):
		#log.info("%s summons %r", targets, cards)
		player = source
		if len(targets) == 0:
			action_log.log("%s plays %r", player, card)
		else:
			action_log.log("%s plays %r, targeting %s", player, card, str(targets))

		player.pay_cost(card, card.morale, card.supply)

		card.targets = targets

		# Move the card into play.
		# IF this card is a spell, then discard it instead.
		if card.type == CardType.SPELL:
			card.zone = Zone.DISCARD
		else:
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

		# Trigger the card's corrupt actions.
		if card.corrupts:
			if targets[0] != None:
				# Success: Perform the corrupt action
				source.game.queue_actions(card, [Corrupt(card, card.targets)])
			else:
				# Failure: append the corrupt failure actions to the beggining
				# of the  emerge actions
				action_log.log("%r fails to corrupt", card)
				emerge_actions = card.get_actions("corrupt_fail") + emerge_actions

		# Trigger the card's emerge actions.
		if len(emerge_actions) > 0:
			source.game.queue_actions(card, [Emerge(card, card.targets)])

		# Broadcast the "After Play" event
		self.broadcast(player, EventListener.AFTER, player, card)


class Draw(TargetedAction):
	"""
	Draws one card for the targets from the top of their deck.
	"""
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
		action_log.log("%s begins turn %i", player, source.turn)
		source.current_player = player
		#source.manager.step(source.next_step, Step.MAIN_START_TRIGGERS)
		#source.manager.step(source.next_step, source.next_step)
		self.broadcast(source, EventListener.ON, player)
		#source._begin_turn(player)



class EndTurn(GameAction):
	PLAYER = ActionArg()

	def invoke(self, source, player):
		action_log.log("%s ends turn %i", player, source.turn)
		self.broadcast(source, EventListener.ON, player)

# Aftermath = Triggered when a unit dies.
class Aftermath(TargetedAction):
	TARGET = ActionArg()

	def invoke(self, source, target):
		action_log.log("Triggering aftermath for %r", target)

		for aftermath in target.aftermaths:
			if callable(aftermath):
				actions = aftermath(target)
			else:
				actions = aftermath
			actions = aftermath
			source.game.queue_actions(target, actions)

# Emerge = Triggered upon playing the card.
class Emerge(TargetedAction):
	TARGET = ActionArg()

	def invoke(self, source, target):
		action_log.log("Triggering emerge for %r", target)

		emerge_actions = []
		if target.type == CardType.UNIT:
			emerge_actions = target.get_actions("emerge")
		elif target.type == CardType.SPELL:
			emerge_actions = target.get_actions("play")
		if target.corrupts:
			if target.targets[0] == None:
				emerge_actions = target.get_actions("corrupt_fail") + emerge_actions
			else:
				emerge_actions = target.get_actions("corrupt") + emerge_actions

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
	#TARGET = ActionArg()

	def invoke(self, source, target):
		corrupt_target = target.targets[0]
		action_log.log("%r corrupts %r", target, corrupt_target)

		# Destroy the corrupt target.
		source.game.queue_actions(target, [Destroy(corrupt_target)])

		# Perform the corrupt actions.
		corrupt_actions = target.get_actions("corrupt")
		for action in corrupt_actions:
			if callable(action):
				actions = action(target)
			else:
				actions = action
			source.game.queue_actions(target, action)

			if target.controller.extra_corrupts:
				action_log.log("Triggering corrupt action for %r again", target)
				source.game.queue_actions(target, actions)

# Inspire = Gain X Morale when this unit attacks a player
class Inspire(TargetedAction):
	"""
	Trigger inspire for the target.
	"""
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

		if not isinstance(entities, list):
			entities = [entities]

		return [self.copy(source, e) for e in entities]


class ExactCopy(Copy):
	"""
	Lazily create an exact copy of the target.
	An exact copy will include buffs and all tags.
	"""
	def copy(self, source, entity):
		copy = super().copy(source, entity)
		#for k in entity.silenceable_attributes:
		#	v = getattr(entity, k)
		#	setattr(copy, k, v)
		copy.damage = entity.damage
		#for buff in entity.buffs:
		#	# Recreate the buff stack
		#	entity.buff(copy, buff.id)
		return copy


class Buff(TargetedAction):
	"""
	Buff character targets with Effect \a id
	NOTE: Any Card can buff any other Card. The controller of the
	Card that buffs the target becomes the controller of the buff.
	"""
	TARGET = ActionArg()
	BUFF = CardArg()

	def invoke(self, source, target, buffs, **kwargs):
		ret = []
		for buff in buffs:
			for k, v in kwargs.items():
				if isinstance(v, LazyValue):
					v = v.evaluate(source)
				setattr(buff, k, v)
			ret.append(buff.apply(target))
		return ret


class GiveMorale(TargetedAction):
	"""
	Make player targets gain \a amount morale.
	Note: \a amount can be negative to cause them to lose mana.
	"""
	TARGET = ActionArg()
	AMOUNT = IntArg()

	def invoke(self, source, target, amount):
		print("Giving %d morale to %r" %(amount, target))
		target.morale += amount

class Bounce(TargetedAction):
	"""
	Move a unit on the field back into their controller's hand.
	"""
	def invoke(self, source, target):
		if len(target.controller.hand) >= target.controller.max_hand_size:
			action_log.log("%r is bounced to a full hand and gets destroyed", target)
			return source.game.queue_actions(source, [Destroy(target)])
		else:
			action_log.log("%r is bounced back to %s's hand", target, target.controller)
			target.zone = Zone.HAND





class AuraBuff:
	def __init__(self, source, entity):
		self.source = source
		self.entity = entity
		self.tags = CardManager(self)

	def __repr__(self):
		return "<AuraBuff %r -> %r>" % (self.source, self.entity)

	def update_tags(self, tags):
		self.tags.update(tags)
		self.tick = self.source.game.tick

	def remove(self):
		action_log.log("Destroying %r", self)
		self.entity.slots.remove(self)
		self.source.game.active_aura_buffs.remove(self)

	def _getattr(self, attr, i):
		value = getattr(self, attr, 0)
		if callable(value):
			return value(self.entity, i)
		return i + value


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



class ActionOutput(LazyValue):
	def __repr__(self):
		return "<%s>" %(self.__class__.__name__)
		#return "<%s.%s>" % (self.owner.__name__, self.name)

	def evaluate(self, source):
		#assert source.event_args
		#return source.event_outputs[self.index]
		return source.event_outputs[0]

class Choose(GameAction):
	"""
	Initiate a choice for \a player, provided a set of \a cards to choose from.
	This will halt the action queue until the player makes their choice.
	"""
	PLAYER = ActionArg()
	CARDS = ActionArg()
	CHOICE = ActionOutput()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.choice_callback = ()
		self.type = ChoiceType.GENERAL

	def then(self, *args):
		"""
		Create a callback containing an action queue, called upon the
		action's trigger with the action's arguments available.
		"""
		# Create a special callback that triggers when the choice is complete.
		ret = self.__class__(*self._args, **self._kwargs)
		ret.choice_callback = args
		ret.times = self.times
		return ret

	def get_args(self, source):
		# Evaluate the player argument.
		player = self._args[0]
		if isinstance(player, Selector):
			player = player.eval(source.game.players, source)
			assert len(player) == 1
			player = player[0]
		elif isinstance(player, LazyValue):
			player = player.evaluate(source)
			assert player != None

		# Evaluate the choice list argument.
		cards = self._args[1]
		if isinstance(cards, Selector):
			cards = cards.eval(source.game, source)
		elif isinstance(cards, LazyValue):
			cards = cards.evaluate(source)

		count = 1
		if len(self._args) >= 3:
			count = self._args[2]

		# TODO: create a card from ID
		#for card in cards:
			#if isinstance(card, str):
				#pass
			#else:
				# Cards in the choice must be set aside.
				#card.zone = Zone.SET_ASIDE

		action_log.log("%r begins choice between %r" %(player, cards))
		return player, cards, count

	def invoke(self, source, player, cards, count):
		self.source = source
		self.player = player
		self.source.game.choosing_player = player
		self.cards = cards
		self.min_count = count
		self.max_count = count
		self.source.game.choice = self
		self.player.choice = self # The player enters a choosing state.

	def choose(self, cards):
		"""
		Perform the choice. This will trigger any followup actions, plus the
		rest of the action queue.
		"""
		if not isinstance(cards, list):
			cards = [cards]

		# Validate the choices
		if len(cards) < self.min_count:
			raise InvalidAction("Too few choices: %d (must be between %d and %d)" % (len(cards), self.min_count, self.max_count))
		if len(cards) > self.max_count:
			raise InvalidAction("Too many choices: %d (must be between %d and %d)" % (len(cards), self.min_count, self.max_count))
		for card in cards:
			if card not in self.cards:
				raise InvalidAction("%r is not a valid choice (one of %r)" % (card, self.cards))

		action_log.log("%r chooses %r" %(self.player, cards))

		# TODO: need to discard certain choice cards

		self.player.choice = None
		self.source.game.choice = None

		for action in self.choice_callback:
			action_log.log("Choice queues up callback %r", action)
			#action_log.log("%r queues up callback %r with args %r", self, action, str([target] + target_args))
			self.source.game.queue_actions(self.source, [action], event_args=self._args, event_outputs=[cards])

#------------------------------------------------------------------------------
# General Actions
#------------------------------------------------------------------------------

class IfThen(TargetedAction):
	"""
	Perform \a then_actions if a condition is true.
	"""
	CONDITION = ActionArg()
	THEN_ACTIONS = ActionArg()

	def invoke(self, source, condition, then_actions):
		if condition:
			self.source.game.queue_actions(source, then_actions)

class IfThenElse(TargetedAction):
	"""
	Perform \a then_actions if a condition is true, else perform
	\a else_actions.
	"""
	CONDITION = ActionArg()
	THEN_ACTIONS = ActionArg()
	ELSE_ACTIONS = ActionArg()

	def invoke(self, source, condition, then_actions):
		if condition:
			self.source.game.queue_actions(source, then_actions)
		else:
			self.source.game.queue_actions(source, else_actions)


#------------------------------------------------------------------------------
# Custom Actions
#------------------------------------------------------------------------------

# Custom compound actions

def ChooseAndDiscard(player, count=1):
	action = Choose(player, IN_HAND & CONTROLLED_BY(player)).then(
		Discard(Choose.CHOICE))
	action.name = "ChooseAndDiscard(%r" %(player)
	if count != 1:
		action.name += ", %d" %(count)
	action.name += ")"
	return action


#def ChooseTarget(player, targeted_action):
#	targets = targeted_action._args[0]
#	#print(targets)
#	action = Choose(player, targets).then(
#		targeted_action)
#	action.name = "ChooseTarget(%r, %r)" %(player, targeted_action)
#	return action

#------------------------------------------------------------------------------
# Custom Event Actions
#------------------------------------------------------------------------------

OWN_TURN_BEGIN = BeginTurn(CONTROLLER)
TURN_BEGIN = BeginTurn(ALL_PLAYERS)
OWN_TURN_END = EndTurn(CONTROLLER)
TURN_END = EndTurn(ALL_PLAYERS)

