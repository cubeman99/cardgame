import operator
import random
from abc import ABCMeta, abstractmethod
from ..enums import *
from ..entity import BaseEntity
from .lazynum import *
from typing import Any, Union, List, Callable, Iterable, Optional, Set
import inspect

# Type aliases
SelectorLike = Union["Selector", LazyNum]
BinaryOp = Callable[[Any, Any], bool]



class Selector(LazyNum):
	name = None

	def __repr__(self):
		return self.get_name()

	def get_name(self):
		if self.name:
			return self.name
		return self.eval_name()

	def eval_name(self):
		if self.name:
			return self.name
		return "UNKNOWN"


	"""
	Selectors take entity lists and returns a sub-list. Selectors
	are closed under addition, subtraction, complementation, and ORing.

	Note that addition means set intersection and OR means set union. For
	convenience, LazyNums can also treated as selectors.

	Set operations preserve ordering (necessary for cards like Echo of
	Medivh, where ordering matters)
	"""

	def select(self, entities: List[BaseEntity], source: BaseEntity) -> List[BaseEntity]:
		return entities

	def eval(self, source):
		return self.select(source.game, source)

	def __add__(self, other: SelectorLike) -> "Selector":
		return SetOpSelector(operator.and_, self, other)

	def __and__(self, other: SelectorLike) -> "Selector":
		return SetOpSelector(operator.and_, self, other)

	def __or__(self, other: SelectorLike) -> "Selector":
		return SetOpSelector(operator.or_, self, other)

	def __neg__(self) -> "Selector":
		# Note that here we define negation in terms of subtraction, and
		# not the other way around, because selectors are implemented using
		# concrete set operations instead of boolean manipulation
		return self.__class__() - self

	def __sub__(self, other: SelectorLike) -> "Selector":
		return SetOpSelector(operator.sub, self, other)

	def __rsub__(self, other: SelectorLike) -> "Selector":
		return other - self

	def __radd__(self, other: SelectorLike) -> "Selector":
		return self + other

	def __ror__(self, other: SelectorLike) -> "Selector":
		return self | other

	def __getitem__(self, val: Union[int, slice]) -> "Selector":
		if isinstance(val, int):
			val = slice(val)
		return SliceSelector(self, val)

class EnumSelector(Selector):
	def __init__(self, tag_enum=None):
		self.tag_enum = tag_enum
		self.name = "<%s>" %(self.tag_enum.name)

	def select(self, entities, source):
		if not self.tag_enum or not hasattr(self.tag_enum, "test"):
			raise RuntimeError("Unsupported enum type {}".format(str(self.tag_enum)))
		return [e for e in entities if self.tag_enum.test(e, source)]

class SelectorEntityValue(metaclass=ABCMeta):
	"""
	SelectorEntityValues can be compared to arbitrary objects LazyNums;
	the comparison's boolean result forms a selector on entities.
	"""
	@abstractmethod
	def value(self, entity, source):
		pass

	def __eq__(self, other) -> Selector:
		return ComparisonSelector(operator.eq, self, other)

	def __gt__(self, other) -> Selector:
		return ComparisonSelector(operator.gt, self, other)

	def __lt__(self, other) -> Selector:
		return ComparisonSelector(operator.lt, self, other)

	def __ge__(self, other) -> Selector:
		return ComparisonSelector(operator.ge, self, other)

	def __le__(self, other) -> Selector:
		return ComparisonSelector(operator.le, self, other)

	def __ne__(self, other) -> Selector:
		return ComparisonSelector(operator.ne, self, other)

class ComparisonSelector(Selector):
	"""
	A ComparisonSelector compares values of entities to
	other values. Lazy values are evaluated at selector runtime.
	"""
	def __init__(self, op: BinaryOp, left: SelectorEntityValue, right):
		self.op = op
		self.left = left
		self.right = right

	def select(self, entities, source):
		right_value = (self.right.evaluate(source)
		   if isinstance(self.right, LazyNum) else self.right)
		return [e for e in entities if
				self.op(self.left.value(e, source), right_value)]

	def eval_name(self):
		if self.op.__name__ == "eq":
			infix = "=="
		elif self.op.__name__ == "gt":
			infix = ">"
		elif self.op.__name__ == "lt":
			infix = "<"
		elif self.op.__name__ == "ge":
			infix = ">="
		elif self.op.__name__ == "le":
			infix = "<="
		elif self.op.__name__ == "ne":
			infix = "!="
		else:
			infix = "UNKNOWN_OP"
		return "(%s %s %s)" % (self.left, infix, self.right)

