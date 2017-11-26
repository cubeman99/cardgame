
from .utils import *

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

def test_warpack_chieftan():
	"""
	Warpack Chieftan
	When this Unit attacks, put a 1/1 Aard Whelp into play attacking the
	opponent.
	"""
	game = Game()
	chief = game.player1.give("WarpackChieftan")
	chief.play()
	defender = game.player2.give("InfestedWhale")
	defender.play()

	expect_eq(defender.health, 3)
	expect_eq(game.player1.territory, 0)
	expect_eq(len(game.player1.field), 1)

	chief.attack(game.player2)

	expect_eq(defender.health, 3)
	expect_eq(game.player1.territory, 3)
	expect_eq(len(game.player1.field), 2)

	chief.attack(defender)

	expect_eq(defender.health, 1)
	expect_eq(game.player1.territory, 4)
	expect_eq(len(game.player1.field), 3)

def test_redmaw_berserker():
	"""
	Unit: Redmaw Berserker
	When this unit takes damage, destroy it at the end of the turn
	"""
	game = Game()
	berserker = game.player1.give("RedmawBerserker").play()
	attacker = game.player2.give("PackExile").play()

	# Damage the berserker and verify it receives a buff
	expect_eq(len(berserker.buffs), 0)
	attacker.attack(berserker)
	expect_eq(len(berserker.buffs), 1)

	# End the turn and verify the berserker is destroyed
	expect_false(berserker.dead)
	game.end_turn(game.player1)
	expect_true(berserker.dead)

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

