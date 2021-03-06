
from .utils import *


# Used by InfestedWhale and ExtremePressure
class Token_Tentacle:
	name	= "Tentacle"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (1, 1)

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

class AgileSquirmer:
	name	= "Agile Squirmer"
	text	= "Emerge: deal 3 damage to an enemy unit, aftermath: summon a 1/3"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (1, 2)
	stats	= (4, 2)
	targets	= [ENEMY_UNITS]
	emerge	= Damage(TARGET, 3)
	aftermath = Summon(CONTROLLER, "AgileSquirmer_Token")

class AgileSquirmer_Token:
	name	= "Agile Squirmer Token"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (1, 3)

class EchoingFiend:
	name	= "Echoing Fiend"
	text	= "Corrupt: Summon a copy of the destroyed Unit as a token"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (1, 1)
	stats	= (2, 4)
	corrupt = Summon(CONTROLLER, ExactCopy(CORRUPTED_UNIT), token=True)

class ElegalthsDeputy:
	name	= "Elegalth's Deputy"
	text	= "All corrupts, trigger twice while alive, Aftermath: summon a 1/1"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (4, 0)
	stats	= (2, 5)
	aftermath	= Summon(CONTROLLER, "ElegalthsDeputy_Token")
	update		= Refresh(CONTROLLER, {GameTag.EXTRA_CORRUPTS: True})

class ElegalthsDeputy_Token:
	name	= "Elegalth's Deputy Token"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (1, 1)

class InfestedWhale:
	name	= "Infested Whale"
	text	= "Aftermath: Summon 2 1/1 Tentacles"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (1, 0)
	stats	= (0, 3)
	aftermath	= Summon(CONTROLLER, ["Token_Tentacle"] * 2)
	events		= [OWN_TURN_BEGIN.on(Damage(SELF, 1))]

class NecrolightFollower:
	name	= "Necrolight Follower"
	text	= "Aftermath: return a dead unit to your hand."
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 1)
	stats	= (2, 3)
	aftermath = Choose(CONTROLLER, DEAD_ALLIED_UNITS - SELF).then(Bounce(Choose.CHOICE))

class NecrolightPriestess:
	name	= "Necrolight Priestess"
	text	= "Emerge: Trigger all aftermaths that are currently in play."
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (4, 0)
	stats	= (3, 5)
	emerge	= Aftermath(ALL_UNITS)

class NecrolightSoldier:
	name	= "Necrolight Soldier"
	text	= "Corrupt: Deal 2 damage to an enemy unit"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (2, 3)
	targets = [ENEMY_UNITS]
	corrupt	= Damage(TARGET[1], 2)

class NoxiousTentacle:
	name = "Noxious Tentacle"
	text = "Aftermath: If killed by a unit, deal 2 damage to it"
	type = CardType.UNIT
	tribe = Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (2, 1)
	aftermath = [
		IfThen(Exists(SOURCE_OF_DEATH & UNITS),
			Damage(SOURCE_OF_DEATH, 2))
	]

class OctopiExile:
	name	= "Octopi Exile"
	text	= "Aftermath: Both players draw a card"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (2, 2)
	aftermath = Draw(ALL_PLAYERS)

class ServantOfElagalth:
	name	= "Servant of Elagalth"
	text	= "Aftermath: Summon a 3/4"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (2, 0)
	stats	= (2, 2)
	aftermath = Summon(CONTROLLER, "ServantOfElagalth_Token")

class ServantOfElagalth_Token:
	name	= "Servant of Elagalth Token"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (3, 4)

StarvingCephalopod_Buff = buff(0,0)

class StarvingCephalopod:
	name	= "Starving Cephalopod"
	text	= "Corrupt: Gain the destroyed unit's stats * 2"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (1, 1)
	stats	= (0, 0)
	corrupt	= Buff(SELF, "StarvingCephalopod_Buff",
		power = POWER(CORRUPTED_UNIT) * 2,
		max_health = HEALTH(CORRUPTED_UNIT) * 2)

class SunkenGoliath:
	name = "Sunken Goliath"
	text = "Aftermath: destroy an enemy unit with less attack"
	type = CardType.UNIT
	tribe = Tribe.OCTOPI
	cost	= (3, 0)
	stats	= (4, 7)
	aftermath = Choose(CONTROLLER, ENEMY_UNITS & (POWER < POWER(SELF))).then(
		Destroy(Choose.CHOICE))

class UnstableLurker:
	name	= "Unstable Lurker"
	text	= "Aftermath: Deal 3 damage to all enemies"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (2, 1)
	stats	= (3, 1)
	aftermath = Damage(ENEMY_UNITS, 3)


