
from .utils import *

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
		power=CONDUIT * 2, max_health=CONDUIT * 2)

ThunderbloodPontiff_Buff = buff(0,0)

class CovenBruiser:
	name	= "Coven Bruiser"
	text	= "Swarm +1/+1, Conduit: +X/+X"
	type	= CardType.UNIT
	tribe	= Tribe.EEL
	cost	= (1, 1)
	stats	= (1, 1)
	swarm	= "CovenBruiser_Swarm"
	emerge	= Buff(SELF, "CovenBruiser_Buff",
		power=CONDUIT, max_health=CONDUIT)

CovenBruiser_Swarm = buff(+1,+1)
CovenBruiser_Buff = buff(0,0)

class VoltitheClergy:
	name	= "Voltithe Clergy"
	text	= "Emerge: Discard 1. Inform. Aftermath: Draw a card"
	type	= CardType.UNIT
	tribe	= Tribe.EEL
	cost	= (0, 1)
	stats	= (3, 4)
	inform	= 1
	emerge	= ChooseAndDiscard(CONTROLLER)
	aftermath = Draw(CONTROLLER)

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

