
from .utils import *


def test_lazy_num():
	game = Game()
	a1 = game.player1.give("OctopiExile", Zone.PLAY)
	a2 = game.player1.give("OctopiExile", Zone.PLAY)
	e1 = game.player2.give("OctopiExile", Zone.PLAY)
	e2 = game.player2.give("OctopiExile", Zone.PLAY)
	e3 = game.player2.give("OctopiExile", Zone.PLAY)

	lzy = Count(ALLIED_UNITS)
	val = 2

	expect_eq(
		lzy.eval(game.player1),
		val)
	expect_eq(
		(lzy + 1).eval(game.player1),
		(val + 1))
	expect_eq(
		(9 + lzy).eval(game.player1),
		(9 + val))
	expect_eq(
		(lzy + lzy).eval(game.player1),
		(val + val))
	expect_eq(
		(lzy - 1).eval(game.player1),
		(val - 1))
	expect_eq(
		(7 - lzy).eval(game.player1),
		(7 - val))
	expect_eq(
		(lzy - lzy).eval(game.player1),
		(val - val))
	expect_eq(
		(lzy * 3).eval(game.player1),
		(val * 3))
	expect_eq(
		(4 * lzy).eval(game.player1),
		(4 * val))
	expect_eq(
		(lzy * lzy).eval(game.player1),
		(val * val))
	expect_eq(
		(-lzy).eval(game.player1),
		(-val))
	expect_eq(
		(lzy == 2).eval(game.player1),
		(val == 2))
	expect_eq(
		(lzy != 2).eval(game.player1),
		(val != 2))
	expect_eq(
		(lzy <= 2).eval(game.player1),
		(val <= 2))
	expect_eq(
		((lzy <= 2) & ~(lzy == 2)).eval(game.player1),
		((val <= 2) and not (val == 2)))

	print("%r" %((lzy <= 2) & ~(lzy == 2)))
	expect_true((lzy == lzy).eval(game.player1))
	expect_false((lzy != lzy).eval(game.player1))

	expect_true(Alive(ALLIED_UNITS).eval(game.player1))
	expect_true(Alive(ALLIED_UNITS).eval(game.player2))
	expect_true(Exists(ALLIED_UNITS).eval(game.player1))
	expect_false(Exists(IN_DISCARD).eval(game.player1))
	expect_true((~Exists(IN_DISCARD)).eval(game.player1))

	"""expect_false((lazy < 2).evaluate(game.player1))
	expect_false((lazy > 2).evaluate(game.player1))
	expect_false((lazy >= 3).evaluate(game.player1))
	expect_false((lazy <= 1).evaluate(game.player1))
	expect_false((lazy == 3).evaluate(game.player1))
	expect_false((lazy != 2).evaluate(game.player1))"""

	#expect_eq(True, Alive(ENEMY_UNITS).evaluate(game.player1))
	#expect_eq(True, Alive(ENEMY_UNITS).evaluate(game.player1))
	#expect_eq(False, Dead(ENEMY_UNITS).evaluate(game.player1))
	#expect_eq(True, Exists(ENEMY_UNITS).evaluate(game.player1))
	#expect_eq(False, Exists(IN_DISCARD).evaluate(game.player1))
	#expect_eq(ALLIED_UNITS.evaluate(game.player1), [a])
	#expect_eq(ENEMY_UNITS.evaluate(game.player1), [b, c])

def test_actions():
	game = Game()
	a = game.player1.give("OctopiExile")
	b = game.player2.give("OctopiExile")
	a.play()
	b.play()
	a.attack(b)


