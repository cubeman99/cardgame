
from .utils import *

def test_setup():
	pass
def test_cleanup():
	pass

#------------------------------------------------------------------------------
# Units
#------------------------------------------------------------------------------

def test_echoing_fiend():
	"""
	Echoing Fiend
	Corrupt: Summon a copy of the destroyed Unit as a token
	"""
	game = Game()
	fiend = game.player1.give("EchoingFiend")
	target = game.player1.give("InfestedWhale", Zone.PLAY)

	# Corrupt the target.
	expect_eq(len(game.player1.field), 1)
	fiend.play(targets=[target])
	expect_eq(len(game.player1.field), 4)

	# Verify there is an exact copy of target, and that it is a token.
	target_copy = [e for e in game.player1.field if e.id == target.id]
	expect_eq(len(target_copy), 1)
	target_copy = target_copy[0]
	expect_eq(target_copy.id, target.id)
	expect_ne(target_copy.entity_id, target.entity_id)
	expect_eq(target.token, False)
	expect_eq(target_copy.token, True)

def test_infested_whale():
	"""
	Infested Whale
	Aftermath: Summon 2 1/1 Tentacles
	"""
	game = Game()
	whale = game.player1.give("InfestedWhale")
	attacker = game.player2.give("SunkenGoliath")
	whale.play()
	attacker.play()

	expect_eq(len(game.player1.field), 1)

	attacker.attack(whale)

	expect_eq(len(game.player1.field), 2)
	expect_eq(whale.zone, Zone.DISCARD)

def test_necrolight_soldier():
	"""
	Corrupt: Deal 2 damage to an enemy unit
	"""
	game = Game()
	target1 = game.player1.give("InfestedWhale").play()
	target2 = game.player2.give("InfestedWhale").play()
	card = game.player1.give("NecrolightSoldier")
	expect(card.corrupts)

	expect_eq(len(game.player1.field), 1)
	expect_eq(len(game.player2.field), 1)
	expect_eq(target2.damage, 0)

	card.play(targets=[target1, target2])

	expect_eq(len(game.player1.field), 3)
	expect_eq(len(game.player2.field), 1)
	expect_eq(target2.damage, 2)

def test_necrolight_follower():
	"""
	Aftermath: return a dead unit to your hand.
	"""
	game = Game()
	card = game.player1.give("NecrolightFollower").play()
	valid_choices = [
		game.player1.give("NecrolightFollower", Zone.DISCARD),
		game.player1.give("NecrolightFollower", Zone.DISCARD),
		game.player1.give("NecrolightFollower", Zone.DISCARD),
	]
	invalid_choices = [
		game.player1.give("NecrolightFollower", Zone.PLAY),
		game.player1.give("NecrolightFollower", Zone.HAND),
		game.player2.give("NecrolightFollower", Zone.DISCARD),
	]
	game.queue_actions(game.player1, [Destroy(card)])
	game.process_deaths()

	expect_true(game.player1.choice != None)
	expect_eq(len(game.player1.choice.cards), 3)
	expect_true(valid_choices[0] in game.player1.choice.cards)
	expect_true(valid_choices[1] in game.player1.choice.cards)
	expect_true(valid_choices[2] in game.player1.choice.cards)
	expect_false(invalid_choices[0] in game.player1.choice.cards)
	expect_false(invalid_choices[1] in game.player1.choice.cards)
	expect_false(invalid_choices[2] in game.player1.choice.cards)
	expect_false(card in game.player1.choice.cards)

def test_elegalths_deputy():
	"""
	Unit: Elegalth's Deputy
	All corrupts, trigger twice while alive, Aftermath: summon a 1/1
	"""
	# Corrupt without extra corrupts
	game = Game()
	target = game.player1.give("PackExile", Zone.PLAY)
	game.player1.give("AbyssalSummoning").play(targets=[target])
	expect_eq(len(game.player1.field), 1)
	expect_eq(game.player1.extra_corrupts, False)

	# Corrupt with extra corrupts
	game = Game()
	expect_eq(game.player1.extra_corrupts, False)
	card = game.player1.give("ElegalthsDeputy").play()
	expect_eq(game.player1.extra_corrupts, True)
	expect_eq(len(game.player1.field), 1)
	target = game.player1.give("PackExile", Zone.PLAY)
	game.player1.give("AbyssalSummoning").play(targets=[target])
	expect_eq(len(game.player1.field), 3)

	# Kill it, verify the aftermath, and verify extra corrupts go away
	game.queue_actions(game.player1, [Destroy(card)])
	game.process_deaths()
	expect_eq(len(game.player1.field), 3)
	game.player1.give("AbyssalSummoning").play(
		targets=[game.player1.field[0]])
	expect_eq(len(game.player1.field), 3)


