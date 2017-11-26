
from .utils import *

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

class TomePrinter:
	name	= "Tome Printer"
	text	= "Your max hand size is increased by one while this Unit is in play."
	type	= CardType.UNIT
	tribe	= Tribe.MOLE
	cost	= (0, 1)
	stats	= (0, 2)
	update	= Refresh(CONTROLLER, buff="TomePrinter_Buff")

TomePrinter_Buff = buff(max_hand_size=+1)

class ScholarExile:
	name	= "Scholar Exile"
	text	= "Wisdom: +0/+2 and Inform"
	type	= CardType.UNIT
	tribe	= Tribe.MOLE
	cost	= (0, 0)
	stats	= (1, 1)
	wisdom	= "ScholarExile_Wisdom"

ScholarExile_Wisdom = buff(+0,+2, inform=1)

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

