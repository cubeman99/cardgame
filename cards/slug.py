
from enums import *
from cards.card_data import CardData
from cards.utils import *
from logic.events import *
from logic.conditions import *

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------


class IchorExile:
	name	= "Ichor Exile"
	text	= "Muddle."
	type	= CardType.UNIT
	tribe	= Tribe.SLUG
	cost	= (0, 0)
	stats	= (1, 2)
	muddle	= 1

class BreweryServant:
	name	= "Brewery Servant"
	text	= "Toxic"
	type	= CardType.UNIT
	tribe	= Tribe.SLUG
	cost	= (0, 0)
	stats	= (1, 2)
	toxic	= 1

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

