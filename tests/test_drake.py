
from .utils import *

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

def test_snarling_bailiff():
	"""
	Unit: Snarling Bailiff
	Renew. This Unit has +2/+2 for each Verdict in play.
	"""
	game = Game()
	bailiff = game.player1.give("SnarlingBailiff").play()

	# 0 verdicts in play: 2/2 (no buff)
	expect_eq(len(bailiff.buffs), 0)
	expect_eq(bailiff.power, 2)
	expect_eq(bailiff.health, 2)

	# 1 verdict in play: 4/4
	drake = game.player1.give("BoundDrake").play()
	expect_eq(len(bailiff.buffs), 1)
	expect_eq(bailiff.power, 4)
	expect_eq(bailiff.health, 4)

	# 3 verdicts in play: 8,8
	drake.buff(drake, buff="Verdict_Buff")
	drake2 = game.player2.give("BoundDrake").play()
	expect_eq(len(bailiff.buffs), 1)
	expect_eq(bailiff.power, 8)
	expect_eq(bailiff.health, 8)

	# 1 verdict in play: 4/4
	drake.destroy()
	expect_eq(len(bailiff.buffs), 1)
	expect_eq(bailiff.power, 4)
	expect_eq(bailiff.health, 4)

	# 0 verdicts in play: 2/2 (no buff)
	drake2.destroy()
	expect_eq(len(bailiff.buffs), 0)
	expect_eq(bailiff.power, 2)
	expect_eq(bailiff.health, 2)

#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

