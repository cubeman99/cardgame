from enums import CardType, GameTag, Step, Zone, Type, OptionType
import card_details

PLAYABLE_CARD_TYPES = [
	CardType.UNIT,
	CardType.SPELL
]

def tag_attribute(tag, default=0):
	@property
	def func(self):
		return self.tags.get(tag, default)

	return func

class Entity:
	_args = ()
	#name = tag_attribute(GameTag.NAME)
	#name = tag_attribute(GameTag.NAME, "")
	text = tag_attribute(GameTag.TEXT)
	power = tag_attribute(GameTag.POWER)
	max_health = tag_attribute(GameTag.HEALTH)
	damage = tag_attribute(GameTag.DAMAGE)
	#max_health = tag_attribute(GameTag.MAX_HEALTH)
	morale = tag_attribute(GameTag.MORALE)
	supply = tag_attribute(GameTag.SUPPLY)
	zone = tag_attribute(GameTag.ZONE, Zone.INVALID)
	name = tag_attribute(GameTag.NAME)

	def __init__(self, id):
		self.id = id
		self.game = None
		self.tags = {}
		self._initial_controller = 0

	def __repr__(self):
		return "%s(id=%r, %s)" % (
			self.__class__.__name__, self.id,
			", ".join("%s=%r" % (k, getattr(self, k)) for k in self._args)
		)

	@property
	def health(self):
		return self.max_health - self.damage

	@property
	def controller(self):
		return self.game.find_entity_by_id(self.tags.get(GameTag.CONTROLLER, 0))

	@property
	def owner(self):
		return self.game.find_entity_by_id(self.tags.get(GameTag.OWNER, 0))

	@property
	def buffs(self):
		"""Return the buffs applied to this entity."""
		for e in self.game.entities:
			if e.type == CardType.EFFECT and e.owner == self and e.zone == self.zone:
				yield e

	def is_tag_buffed(self, tag):
		return self.get_tag_buff_amount(tag) > 0

	def is_tag_debuffed(self, tag):
		return self.get_tag_buff_amount(tag) < 0

	def get_tag_buff_amount(self, tag):
		"""Returns the amount by which a tag is currently being adjusted due
		to buffs."""
		if GameTag(tag).type != Type.NUMBER:
			return 0
		value = 0
		for buff in self.buffs:
			value += buff.tags.get(tag, 0)
		return value

	@property
	def initial_controller(self):
		return self.game.get_player(
			self._initial_controller or self.tags.get(GameTag.CONTROLLER, 0)
		)

	@property
	def type(self):
		return self.tags.get(GameTag.CARD_TYPE, CardType.INVALID)

	@property
	def zone(self):
		return self.tags.get(GameTag.ZONE, Zone.INVALID)

	def tag_change(self, tag, value):
		if tag == GameTag.CONTROLLER and not self._initial_controller:
			self._initial_controller = self.tags.get(GameTag.CONTROLLER, value)
		self.tags[tag] = value

class Option:
	def __init__(self, type, args):
		self.type = OptionType(type)
		self.targets = args.get("Targets", [])
		self.entity_id = args.get("ID", None)

	def __str__(self):
		# Type
		text = "%s" %(self.type.name.lower())
		# Make first letter uppercase.
		text = text[0].upper() + text[1:]
		# Entity
		if self.entity_id != None:
			text += " entity %d" %(self.entity_id)
		# Targets
		if len(self.targets) > 0:
			if len(self.targets) > 1 or self.targets[0] != None:
				text += " targeting"
				i = 0
				for target in self.targets:
					if i > 0:
						text += ","
					if i > 0 and i == len(self.targets) - 1:
						text += " or"
					if target != None:
						text += " %s" %(target)
					else:
						text += " (no target)"
					i += 1
		return text

