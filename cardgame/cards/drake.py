
from .utils import *


class Verdict_Buff:
	type	= CardType.EFFECT
	power	= -1
	health	= -1
	verdict	= 1

def PlaceVerdict(target):
	"""
	Place a verdict on the targets.
	"""
	return Buff(target, "Verdict_Buff")

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

class AppointedSlayer:
	name	= "Appointed Slayer"
	text	= "At the start of each turn, this Unit becomes an X/X for each Morale you have."
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (1, 0)
	stats	= (0, 2)
	# TODO

class BoundDrake:
	name	= "Bound Drake"
	text	= "Emerge: Place a -1/-1 Verdict on this Unit. Toxic, Renew"
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (0, 0)
	stats	= (1, 3)
	toxic	= 1
	renew	= 1
	emerge	= PlaceVerdict(SELF)

class CourtAdjudicator:
	name	= "Court Adjudicator"
	text	= "Emerge: Place a -1/-1 Verdict on a Unit."
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (0, 1)
	stats	= (2, 4)
	targets = [ALL_UNITS]
	emerge	= PlaceVerdict(TARGET)

class CourtExile:
	name	= "Court Exile"
	text	= "Emerge: Discard 1 from your deck"
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (0, 0)
	stats	= (3, 3)
	emerge	= ChooseAndDiscard(ALLIED_DECK)

class DraconicTitan:
	name	= "Draconic Titan"
	text	= "Renew"
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (3, 1)
	stats	= (6, 9)
	renew	= 1

class DrakbloodAscetic:
	name	= "Drakblood Ascetic"
	text	= "Toxic, Emerge: Give Renew to a Unit"
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (1, 0)
	stats	= (1, 2)
	toxic	= 1
	targets = [ALL_UNITS]
	emerge	= Buff(TARGET, "DrakbloodAscetic_Buff")

class DrakbloodAscetic_Buff:
	type	= CardType.EFFECT
	renew	= 1

class Drakliege:
	name	= "Drakliege"
	text	= "Emerge: Deal 2 damage to all Units with a Verdict"
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (2, 2)
	stats	= (6, 8)
	emerge	= Damage(UNITS_WITH_VERDICT, 2)

class GavelhandPunisher:
	name	= "Gavelhand Punisher"
	text	= "Renew, Emerge: Destroy a unit with a Verdict"
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (1, 3)
	stats	= (4, 7)
	renew	= 1
	targets = [UNITS_WITH_VERDICT]
	emerge	= Destroy(TARGET)

class JusticarBasher:
	name	= "Justicar Basher"
	text	= "Renew, This unit gains +3/+2 while in combat against a unit with a Verdict"
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (1, 2)
	stats	= (3, 4)
	renew	= 1
	update	= IfThen(
		Exists(ENEMY_UNITS & VERDICT),
		Refresh(SELF, buff="JusticarBasher_Buff"))
	# TODO

JusticarBasher_Buff = buff(+3,+2)

class OratorDrake:
	name	= "Orator Drake"
	text	= "Emerge: Move a Verdict from one Unit to another. Inform"
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (2, 0)
	stats	= (2, 5)
	inform	= 1
	# TODO

class SnarlingBailiff:
	name	= "Snarling Bailiff"
	text	= "Renew. This Unit has +2/+2 for each Verdict in play."
	type	= CardType.UNIT
	tribe	= Tribe.DRAKE
	cost	= (1, 2)
	stats	= (2, 2)
	renew	= 1
	update	= IfThen(
		Exists(VERDICTS),
		Refresh(SELF, buff="JusticarBasher_Buff",
			power=Count(VERDICTS) * 2,
			max_health=Count(VERDICTS) * 2))

class SnarlingBailiff_Buff:
	type = CardType.EFFECT

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

class AcquittedOfCharge:
	name	= "Acquitted of Charge"
	text	= "Allied Unit is removed from play, and retuned to play."
	type	= CardType.SPELL
	tribe	= Tribe.DRAKE
	cost	= (0, 1)
	targets	= [ALLIED_UNITS]
	play	= []
	# TODO

class CourtCorruption:
	name	= "Court Corruption"
	text	= "Discard 3 cards from your deck, remove any number of Verdicts"
	type	= CardType.SPELL
	tribe	= Tribe.DRAKE
	cost	= (1, 0)
	play	= []
	# TODO

class CourtProceedings:
	name	= "Court Proceedings"
	text	= "Place a -1/-1/ Verdict on all Units"
	type	= CardType.SPELL
	tribe	= Tribe.DRAKE
	cost	= (0, 2)
	play	= PlaceVerdict(ALL_UNITS)

class CourtRecess:
	name	= "Court Recess"
	text	= "Remove all Verdicts, deal 1 damage to all Units for each removed Verdict"
	type	= CardType.SPELL
	tribe	= Tribe.DRAKE
	cost	= (2, 1)
	play	= []
	# TODO

class DraconicSubmission:
	name	= "Draconic Submission"
	text	= "Target Unit can't Flip"
	type	= CardType.SPELL
	tribe	= Tribe.DRAKE
	cost	= (1, 0)
	play	= []
	# TODO

class DrakbloodInitiation:
	name	= "Drakblood Initiation"
	text	= "Give Renew and Toxic to a Unit, or place a 2/2 Unit with a -1/-1 Verdict and Toxic."
	type	= CardType.SPELL
	tribe	= Tribe.DRAKE
	cost	= (1, 1)
	play	= []
	# TODO

class Hammerfall:
	name	= "Hammerfall"
	text	= "Place a -1/-1/ Verdict on up to two Units."
	type	= CardType.SPELL
	tribe	= Tribe.DRAKE
	cost	= (0, 1)
	play	= []
	# TODO

class OwnershipOfTheCourt:
	name	= "Ownership of the Court"
	text	= "Take control of a Unit with a Verdict"
	type	= CardType.SPELL
	tribe	= Tribe.DRAKE
	cost	= (2, 1)
	play	= []
	# TODO

class PublicExecution:
	name	= "Public Execution"
	text	= "Destroy an allied Unit, Gain 1 Moral, and take a draw step if the Unit had a Verdict"
	type	= CardType.SPELL
	tribe	= Tribe.DRAKE
	cost	= (0, 0)
	play	= []
	# TODO



