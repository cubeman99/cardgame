
from .utils import *

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

class BreweryServant:
	name	= "Brewery Servant"
	text	= "Toxic"
	type	= CardType.UNIT
	tribe	= Tribe.SLUG
	cost	= (0, 0)
	stats	= (1, 2)
	toxic	= 1

class ContaminantMatriarch:
	name	= "Contaminant Matriarch"
	text	= "Toxic, Muddle, Inform"
	type	= CardType.UNIT
	tribe	= Tribe.SLUG
	cost	= (2, 2)
	stats	= (1, 7)
	toxic	= 1
	muddle	= 1
	inform	= 1

class FumeSpewer:
	name	= "Fume Spewer"
	text	= "Emerge: Give a Unit -1/0 and Toxic"
	type	= CardType.UNIT
	tribe	= Tribe.SLUG
	cost	= (0, 1)
	stats	= (2, 4)
	targets	= [ALL_UNITS - SELF]
	emerge	= Buff(TARGET, "FumeSpewer_Buff")

FumeSpewer_Buff = buff(-1,0, toxic=1)

class IchorExile:
	name	= "Ichor Exile"
	text	= "Muddle"
	type	= CardType.UNIT
	tribe	= Tribe.SLUG
	cost	= (0, 0)
	stats	= (1, 2)
	muddle	= 1

# TODO: IchorSeductress

class IchorbloomHypnotist:
	name	= "Ichorbloom Hypnotist"
	text	= "Muddle, Inform, Emerge: Return a Unit to its owner's hand"
	type	= CardType.UNIT
	tribe	= Tribe.SLUG
	cost	= (2, 1)
	stats	= (2, 4)
	muddle	= 1
	inform	= 1
	targets	= [ALL_UNITS - SELF]
	emerge	= Bounce(TARGET)

# TODO: IchorwellBinger

# TODO: SlickskinConspirator

# TODO: SlickskinDeviant

class SlickskinInhibitress:
	name	= "Slickskin Inhibitress"
	text	= "Toxic. While in play, players' max hand size is reduced by 1."
	type	= CardType.UNIT
	tribe	= Tribe.SLUG
	cost	= (2, 0)
	stats	= (1, 5)
	toxic	= 1
	update	= Refresh(CONTROLLER, buff="SlickskinInhibitress_Buff")

SlickskinInhibitress_Buff = buff(max_hand_size=-1)

# TODO: Slimeshifter

class TorpidMaiden:
	name	= "Torpid Maiden"
	text	= "Muddle, When you discard a card, this unit gains 0/+1"
	type	= CardType.UNIT
	tribe	= Tribe.SLUG
	cost	= (1, 0)
	stats	= (2, 2)
	muddle	= 1
	events	= Discard(CONTROLLER).on(Buff(SELF, buff="TorpidMaiden_Buff"))

TorpidMaiden_Buff = buff(+0,+1)

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

# TODO: AwashInHaze
class AwashInHaze:
	name	= "Awash in Haze"
	text	= "Give all Units -3/0 Until the next turn"
	type	= CardType.SPELL
	tribe	= Tribe.SLUG
	cost	= (1, 0)
	stats	= (2, 2)
	muddle	= 1
	play	= Buff(ALL_UNITS, buff="AwashInHaze_Buff")

AwashInHaze_Buff = buff(-3,0)

class DrinkDeep:
	name	= "Drink Deep"
	text	= "Give a Unit -0/-1 and Toxic"
	type	= CardType.SPELL
	tribe	= Tribe.SLUG
	cost	= (0, 0)
	targets	= [ALL_UNITS]
	play	= Buff(TARGET, "DrinkDeep_Buff")

DrinkDeep_Buff = buff(-0,-1, toxic=1)

# TODO: MireDeluge

# TODO: BrainBoil

class ContaminantStupor:
	name	= "Contaminant Stupor"
	text	= "Reduce a Unit's power to 0."
	type	= CardType.SPELL
	tribe	= Tribe.SLUG
	cost	= (0, 0)
	targets	= [ALL_UNITS]
	play	= Buff(TARGET, "ContaminantStupor_Buff")

class ContaminantStupor_Buff:
	type	= CardType.EFFECT
	power	= SET(0)

# TODO: IchorbloomInitiation

# TODO: Overdose

class PsychoCorrosion:
	name	= "Psycho Corrosion"
	text	= "Deal 2 damage to a Unit, opponent discards two cards from their deck if it dies."
	type	= CardType.SPELL
	tribe	= Tribe.SLUG
	cost	= (0, 1)
	targets	= [ALL_UNITS]
	play	= [
		Damage(TARGET, 2),
		IfThen(Dead(TARGET),
			Choose(OPPONENT, ENEMY_DECK).then(Discard(Choose.CHOICE)))
	]


