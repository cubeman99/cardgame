import random
import time
from itertools import chain
from player import Player
from entity import Entity
from card import Unit, Spell, Effect
from manager import GameManager
from utils import CardList
from enums import *
from logic.actions import *
import cards
import json


class Game(Entity):
	Manager = GameManager

	def __init__(self):
		super().__init__()
		self.controller = None
		self.zone = Zone.PLAY
		self.type = CardType.GAME
		self.data = None
		self.removed_entities = []

		players = [
			self.create_card("PlayerCard"),
			self.create_card("PlayerCard"),
		]

		self.turn = 0
		self.turn_counter = 0
		self.play_counter = 0
		self.tick = 0
		self.active_aura_buffs = CardList()

		self.players = players
		self.player1 = self.players[0]
		self.player2 = self.players[1]
		self.player1.name = "Player1"
		self.player2.name = "Player2"
		self.player1.opponent = self.player2
		self.player2.opponent = self.player1
		self.manager.new_entity(self)
		self.game = self
		for player in players:
			player.controller = player
			player.game = self
			self.manager.new_entity(player)

		self.current_player = players[0] # Player whose turn it is.
		self.step_player = players[0] # Player who controls the current step
		self.choosing_player = players[0] # Player who is currently choosing an action or choice
		self.step = Step.PLAY
		#self.state = State.INVALID

	@property
	def id(self):
		return "Game"

	@property
	def name(self):
		return "Game"

	def __str__(self):
		return "Game"

	def __repr__(self):
		return "%s" % (self.__class__.__name__)

	def serialize_state(self):
		state = {}
		for entity in self:
			entity_state = {}
			state[entity.entity_id] = entity_state
			for tag, value in entity.tags.items():
				type = tag.type
				if isinstance(value, str):
					entity_state[tag] = value
				elif type == Type.ENTITY or type == Type.PLAYER:
					if value != None:
						entity_state[tag] = int(value)
					else:
						entity_state[tag] = -1
				else:
					entity_state[tag] = int(value)
		return state

	def deserialize_state(self, state):
		# Clear current state first.
		#self = Game()

		# Create entity objects.
		entities = {}
		for entity_id, tags in state.items():
			type = tags[GameTag.CARD_TYPE]
			entity = None
			if type == CardType.GAME:
				entity = self
			elif type == CardType.PLAYER:
				entity = self.find_entity(entity_id)
			else:
				card_id = tags[GameTag.CARD_ID]
				entity = self.create_card(card_id)
				self.game.manager.new_entity(entity)
				entity.entity_id = entity_id
			if entity:
				entities[entity_id] = entity

		# Deserialize entity tags
		for entity_id, tags in state.items():
			entity = entities[entity_id]

			entity.controller = tags.get(GameTag.CONTROLLER, None)

			for tag, value in tags.items():
				type = tag.type
				if type == Type.ENTITY or type == Type.PLAYER:
					value = entities.get(value, None)
				entity.tags[tag] = value


	# Function to create a card instance of the correct class.
	def create_card(self, id):
		data = cards.db[id]
		subclass = {
			CardType.UNIT:		Unit,
			CardType.SPELL:		Spell,
			CardType.EFFECT:	Effect,
			CardType.PLAYER:	Player,
		}[data.type]
		card = subclass(data)
		return card

	def play_card(self, card, targets=[]):
		type = BlockType.PLAY
		player = card.controller
		actions = [Play(card, targets)]
		return self.action_block(player, actions, type, targets=targets)


	@property
	def non_current_player(self):
		if self.players[0] is self.current_player:
			return self.players[1]
		else:
			return self.players[0]

	# Iterate over all entities
	def __iter__(self):
		return chain(self.entities, self.hands, self.decks, self.discarded)

	@property
	def entities(self):
		#return CardList(chain(self.players[0].entities, self.players[1].entities))
		return CardList(chain([self], self.players[0].entities, self.players[1].entities))

	@property
	def live_entities(self):
		return CardList(chain(self.players[0].live_entities, self.players[1].live_entities))

	@property
	def board(self):
		return CardList(chain(self.players[0].field, self.players[1].field))

	@property
	def decks(self):
		return CardList(chain(self.players[0].deck, self.players[1].deck))

	@property
	def discarded(self):
		return CardList(chain(self.players[0].discarded, self.players[1].discarded))

	@property
	def hands(self):
		return CardList(chain(self.players[0].hand, self.players[1].hand))

	def print_state(self):
		print("GAME STATE:")
		for entity in self:
			print(" %3d. %r" %(entity.entity_id, entity))
		for player in self.players:
			print("  %r" %(player))
			#for entity in player.entities:
			#	print("   %3d. %r" %(entity.entity_id, entity))
			for unit in player.field:
				print("   %3d. %d/%d %s" %(unit.entity_id, unit.power, unit.health, unit.name))

	def action_start(self, type, source, index, targets):
		self.manager.action_start(type, source, index, targets)
		#if type != BlockType.PLAY:
		#	self._action_stack += 1

	def action_end(self, type, source):
		self.manager.action_end(type, source)

