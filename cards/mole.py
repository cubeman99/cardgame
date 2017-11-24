
from enums import *
from cards.card_data import CardData
from cards.utils import *
from logic.events import *
from logic.conditions import *

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

TomePrinter_Buff = buff(max_hand_size=+1)

class IchorExile:
	name	= "Ichor Exile"
	text	= "Your max hand size is increased by one while this Unit is in play."
	type	= CardType.UNIT
	tribe	= Tribe.MOLE
	cost	= (0, 1)
	stats	= (0, 2)
	update	= Refresh(CONTROLLER, buff="TomePrinter_Buff")

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