class SetOpSelector(Selector):
	def __init__(self, op: Callable, left: Selector, right: SelectorLike):
		self.op = op
		self.left = left
		self.right = right

	@staticmethod
	def _entity_id_set(entities: Iterable[BaseEntity]) -> Set[BaseEntity]:
		return set(e.entity_id for e in entities if e)

	def select(self, entities, source):
		left_children = self.left.select(entities, source)
		right_children = self.right.select(entities, source)
		result_entity_ids = self.op(self._entity_id_set(left_children),
									self._entity_id_set(right_children))
		# Preserve input ordering and multiplicity
		return [e for e in entities if e.entity_id in result_entity_ids]

	def eval_name(self):
		name = self.op.__name__
		if name == "and_":
			infix = "&"
		elif name == "or_":
			infix = "|"
		elif name == "sub":
			infix = "-"
		else:
			infix = "UNKNOWN_OP"

		return "(%r %s %r)" % (self.left, infix, self.right)

class AttrValue(SelectorEntityValue):
	def __init__(self, tag):
		self.tag = tag
		#if isinstance(self.tag, str):
		#	self.name = "%s" %(self.tag)
		#else:
		#	self.name = "%s" %(self.tag.name)

	def __repr__(self):
		if isinstance(self.tag, str):
			return "%s" %(self.tag)
		else:
			return "%s" %(self.tag.name)

	#def select(self, source):
	#	return getattr(source, self.tag)

	def value(self, entity, source):
		if isinstance(self.tag, str):
			return getattr(entity, self.tag, 0)
		return entity.tags.get(self.tag, 0)

	def __call__(self, selector):
		"""Convenience function to support uses like ARMOR(SELF)"""
		return Attr(selector, self.tag)


class Controller(LazyNum):
	def __init__(self):
		self.name = "Controller"

	def _get_entity_attr(self, entity):
		return entity.controller

	def evaluate(self, source):
		# If we don't have an argument, we default to SELF
		# This allows us to skip selector evaluation altogether.
		return self._get_entity_attr(source)
		assert len(entities) == 1
		return self._get_entity_attr(entities[0])

	def __repr__(self):
		return "Opponent"


class Opponent(Controller):
	def _get_entity_attr(self, entity):
		return entity.controller.opponent
		self.name = "Opponent"
	def __repr__(self):
		return "Opponent"

class FuncSelector(Selector):
	def __init__(self, func: Callable[[List[BaseEntity], BaseEntity], List[BaseEntity]], name=None):
		"""func(entities, source) returns the results"""
		self.func = func
		self.name = name if name else "<%s>" %(self.__class__.__name__)

	def select(self, entities, source):
		return self.func(entities, source)

# Enum tests
GameTag.test = lambda self, entity, *args: entity is not None and bool(entity.tags.get(self))
CardType.test = lambda self, entity, *args: entity is not None and self == entity.type
Tribe.test = lambda self, entity, *args: entity is not None and self == getattr(entity, "tribe", Tribe.INVALID)
#Rarity.test = lambda self, entity, *args: entity is not None and self == getattr(entity, "rarity", Rarity.INVALID)
Zone.test = lambda self, entity, *args: entity is not None and self == entity.zone
#CardClass.test = lambda self, entity, *args: entity is not None and self == getattr(entity, "card_class", CardClass.INVALID)


def TARGETS(index):
	return FuncSelector(lambda entities, source: [source.targets[index]], name="TARGET[%d]" %(index))

# Functions
SELF			= FuncSelector(lambda entities, source: [source], name="SELF")
ATTACKER		= FuncSelector(lambda entities, source: [source.attacker], name="ATTACKER")
DEFENDER		= FuncSelector(lambda entities, source: [source.defender], name="DEFENDER")
SOURCE_OF_DEATH	= FuncSelector(lambda entities, source: [source.source_of_death], name="SOURCE_OF_DEATH")
OWNER			= FuncSelector(lambda entities, source: [source.owner], name="SOURCE_OF_DEATH")


class Target(Selector):
	def __init__(self, index=0):
		self.index = index
		self.name = "TARGET[%d]" %(self.index)

	def select(self, entities, source):
		return source.targets[self.index]

	def __getitem__(self, index):
		return FuncSelector(lambda entities, source:
				[source.targets[index]],
			name="TARGET[%d]" %(index))