#------------------------------------------------------------------------------
# Spells
#------------------------------------------------------------------------------

def test_sacrificial_incantation():
	"""
	Spell: Sacrificial Incantation
	Corrupt: deal 5 damage to a unit, gain 1 morale. Every unit corrupted
	allows an additional cast.
	"""
	game = Game()
	game.player1.morale = 10
	expect_eq(len(game.player1.hand), 0)
	card = game.player1.give("SacrificialIncantation")
	expect_eq(len(game.player1.hand), 1)
	expect_eq(card.zone, Zone.HAND)
	expect_eq(game.player1.morale, 10)

	# Play the card, verify it returns to the hand
	# Also verify the two targets die.
	corrupt_target = game.player1.give("PackExile", Zone.PLAY)
	damage_target = game.player2.give("PackExile", Zone.PLAY)
	card.play(targets=[corrupt_target, damage_target])
	expect_eq(len(game.player1.hand), 1)
	expect_eq(card.zone, Zone.HAND)
	expect_eq(game.player1.morale, 8)
	expect_true(corrupt_target.dead)
	expect_true(damage_target.dead)

	# Play the card, verify it returns to the hand
	# Also verify the two targets die.
	corrupt_target = game.player1.give("PackExile", Zone.PLAY)
	damage_target = game.player2.give("PackExile", Zone.PLAY)
	card.play(targets=[corrupt_target, damage_target])
	expect_eq(len(game.player1.hand), 1)
	expect_eq(card.zone, Zone.HAND)
	expect_eq(game.player1.morale, 6)
	expect_true(corrupt_target.dead)
	expect_true(damage_target.dead)

def test_abyssal_summoning():
	"""
	Spell: Abyssal Summoning
	Corrupt: Summon a 5/5 Elgathian, else summon a 3/3 Failure
	"""
	# Play with corrupt target
	game = Game()
	target = game.player1.give("OctopiExile", Zone.PLAY)
	expect_eq(len(game.player1.field), 1)
	card = game.player1.give("AbyssalSummoning")
	card.play(targets=[target])
	expect_eq(len(game.player1.field), 1)
	expect_true(target.dead)
	expect_eq(game.player1.field[0].power, 5)
	expect_eq(game.player1.field[0].health, 5)
	expect_eq(card.zone, Zone.DISCARD)

	# Play without corrupt target
	game = Game()
	expect_eq(len(game.player1.field), 0)
	game.player1.give("AbyssalSummoning").play(targets=[None])
	expect_eq(len(game.player1.field), 1)
	expect_eq(game.player1.field[0].power, 3)
	expect_eq(game.player1.field[0].health, 3)

def test_return_from_the_abyss():
	"""
	Spell: Return From The Abyss
	Select two graveyard cards, return them to your hand.
	"""
	# Play with corrupt target
	game = Game()
	valid_targets = [
		game.player1.give("OctopiExile", Zone.DISCARD),
		game.player1.give("OctopiExile", Zone.DISCARD),
		game.player1.give("OctopiExile", Zone.DISCARD),
	]
	game.player1.give("ReturnFromTheAbyss").play()
	expect_ne(game.player1.choice, None)

	# Verify the cards listed in the choice
	choice = game.player1.choice
	expect_eq(len(valid_targets), 3)
	expect_true(valid_targets[0] in choice.cards)
	expect_true(valid_targets[1] in choice.cards)
	expect_true(valid_targets[2] in choice.cards)

	# Choose two valid targets, and verify they return to hand
	expect_eq(len(game.player1.hand), 0)
	choice.choose(valid_targets[0:2])
	expect_eq(game.player1.choice, None)
	expect_eq(len(game.player1.hand), 2)

