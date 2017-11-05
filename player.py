
from card import LiveEntity
from utils import CardList
from entity import Entity, int_property
from enums import *
from manager import PlayerManager


#class

class Player(LiveEntity):
	Manager = PlayerManager

	morale			= int_property("morale")
	supply			= int_property("supply")
	territory		= int_property("territory")
	max_hand_size	= int_property("max_hand_size")

	name = "UNKNOWN"

	def __init__(self, data):
		#self.name = name
		super().__init__(data)
		self._game = None
		self.deck = CardList()
		self.hand = CardList()
		self.discarded = CardList()
		self.field = CardList()
		self.zone = Zone.INVALID
		self.last_card_played = None
		self.controller = self

	@property
	def game(self):
		return self._game

	@game.setter
	def game(self, value):
		self._game = value

	def __str__(self):
		return self.name

	def __repr__(self):
		return self.name

	@property
	def current_player(self):
		return self.game.current_player is self

	@property
	def entities(self):
		for entity in self.field:
			yield entity
			#yield from entity.entities
		yield self

	@property
	def live_entities(self):
		yield from self.field

	@property
	def health(self):
		return 100 # players don't have health

	# Create a new card controlled by this player.
	def card(self, id, source=None, parent=None, zone=Zone.SET_ASIDE):
		#card = self.game.Card(id)
		card = self.game.create_card(id)
		card.controller = self
		card.zone = zone
		card.play_counter = self.game.play_counter
		self.game.play_counter += 1
		if source is not None:
			card.creator = source
		if parent is not None:
			card.parent_card = parent
		self.game.manager.new_entity(card)
		return card

	def prepare_for_game(self):
		#self.summon(self.starting_hero)
		for id in self.starting_deck:
			self.card(id, zone=Zone.DECK)
		self.shuffle_deck()
		#self.playstate = PlayState.PLAYING

		# Draw initial hand (but not any more than what we have in the deck)
		hand_size = min(len(self.deck), self.start_hand_size)
		starting_hand = random.sample(self.deck, hand_size)
		# It's faster to move cards directly to the hand instead of drawing
		for card in starting_hand:
			card.zone = Zone.HAND

		def can_pay_cost(self, card):
			return self.morale >= card.morale_cost and \
				self.supply >= card.supply_cost

	def pay_cost(self, source, amount: int):
		return amount

	def shuffle_deck(self):
		random.shuffle(self.deck)

	def summon(self, cards):
		# If the card argument is a card ID, then create the card instance.
		#if isinstance(card, str):
		#	card = self.card(card, zone=Zone.PLAY)
		#self.game.cheat_action(self, )
		game.queue_actions(self, actions.Summon(self, cards))

	def give(self, card):
		if isinstance(card, str):
			card = self.card(card, zone=Zone.HAND)
		else:
			card.controller = self
			card.zone = Zone.HAND

	def play(self, card):
		card.zone = Zone.PLAY



