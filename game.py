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


class Game(Entity):
	Manager = GameManager

	def __init__(self):
		super().__init__()
		self.controller = None
		self.zone = Zone.PLAY
		self.type = CardType.GAME
		self.data = None

		players = [
			self.create_card("PlayerCard"),
			self.create_card("PlayerCard"),
		]

		self.turn = 0
		self.turn_counter = 0
		self.play_counter = 0
		self.tick = 0
		#self.state = State.INVALID
		self.step = Step.UNFLIP
		self.active_aura_buffs = CardList()

		self.players = players
		self.current_player = players[0]
		self.player1 = players[0]
		self.player2 = players[1]
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

	def __str__(self):
		return "Game"

	def __repr__(self):
		return "%s" % (self.__class__.__name__)

	# Iterate over all entities
	def __iter__(self):
		return chain(self.players, self.hands, self.board, self.decks, self.discarded)
		#return chain(self.entities, self.hands, self.board, self.decks, self.discarded)

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

	def play_card(self, card, target):
		type = BlockType.PLAY
		player = card.controller
		actions = [Play(card, target)]
		return self.action_block(player, actions, type, target=target)


	@property
	def non_current_player(self):
		if self.players[0] is self.current_player:
			return self.players[1]
		else:
			return self.players[0]

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
		#for entity in self.entities:
		#	print(" %3d. %r" %(entity.entity_id, entity))
		for player in self.players:
			print("  %r" %(player))
			#for entity in player.entities:
			#	print("   %3d. %r" %(entity.entity_id, entity))
			for unit in player.field:
				print("   %3d. %d/%d %s" %(unit.entity_id, unit.power, unit.health, unit.name))

	def action_start(self, type, source, index, target):
		self.manager.action_start(type, source, index, target)
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

	def action_block(self, source, actions, type, index=-1, target=None, event_args=None):
		self.action_start(type, source, index, target)
		if actions:
			ret = self.queue_actions(source, actions, event_args)
		else:
			ret = []
		self.action_end(type, source)
		return ret

	def queue_actions(self, source, actions, event_args=None):
		if not isinstance(actions, list):
			actions = [actions]
		source.event_args = event_args
		result = self.trigger_actions(source, actions)
		source.event_args = None
		return result

	def trigger_actions(self, source, actions):
		result = []
		for action in actions:
			result.append(action.trigger(source))
		return result

	def trigger(self, source, actions, event_args):
		"""
		Perform actions as a result of an event listener (TRIGGER)
		"""
		return self.action_block(source, actions,
			type=BlockType.TRIGGER, event_args=event_args)

	@property
	def entities(self):
		return CardList(chain([self], self.players[0].entities, self.players[1].entities))

	@property
	def live_entities(self):
		return CardList(chain(self.players[0].live_entities, self.players[1].live_entities))

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
		self.manager.turn(player)
		return ret

	def end_turn(self):
		return self.queue_actions(self, [EndTurn(self.current_player)])


