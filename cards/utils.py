
from enums import *
from cards.card_data import CardData
from logic.events import *
from logic.conditions import *
from logic.actions import *

def SET(amount):
	return lambda self, i: amount

# Factory Buff class creation helper
def buff(power=0, health=0, inspire=0, **kwargs):
	buff_tags = {}
	buff_tags[GameTag.CARD_TYPE] = CardType.EFFECT
	if power:
		buff_tags[GameTag.POWER] = power
	if health:
		buff_tags[GameTag.HEALTH] = health
	if inspire:
		buff_tags[GameTag.INSPIRE] = inspire

	for tag in GameTag:
		if tag.name.lower() in kwargs.copy():
			buff_tags[tag] = kwargs.pop(tag.name.lower())

	#if "immune" in kwargs:
	#	value = kwargs.pop("immune")
	#	buff_tags[GameTag.CANT_BE_DAMAGED] = value
	#	buff_tags[GameTag.CANT_BE_TARGETED_BY_OPPONENTS] = value

	if kwargs:
		raise NotImplementedError(kwargs)

	class Buff:
		tags = buff_tags

	return Buff