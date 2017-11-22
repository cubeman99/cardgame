
from entity import Entity, int_property
from manager import Manager, CardManager
from itertools import chain
from enums import *
import logic.selector
import logic.actions as actions
import logging

MAX_HAND_SIZE = 6

class BaseCard(Entity):
	Manager = CardManager

	def __init__(self, data):
		self.data = data
		self.name = ""
		super().__init__()
		#self.requirements = data.requirements.copy()
		self.id = data.id
		self.controller = None
		self._zone = Zone.INVALID
		self._events = data.scripts.events
		self.tags.update(data.tags)
		self.type = data.type
		self.owner = None

	def get_all_actions(self, name):
		return getattr(self.data.scripts, name)
		#actions = self.get_actions(name)
		#if isinstance(actions, tuple):
		#	actions = list(actions)
		#if not isinstance(actions, list):
		#	actions = [actions]
		#if actions == None:
		#	actions = []
		#return actions

	@property
	def entities(self):
		return chain([self], self.buffs)

	@property
	def play_targets(self):
		# Evaluate play targets based on current board state.
		target_selectors = list(self.data.play_targets)
		if self.get_all_actions("corrupt"):
			target_selectors = [logic.selector.ALLIED_UNITS] + target_selectors
		targets = []
		for selector in target_selectors:
			targets.append(selector.eval(
				entities=self.game.entities,
				source=self.controller))
		return targets

	def __hash__(self):
		return self.id.__hash__()

	def buff(self, target, buff, **kwargs):
		"""
		Summon \a buff and apply it to \a target
		If keyword arguments are given, attempt to set the given
		values to the buff. Example:
		player.buff(target, health=random.randint(1, 5))
		NOTE: Any Card can buff any other Card. The controller of the
		Card that buffs the target becomes the controller of the buff.
		"""
		ret = self.controller.card(buff, self)
		ret.source = self
		ret.apply(target)
		for k, v in kwargs.items():
			setattr(ret, k, v)
		return ret

	def refresh_buff(self, source, id):
		for buff in self.buffs:
			if buff.source is source and buff.id == id:
				buff.tick = source.game.tick
				break
		else:
			logging.action_log.log("Aura from %r buffs %r with %r", source, self, id)
			buff = source.buff(self, id)
			buff.tick = source.game.tick
			source.game.active_aura_buffs.append(buff)

	def refresh_tags(self, source, tags):
		for slot in self.slots:
			if slot.source is source:
				slot.update_tags(tags)
				break
		else:
			buff = AuraBuff(source, self)
			logging.action_log.log("Creating %r", buff)
			buff.update_tags(tags)
			self.slots.append(buff)
			source.game.active_aura_buffs.append(buff)

	def __str__(self):
		return self.data.name

	def __repr__(self):
		return "%s(%s)" % (self.data.id, self.entity_id)

	@property
	def game(self):
		return self.controller.game

	@property
	def zone(self):
		return self._zone

	@zone.setter
	def zone(self, value):
		self._set_zone(value)

	def _set_zone(self, value):
		old = self.zone
		self._zone = value

		if old == value:
			return

		caches = {
			Zone.HAND: self.controller.hand,
			Zone.DECK: self.controller.deck,
			Zone.DISCARD: self.controller.discarded,
		}

		if caches.get(old) is not None:
			caches[old].remove(self)
		if caches.get(value) is not None:
			caches[value].append(self)
		self._zone = value

		if value == Zone.PLAY:
			self.play_counter = self.game.play_counter
			self.game.play_counter += 1

	# Check if the card is playable
	def is_playable(self):
		"""Check if this card is playable based on the current game state"""

		# TODO: other requirements (targeting)
		# TODO: battle cards
		return self.game.step == Step.PLAY and \
			self.game.current_player == self.controller and \
			self.game.choosing_player == self.controller and \
			self.zone == Zone.HAND and \
			self.controller.can_pay_cost(self)

	# Check if the card is activated by some condition
	def is_activated(self):
		"""Check if this card is activated by the current game state"""
		return False

	@property
	def supply_cost(self):
		return self.data.supply

	@property
	def morale_cost(self):
		return self.data.morale

	#def play(self, *args):
	#	raise NotImplementedError

	def play(self, targets=[]):
		self.game.play_card(self, targets)
		return self

	def destroy(self):
		pass

	def discard(self):
		pass

	def draw(self):
		#if len(self.controller.hand) >= MAX_HAND_SIZE:
			#self.discard()
		#else:
		logging.action_log.log("%s draws %r", self.controller, self)
		self.zone = Zone.HAND
		actions = self.get_actions("draw")
		self.game.trigger(self, actions, event_args=None)

	#def heal(self, target, amount):
		#return self.game.


class LiveEntity(BaseCard):
	power		= int_property("power")
	#power = 0
	max_health	= int_property("max_health")
	damage		= int_property("damage")

	def __init__(self, data):
		super().__init__(data)
		#self.damage = 0
		self._to_be_destroyed = False
		self.source_of_death = None

	@property
	def to_be_destroyed(self):
		return self.health <= 0 or self._to_be_destroyed

	@to_be_destroyed.setter
	def to_be_destroyed(self, value):
		self._to_be_destroyed = value

	@property
	def damaged(self):
		return self.damage > 0

	@property
	def dead(self):
		return self.zone == Zone.DISCARD or self.to_be_destroyed


	@property
	def delayed_destruction(self):
		return self.zone == Zone.PLAY

	@property
	def aftermaths(self):
		actions = []
		for action in self.get_actions("aftermath"):
			actions.append(action)
		for buff in self.buffs:
			for action in buff.aftermaths:
				actions.append(action)
		return actions

	@property
	def emerges(self):
		return self.get_all_actions("emerge")

	@property
	def wisdoms(self):
		return self.get_all_actions("wisdom")

	@property
	def corrupts(self):
		return self.tags.get(GameTag.CORRUPT, 0) == 1

	@property
	def corrupt_actions(self):
		return self.get_all_actions("corrupt")

	@property
	def corrupt_fail_actions(self):
		return self.get_all_actions("corrupt_fail")

	def hit(self, source, amount):
		if not self.to_be_destroyed:
			self.damage += amount
			if self.to_be_destroyed:
				self.source_of_death = source
		else:
			self.damage += amount