class Game(Entity):
	_args = ("players", )
	can_be_in_deck = False

	def __init__(self, id):
		super(Game, self).__init__(id)
		self.players = []
		self.entities = []
		self.initial_entities = []
		self.options = []
		#self.initial_state = State.INVALID
		self.initial_step = Step.INVALID

	@property
	def current_player(self):
		"""Return the player whose turn it is"""
		for player in self.players:
			if player.tags.get(GameTag.CURRENT_PLAYER):
				return player

	@property
	def first_player(self):
		"""Return the player who goes first"""
		for player in self.players:
			if player.tags.get(GameTag.FIRST_PLAYER):
				return player

	@property
	def setup_done(self):
		return True
		#return self.tags.get(GameTag.NEXT_STEP, 0) > Step.BEGIN_MULLIGAN

	def get_player(self, value):
		"""Find a player by name"""
		for player in self.players:
			if value == player.name:
				return player

	def in_zone(self, zone):
		"""Iterate entities in a specific zone"""
		for entity in self.entities:
			if entity.zone == zone:
				yield entity

	def create(self, tags):
		"""Create the game"""
		self.tags = dict(tags)
		#self.initial_state = self.tags.get(GameTag.STATE, State.INVALID)
		self.initial_step = self.tags.get(GameTag.STEP, Step.INVALID)
		self.register_entity(self)

	def create_card(self, entity_id, card_id, tags):
		card = Card(entity_id, card_id)
		card.tags.update(tags)
		self.register_entity(card)
		return card

	def register_entity(self, entity):
		"""Register a single entity into the game"""
		entity.game = self
		self.entities.append(entity)
		if isinstance(entity, Player):
			self.players.append(entity)
		elif not self.setup_done:
			self.initial_entities.append(entity)

	def find_entity_by_id(self, id):
		"""Find an entity by it's entity ID"""
		# int() for LazyPlayer mainly...
		id = int(id)

		#if id <= len(self.entities):
		#	entity = self.entities[id - 1]
		#	if entity.id == id:
		#		return entity

		# Entities are ordered by ID... usually. It is NOT safe to assume
		# that the entity is missing if we went past the ID. So this is the fallback.
		for entity in self.entities:
			if entity.id == id:
				return entity


class Player(Entity):
	_args = ("name", )
	UNKNOWN_HUMAN_PLAYER = "UNKNOWN HUMAN PLAYER"
	can_be_in_deck = False
	territory = tag_attribute(GameTag.TERRITORY)

	def __init__(self, id):
		super(Player, self).__init__(id)
		#self.player_id = player_id
		#self.account_hi = hi
		#self.account_lo = lo
		#self.name = name
		self.card_id = ""

	def __str__(self):
		return self.name or ""

	@property
	def names(self):
		"""
		Returns the player's name and real name.
		Returns two empty strings if the player is unknown.
		AI real name is always an empty string.
		"""
		if self.name == self.UNKNOWN_HUMAN_PLAYER:
			return "", ""

		if " " in self.name:
			return "", self.name

		return self.name, ""

	@property
	def initial_deck(self):
		for entity in self.game.initial_entities:
			if entity.initial_controller != self:
				continue
			# Exclude entity types that cannot be in the deck
			if not entity.can_be_in_deck:
				continue
			# Exclude choice cards, The Coin, Malchezaar legendaries
			if entity.tags.get(GameTag.CREATOR, 0):
				continue
			yield entity

	@property
	def hand(self):
		for entity in self.entities:
			if entity.zone == Zone.HAND:
				yield entity

	@property
	def deck(self):
		for entity in self.entities:
			if entity.zone == Zone.DECK:
				yield entity

	@property
	def field(self):
		for entity in self.entities:
			if entity.zone == Zone.PLAY and entity.type == CardType.UNIT:
				yield entity

	@property
	def entities(self):
		for entity in self.game.entities:
			if entity.controller == self:
				yield entity

	@property
	def hero(self):
		entity_id = self.tags.get(GameTag.HERO_ENTITY, 0)
		if entity_id:
			return self.game.find_entity_by_id(entity_id)
		else:
			# Fallback that should never trigger
			for entity in self.in_zone(Zone.PLAY):
				if entity.type == CardType.HERO:
					return entity

	#@property
	#def heroes(self):
	#	for entity in self.entities:
	#		if entity.type == CardType.HERO:
	#			yield entity
	#
	#@property
	#def starting_hero(self):
	#	heroes = list(self.heroes)
	#	if not heroes:
	#		return
	#	return heroes[0]

	def in_zone(self, zone):
		for entity in self.entities:
			if entity.zone == zone:
				yield entity


class Card(Entity):
	_args = ("card_id", )

	def __init__(self, id, card_id):
		super(Card, self).__init__(id)
		self.initial_card_id = card_id
		self.card_id = card_id
		self.revealed = False
		self.data = card_details.find(card_id)
		self.tags = {}
		self.tags.update(self.data.tags)

	@property
	def options(self):
		"""Return a list of options this entity has."""
		for option in self.game.options:
			if option.entity_id == self.id:
				yield option

	@property
	def can_be_in_deck(self):
		card_type = self.type
		if not card_type:
			# If we don't know the card type, assume yes
			return True
		elif card_type == CardType.HERO:
			# The card set is not available, use a hardcoded list for now...
			return self.card_id in PLAYABLE_HERO_CARD_IDS
			# return self.tags.get(GameTag.CARD_SET, 0) not in (CardSet.CORE, CardSet.HERO_SKINS)

		return card_type in PLAYABLE_CARD_TYPES

	def reveal(self, id, tags):
		self.revealed = True
		self.card_id = id
		if self.initial_card_id is None:
			self.initial_card_id = id
		self.tags.update(tags)

	def hide(self):
		self.revealed = False

	def change(self, card_id, tags):
		self.card_id = card_id
		self.tags.update(tags)
