
from enums import *
from cards.card_data import CardData
from cards.utils import *
from logic.events import *
from logic.conditions import *

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

class LastDitchEffort:
	name	= "Last Ditch Effort"
	text	= "Summon 3 1/1 Peasents"
	type	= CardType.SPELL
	tribe	= Tribe.PHEASANT
	cost	= (2, 0)
	play	= Summon(CONTROLLER, "LastDitchEffort_Token") * 3

class LastDitchEffort_Token:
	name	= "Pheasant"
	text	= ""
	type	= CardType.UNIT
	tribe	= Tribe.PHEASANT
	cost	= (0, 0)
	stats	= (1, 1)

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