#------------------------------------------------------------------------------
# Unit
#------------------------------------------------------------------------------
class Unit(LiveEntity):
	inspire		= int_property("inspire")
	spy			= int_property("spy")
	inform		= int_property("inform")

	def __init__(self, data):
		super().__init__(data)
		self.declared_attack = None
		self.declared_intercept = None
		self.flipped = False

	@property
	def attack_targets(self):
		"""Return the valid targets this unit can attack."""
		return self.controller.opponent.field

	@property
	def intercept_targets(self):
		"""Return the valid targets this unit can intercept."""
		for unit in self.controller.opponent.field:
			if unit.declared_attack != None and unit.declared_attack != self:
				yield unit

	@property
	def health(self):
		"""Return the this unit's current health."""
		return self.max_health - self.damage

	def can_attack(self):
		"""Return whether this unit is currently able to declare an attack."""
		# Flipped units cannot attack
		if self.flipped:
			return False
		return self.power > 0 and \
			self.game.step == Step.DECLARE and \
			self.game.current_player == self.controller and \
			self.game.choosing_player == self.controller

	def can_intercept(self):
		"""Return whether this unit is currently able to declare an intercept."""
		# First check if this unit is being attacked.
		for unit in self.controller.opponent.field:
			if unit.declared_attack == self:
				return False
		# Flipped units cannot intercept
		if self.flipped:
			return False
		return self.game.step == Step.RESPONSE and \
			self.game.current_player == self.controller.opponent and \
			self.game.choosing_player == self.controller

	def _set_zone(self, value):
		# Only units can go into a player's field.
		if value == Zone.PLAY:
			#if self._summon_index is not None:
			#	self.controller.field.insert(self._summon_index, self)
			#else:
			self.controller.field.append(self)

		if self.zone == Zone.PLAY:
			logging.action_log.log("%r is removed from the field", self)
			self.controller.field.remove(self)
			if self.damage:
				self.damage = 0

		super()._set_zone(value)


	@property
	def update_scripts(self):
		yield from super().update_scripts
		#if (self.heroic)

	def flip(self):
		self.flipped = True

	def unflip(self):
		self.flipped = False

	def attack(self, target):
		self.game.action_block(
			source=self.controller,
			actions=actions.Attack(self, target),
			type=BlockType.ATTACK)


#------------------------------------------------------------------------------
# Spell
#------------------------------------------------------------------------------
class Spell(BaseCard):
	def __init__(self, data):
		#self.immune_to_spellpower = False
		#self.receives_double_spelldamage_bonus = False
		super().__init__(data)

	#def get_damage(self, amount, target):
	#	amount = super().get_damage(amount, target)
	#	if not self.immune_to_spellpower:
	#		amount = self.controller.get_spell_damage(amount)
	#	if self.receives_double_spelldamage_bonus:
	#		amount *= 2
	#	return amount


#------------------------------------------------------------------------------
# Effect
#------------------------------------------------------------------------------
class Effect(BaseCard):
	power = int_property("power")
	#cost = int_property("cost")
	#has_deathrattle = boolean_property("has_deathrattle")
	#incoming_damage_multiplier = int_property("incoming_damage_multiplier")
	max_health = int_property("max_health")
	max_hand_size = int_property("max_hand_size")
	#spellpower = int_property("spellpower")
	inspire	= int_property("inspire")
	spy		= int_property("spy")
	inform	= int_property("inform")

	buffs = []
	slots = []

	def __init__(self, data):
		self.one_turn_effect = False
		self.additional_deathrattles = []
		super().__init__(data)

	@property
	def aftermaths(self):
		#if not self.has_aftermaths:
		#	return []
		#ret = self.additional_deathrattles[:]
		actions = []
		for action in self.get_actions("aftermath"):
			actions.append(action)
		return actions

	def _getattr(self, attr, value):
		value += getattr(self, "_" + attr, 0)
		return getattr(self.data.scripts, attr, lambda s, x: x)(self, value)
		#return i;
		#return getattr(self.data.scripts, attr, lambda s, x: x)(self, i)

	def _set_zone(self, zone):
		if zone == Zone.PLAY:
			self.owner.buffs.append(self)
		elif zone == Zone.REMOVED_FROM_GAME:
			if self.zone == zone:
				# Can happen if a Destroy is queued after a bounce, for example
				logging.action_log.logger.warning("Trying to remove %r which is already gone", self)
				return
			self.owner.buffs.remove(self)
			if self in self.game.active_aura_buffs:
				self.game.active_aura_buffs.remove(self)
		super()._set_zone(zone)

	def apply(self, target):
		logging.action_log.log("Applying %r to %r", self, target)
		self.owner = target
		if hasattr(self.data.scripts, "apply"):
			self.data.scripts.apply(self, target)
		if hasattr(self.data.scripts, "max_health"):
			logging.action_log.log("%r removes all damage from %r", self, target)
			target.damage = 0
		self.zone = Zone.PLAY

	def remove(self):
		self.game.remove_entity(self)