TARGET			= Target(0)
CORRUPTED_UNIT	= Target(0)

# Keywords
INSPIRE     = EnumSelector(GameTag.INSPIRE)
AFTERMATH   = EnumSelector(GameTag.AFTERMATH)
EMERGE      = EnumSelector(GameTag.EMERGE)
WISDOM      = EnumSelector(GameTag.WISDOM)
CORRUPT     = EnumSelector(GameTag.CORRUPT)

# Tribes
OCTOPI		= EnumSelector(Tribe.OCTOPI)
AARD		= EnumSelector(Tribe.AARD)
SLUG		= EnumSelector(Tribe.SLUG)
PHEASANT	= EnumSelector(Tribe.PHEASANT)
MOLE		= EnumSelector(Tribe.MOLE)
EEL			= EnumSelector(Tribe.EEL)
DRAKE		= EnumSelector(Tribe.DRAKE)

# Attributes
CARD_TYPE		= AttrValue("type")
POWER			= AttrValue(GameTag.POWER)
MAX_HEALTH		= AttrValue(GameTag.HEALTH)
HEALTH			= AttrValue("health")
MORALE			= AttrValue(GameTag.MORALE)
SUPPLY			= AttrValue(GameTag.SUPPLY)
INSPIRE			= AttrValue(GameTag.INSPIRE)
VERDICT_COUNT	= AttrValue(GameTag.VERDICT)
VERDICT			= VERDICT_COUNT > 0


#COST = AttrValue(GameTag.COST)
#DAMAGE = AttrValue(GameTag.DAMAGE)
#MANA = AttrValue(GameTag.RESOURCES)
#USED_MANA = AttrValue(GameTag.RESOURCES_USED)
#NUM_ATTACKS_THIS_TURN = AttrValue(GameTag.NUM_ATTACKS_THIS_TURN)

ALLIED	= AttrValue("controller") == Controller()
ENEMY	= AttrValue("controller") == Opponent()

def CONTROLLED_BY(player):
	selector = AttrValue("controller") == player
	selector.name = "CONTROLLED_BY(%r)" %(player)
	return selector

# Zones
IN_PLAY		= EnumSelector(Zone.PLAY)
IN_HAND		= EnumSelector(Zone.HAND)
IN_DECK		= EnumSelector(Zone.DECK)
IN_DISCARD	= EnumSelector(Zone.DISCARD)
KILLED		= EnumSelector(Zone.DISCARD)

# Card Types
PLAYERS			= CARD_TYPE == CardType.PLAYER
UNITS			= CARD_TYPE == CardType.UNIT
SPELLS			= CARD_TYPE == CardType.SPELL
EFFECTS			= CARD_TYPE == CardType.EFFECT
ALL_PLAYERS		= CARD_TYPE == CardType.PLAYER
ALL_UNITS		= IN_PLAY & UNITS
ALL_SPELLS		= CARD_TYPE == CardType.SPELL
ALL_CHARACTERS	= PLAYERS | (UNITS & IN_PLAY)

VERDICTS = VERDICT & EFFECTS
UNITS_WITH_VERDICT = VERDICT & UNITS

CONTROLLER				= ALLIED & PLAYERS
ALLIED_HAND				= IN_HAND & ALLIED
ALLIED_DECK				= IN_DECK & ALLIED
ALLIED_UNITS			= IN_PLAY & ALLIED & UNITS
ALLIED_DISCARD			= IN_DISCARD & ALLIED
DISCARDED_ALLIED_SPELLS	= IN_DISCARD & ALLIED & SPELLS
DISCARDED_ALLIED_UNITS	= IN_DISCARD & ALLIED & UNITS
DEAD_ALLIED_UNITS		= IN_DISCARD & ALLIED & UNITS

OPPONENT		= ENEMY & PLAYERS
ENEMY_HAND		= IN_HAND & ENEMY
ENEMY_DECK		= IN_DECK & ENEMY
ENEMY_UNITS		= IN_PLAY & ENEMY & UNITS

CONDUIT		= Count(ALLIED_HAND)

# Assign names to all custom selectors (using their variable names).
for name, obj in inspect.getmembers(sys.modules[__name__]):
	if isinstance(obj, Selector):
		obj.name = name

#for name, obj in inspect.getmembers(sys.modules[__name__]):
#	if isinstance(obj, Selector):
#		obj.name = name
#		print("%r = %s" %(obj, obj.eval_name()))
