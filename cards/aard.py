
from enums import *
from cards.card_data import CardData
from cards.utils import *
from logic.events import *
from logic.conditions import *

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

class PackExile:
	name	= "Pack Exile"
	text	= "Fury"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (0, 0)
	stats	= (2, 1)
	fury	= 1

class RagepackGrowler:
	name	= "Ragepack Growler"
	text	= "Swarm: +2/+1"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (0, 0)
	stats	= (1, 2)
	swarm	= "RagepackGrowler_Swarm"

RagepackGrowler_Swarm = buff(+2,+1)

class RedmawBerserker:
	name	= "Redmaw Berserker"
	text	= "When this unit takes damage, destroy it at the end of the turn"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (0, 0)
	stats	= (4, 4)
	events	= Damage(SELF).on(Buff(SELF, "RedmawBerserker_Buff"))

class RedmawBerserker_Buff:
	type	= CardType.EFFECT
	events	= EndTurn(ALL_PLAYERS).on(Destroy(OWNER))

class BlackbloodBruiser:
	name	= "Blackblood Bruiser"
	text	= "Toxic, Fury"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (0, 1)
	stats	= (0, 3)
	toxic	= 1
	fury	= 1

class BonehoarderBrute:
	name	= "Bonehoarder Brute"
	text	= "When this unit kills a unit, it gains +1/+2"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (0, 3)
	stats	= (4, 6)
	events	= Attack(SELF, ALL_UNITS).after(Dead(DEFENDER) & Buff(SELF, "BonehoarderBrute_Buff"))

BonehoarderBrute_Buff = buff(+1,+2)

class WarpackChieftan:
	name	= "Warpack Chieftan"
	text	= "When this Unit attacks, put a 1/1 Aard Whelp into play attacking the opponent."
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (1, 1)
	stats	= (2, 5)
	events	= Attack(SELF, ALL_CHARACTERS).after(
		Summon(CONTROLLER, "WarpackChieftan_Token").then(
		Attack(Summon.CARD, OPPONENT)))
	# TODO: summoned unit must attack the OPPONENT

class WarpackChieftan_Token:
	name	= "Aard Whelp"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (0, 0)
	stats	= (1, 3)

Buff_Fury = buff(+1,+1)

class RageheartThug:
	name	= "Rageheart Thug"
	text	= "Fury"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (1, 1)
	stats	= (2, 4)
	fury	= 1

class WarlordHeir:
	name	= "Warlord Heir"
	text	= "Heroic: +5/+4, Inspire (1)"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (1, 1)
	stats	= (0, 1)
	heroic	= "WarlordHeir_Heroic"

WarlordHeir_Heroic = buff(+5,+4, inspire=1)

class RipperPack:
	name	= "Ripper Pack"
	text	= "Swarm: +2/+2, Emerge: Put a copy of this Unit into play."
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (1, 2)
	stats	= (3, 3)
	swarm	= "RipperPack_Swarm"
	emerge	= Summon(CONTROLLER, ExactCopy(SELF))

RipperPack_Swarm = buff(+2,+2)

class RageheartScreamer:
	name	= "Rageheart Screamer"
	text	= "Aftermath: Give all allied Units Heroic: +2/+2"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (2, 1)
	stats	= (5, 3)
	aftermath	= Buff(ALLIED_UNITS, "RageheartScreamer_Buff")

class RageheartScreamer_Buff:
	heroic = "RageheartScreamer_Buff_Heroic"

RageheartScreamer_Buff_Heroic = buff(+2,+2)

class WarpackHowler:
	name	= "Warpack Howler"
	text	= "Swarm: +4/+3, Emerge: Place two 1/1 Aard units into play"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (2, 2)
	stats	= (2, 3)
	swarm	= "WarpackHowler_Swarm"
	emerge	= Summon(CONTROLLER, "WarpackHowler_Token") * 2

WarpackHowler_Swarm = buff(+4,+3)

class WarpackHowler_Token:
	name	= "Warpack Howler Token"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (0, 0)
	stats	= (1, 1)


#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

class RageheartInitiation:
	name	= "Rageheart Initiation"
	text	= "A Unit gains Fury, or put a 1/1 Aard into play with Fury."
	type	= CardType.SPELL
	tribe	= Tribe.AARD
	cost	= (0, 1)
	play	= Summon(CONTROLLER, "RaidpackRally_Token") * 2

class RageheartInitiation_Choice1:
	name	= "Rageheart Initiation"
	text	= "Give a unit Fury."
	type	= CardType.SPELL
	tribe	= Tribe.AARD
	cost	= (0, 1)
	play	= Buff(TARGET, "RageheartInitiation_Choice1_Buff")

RageheartInitiation_Choice1_Buff = buff(fury=1)

class RageheartInitiation_Choice2:
	name	= "Rageheart Initiation"
	text	= "Put a 1/1 Aard into play with Fury."
	type	= CardType.SPELL
	tribe	= Tribe.AARD
	cost	= (0, 1)
	play	= Summon(CONTROLLER, "RageheartInitiation_Token")

class RageheartInitiation_Token:
	name	= "Aard"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (0, 0)
	stats	= (1, 1)
	fury	= 1

class RaidpackRally:
	name	= "Raidpack Rally"
	text	= "Put two 1/1 Aardwolf into play with Swarm +1/+0"
	type	= CardType.SPELL
	tribe	= Tribe.AARD
	cost	= (1, 1)
	play	= Summon(CONTROLLER, "RaidpackRally_Token") * 2

class RaidpackRally_Token:
	name	= "Warpack Howler"
	text	= "Swarm: +1/+0"
	type	= CardType.UNIT
	tribe	= Tribe.AARD
	cost	= (0, 0)
	stats	= (1, 1)
	swarm	= "RaidpackRally_Token_Swarm"

RaidpackRally_Token_Swarm = buff(+4,+3)

class Overrun:
	name	= "Overrun"
	text	= "Allied Units gain +2/+1"
	type	= CardType.SPELL
	tribe	= Tribe.AARD
	cost	= (1, 1)
	play	= Buff(ALLIED_UNITS, "Overrun_Buff")

Overrun_Buff = buff(+2,+1)

#------------------------------------------------------------------------------
# Test Cards
#------------------------------------------------------------------------------

class PlayerCard:
	name	= "Player"
	text	= "Fury"
	type	= CardType.PLAYER
	tribe	= Tribe.AARD
	morale	= 0
	supply	= 0
	stats	= (0, 100)
	max_hand_size = 6