#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

class AbyssalSummoning:
	name	= "Abyssal Summoning"
	text	= "Corrupt: Summon a 5/5 Elgathian, else summon a 3/3 Failure"
	type	= CardType.SPELL
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	corrupt			= Summon(CONTROLLER, "AbyssalSummoning_Token_Elgathian")
	corrupt_fail	= Summon(CONTROLLER, "AbyssalSummoning_Token_Failure")

class AbyssalSummoning_Token_Elgathian:
	name	= "Elgathian"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (5, 5)

class AbyssalSummoning_Token_Failure:
	name	= "Failure"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (3, 3)

class ElegalthsChosen:
	name	= "Elegalth's Chosen"
	text	= "Give a friendly unit: Aftermath: Summon a 3/3 hatchling"
	type	= CardType.SPELL
	battle	= 1
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	targets	= [ALLIED_UNITS]
	play	= Buff(TARGET, "ElegalthsChosen_Buff")

class ElegalthsChosen_Buff:
	name	= "Elegalth's Chosen Buff"
	type	= CardType.EFFECT
	aftermath = Summon(CONTROLLER, "ElegalthsChosen_Token")

class ElegalthsChosen_Token:
	name	= "Hatchling"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (3, 3)

class ExtremePressure:
	name	= "Extreme Pressure"
	text	= "Deal 3 damage to a unit, if it lives summon a 2/1 Tentacle"
	type	= CardType.SPELL
	tribe	= Tribe.OCTOPI
	cost	= (0, 1)
	targets	= [ALL_UNITS]
	play = [
		Damage(TARGET, 3),
		IfThen(Alive(TARGET),
			Summon(CONTROLLER, "ExtremePressure_Token"))
	]

class ExtremePressure_Token:
	name	= "Tentacle"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (2, 1)

class Necrosis:
	name	= "Necrosis"
	text	= "Choose a unit, it dies at the start of your next turn, corrupt for immediate effect."
	type	= CardType.SPELL
	tribe	= Tribe.OCTOPI
	cost	= (2, 0)
	# TODO

class PotentAfterlife:
	name	= "Potent Afterlife"
	text	= "Corrupt: Draw 2 cards"
	type	= CardType.SPELL
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	corrupt	= Draw(CONTROLLER) * 2

class ReturnFromTheAbyss:
	name	= "Return from the Abyss"
	text	= "Select two graveyard cards, return them to your hand."
	type	= CardType.SPELL
	tribe	= Tribe.OCTOPI
	cost	= (0, 2)
	play	= Choose(CONTROLLER, ALLIED_DISCARD, 2).then(
				Bounce(Choose.CHOICE))

class SacrificialIncantation:
	name	= "Sacrificial Incantation"
	text	= "Corrupt: deal 5 damage to a unit, gain 1 morale. Every unit corrupted allows an additional cast."
	type	= CardType.SPELL
	tribe	= Tribe.OCTOPI
	cost	= (3, 0)
	targets	= [ALL_UNITS]
	corrupt	= Damage(TARGET[1], 5), GiveMorale(CONTROLLER, 1), Bounce(SELF)

#------------------------------------------------------------------------------
# Test Cards
#------------------------------------------------------------------------------

Buff_Test = buff(+4,+5)

class Token_Test:
	name	= "Test Token"
	type	= CardType.UNIT
	tribe	= Tribe.OCTOPI
	cost	= (0, 0)
	stats	= (1, 1)

#TestCard_Buff = buff(+1,+1)
TestCard_Buff = buff(max_hand_size=+1)

class TestCard:
	name	= "Test Card"
	text	= ""
	type	= CardType.UNIT
	cost	= (0, 0)
	stats	= (1, 1)
	#emerge	= Buff(SELF, "Buff_Test")

	#targets	= [ALL_UNITS, ALL_UNITS]
	#emerge	= Damage(TARGET, 3), Damage(TARGET[1], 2)

	aftermath = Choose(ENEMY_UNITS)#.then(Damage(Choose.CHOICE, 2))


	#emerge = Summon(CONTROLLER, "Token_Tentacle"),\
	#	Exists(ALLIED_DECK) & Summon(CONTROLLER, "Token_Test")
	#draw = Summon(CONTROLLER, "Token_Test")
	#events = [Draw(ALL_PLAYERS).on(Summon(CONTROLLER, "Token_Test"))]
	#events = [OWN_TURN_BEGIN.on(Summon(CONTROLLER, "Token_Tentacle"))]

	#update = Refresh(ALLIED_UNITS, buff="TestCard_Buff")
	#update = Refresh(CONTROLLER, buff="TestCard_Buff")