#		if self.ended:
#			raise GameOver("The game has ended.")
#
		#if type != BlockType.PLAY:
		#	self._action_stack -= 1
		#if not self._action_stack:
		#	self.log("Empty stack, refreshing auras and processing deaths")
		self.refresh_auras()
		self.process_deaths()

	def action_block(self, source, actions, type, index=-1, targets=None, event_args=None):
		self.action_start(type, source, index, targets)
		if actions:
			ret = self.queue_actions(source, actions, event_args)
		else:
			ret = []
		self.action_end(type, source)
		return ret

	def queue_actions(self, source, actions, event_args=None, event_outputs=None):
		if not isinstance(actions, list):
			actions = [actions]
		source.event_args = event_args
		source.event_outputs = event_outputs
		result = self.trigger_actions(source, actions)
		source.event_outputs = None
		source.event_args = None
		return result

	def trigger_actions(self, source, actions):
		result = []
		for action in actions:
			if isinstance(action, EventListener):
				raise NotImplementedError
			else:
				result.append(action.trigger(source))
		return result

	def trigger(self, source, actions, event_args):
		"""
		Perform actions as a result of an event listener (TRIGGER)
		"""
		return self.action_block(source, actions,
			type=BlockType.TRIGGER, event_args=event_args)

	def find_entity(self, id):
		entity = [e for e in self.game if e.entity_id == id]
		if len(entity) > 0:
			return entity[0]
		return None

	def find_removed_entity(self, id):
		entity = [e for e in self.removed_entities if e.entity_id == id]
		if len(entity) > 0:
			return entity[0]
		return None

	def remove_entity(self, entity):
		"""Remove an entity from the game, changing its zone to
		REMOVED_FROM_GAME"""
		entity.zone = Zone.REMOVED_FROM_GAME
		self.removed_entities.append(entity)

	def process_deaths(self):
		cards = []
		for card in self.live_entities:
			if card.to_be_destroyed:
				cards.append(card)

		actions = []
		if len(cards) > 0:
			self.action_start(BlockType.DEATHS, self, 0, None)
			for card in cards:
				card.zone = Zone.DISCARD
				actions.append(Death(card))
			#self.check_for_end_game()
			self.action_end(BlockType.DEATHS, self)
			self.trigger(self, actions, event_args=None)

	def refresh_auras(self):
		refresh_queue = []
		for entity in self.entities:
			for script in entity.update_scripts:
				refresh_queue.append((entity, script))

		#for entity in self.hands:
		#	for script in entity.data.scripts.Hand.update:
		#		refresh_queue.append((entity, script))

		# Sort the refresh queue by refresh priority (used by eg. Lightspawn)
		#refresh_queue.sort(key=lambda e: getattr(e[1], "priority", 50))
		for entity, action in refresh_queue:
			action.trigger(entity)

		buffs_to_destroy = []
		for buff in self.active_aura_buffs:
			if buff.tick < self.tick:
				buffs_to_destroy.append(buff)
		for buff in buffs_to_destroy:
			buff.remove()

		self.tick += 1

	def begin_turn(self, player):
		ret = self.queue_actions(self, [BeginTurn(player)])
		self.process_deaths()
		self.manager.turn(player)
		return ret

	def end_turn(self, player):
		self.queue_actions(self, [EndTurn(player)])
		self.process_deaths()

	def end_step(self):
		if self.step == Step.DECLARE:
			self.step = Step.RESPONSE
			self.choosing_player = self.current_player.opponent
			self.step_player = self.current_player.opponent
			print("Entering response step for %s" %(self.current_player.opponent))

		elif self.step == Step.RESPONSE:
			self.step = Step.COMBAT
			self.choosing_player = None
			self.step_player = None
			print("Entering combat step for %s" %(self.current_player))

		# Combat step happens automatically
		if self.step == Step.COMBAT:
			self.resolve_combat()

			self.step = Step.PLAY
			self.choosing_player = self.current_player
			self.step_player = self.current_player
			print("Entering play step for %s" %(self.current_player))

		elif self.step == Step.PLAY:
			self.end_turn(self.current_player)

			self.step = Step.UNFLIP
			self.current_player = self.current_player.opponent
			self.choosing_player = None
			self.step_player = None
			self.turn += 1
			print("Entering unflip step for %s" %(self.current_player))
			self.begin_turn(self.current_player)

		# Unflip step happens automatically
		if self.step == Step.UNFLIP:
			self.unflip_units(self.game.current_player)

			self.step = Step.RESOURCE
			self.choosing_player = self.current_player
			self.step_player = self.current_player
			print("Entering resource step for %s" %(self.current_player))
			self.step_player.morale += 1
			self.step_player.supply += 1
			self.step_player.draw(1)

		# TODO: Make resource step not automatic
		if self.step == Step.RESOURCE:
			self.step = Step.DECLARE
			self.choosing_player = self.current_player
			self.step_player = self.current_player
			print("Entering declare step for %s" %(self.current_player))

	def unflip_units(self, player):
		for unit in player.field:
			if unit.flipped:
				unit.unflip()

	def resolve_combat(self):
		print("Resolving all combat")
		attacks = []

		# Gather a list of attacker/defender pairs
		for attacker in self.current_player.field:
			if attacker.declared_attack != None:
				defender = attacker.declared_attack

				# Check for interceptor
				for interceptor in self.current_player.opponent.field:
					if interceptor.declared_intercept == attacker:
						defender = interceptor
						break

				attacks.append((attacker, defender))

		# Clear declared attacks/intercepts.
		for unit in self.board:
			unit.declared_attack = None
			unit.declared_intercept = None

		# Resolve attacks.
		for attacker, defender in attacks:
			self.game.action_block(self.current_player,
				Attack(attacker, defender), type=BlockType.ATTACK)



