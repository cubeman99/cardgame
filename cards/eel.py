
from enums import *
from cards.card_data import CardData
from cards.utils import *
from logic.events import *
from logic.conditions import *

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

class StaticSnap:
	name	= "Static Snap"
	text	= "Conduit: Deal 2 damage to a Unit X+1 times."
	type	= CardType.SPELL
	tribe	= Tribe.EEL
	cost	= (1, 2)
	targets	= [ALL_UNITS]
	play	= Damage(TARGET, 2) * (CONDUIT + 1)

class ThunderbloodPontiff:
	name	= "Thunderblood Pontiff"
	text	= "Conduit: +2X/+2X"
	type	= CardType.UNIT
	tribe	= Tribe.EEL
	cost	= (3, 1)
	stats	= (1, 1)
	emerge	= Buff(SELF, "ThunderbloodPontiff_Buff",
		power=CONDUIT * 2,
		max_health=CONDUIT * 2)

ThunderbloodPontiff_Buff = buff(0,0)

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

