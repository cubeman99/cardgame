
from .utils import *


#------------------------------------------------------------------------------
# Keywords
#------------------------------------------------------------------------------

def test_heroic():
	"""
	Heroic: Bonuses when sent into combat alone until end of combat.
	"""
	game = Game()

	# Heroic: +5/+4 inspire
	card = game.player1.give("WarlordHeir").play()
	expect_eq(card.power, 5)
	expect_eq(card.health, 5)
	expect_eq(card.inspire, 1)
	expect_eq(len(card.buffs), 1)
	expect_eq(card.buffs[0].owner, card)
	expect_eq(card.buffs[0].source, card)

	game.player1.give("WarlordHeir").play()
	expect_eq(card.power, 0)
	expect_eq(card.health, 1)
	expect_eq(card.inspire, 0)
	expect_eq(len(card.buffs), 0)

	# Allied Units gain +2/+1
	game.player1.give("Overrun").play()
	expect_eq(card.power, 2)
	expect_eq(card.health, 2)
	expect_eq(card.inspire, 0)
	expect_eq(len(card.buffs), 1)

	# TODO: until end of combat

def test_swarm():
	"""
	Swarm: Bonuses while combat when with 3 allies until end of combat.
	"""
	game = Game()

def test_muddle():
	"""
	Muddle: When this unit damages a player, that player discards a card.
	"""
	# Setup the game state.
	game = Game()
	slug = game.player1.give("IchorExile", Zone.PLAY)
	valid_choices = [
		game.player2.give("IchorExile"),
		game.player2.give("IchorExile"),
		game.player2.give("IchorExile"),
	]
	invalid_choices = [
		slug,
		game.player1.give("IchorExile"),
		game.player2.give("IchorExile", Zone.PLAY),
	]
	defender = invalid_choices[2]

	# Attack a player and verify a discard choice begins
	expect_true(game.player2.choice == None)
	slug.attack(game.player2)
	expect_true(game.player2.choice != None)

	# Verify the choice and which cards it gives
	choice = game.player2.choice
	expect_eq(choice.source, slug)
	expect_eq(choice.player, game.player2)
	expect_eq(choice.type, ChoiceType.GENERAL) # TODO: Discard type
	expect_eq(len(choice.cards), 3)
	expect_true(valid_choices[0] in choice.cards)
	expect_true(valid_choices[1] in choice.cards)
	expect_true(valid_choices[2] in choice.cards)
	expect_false(invalid_choices[0] in choice.cards)
	expect_false(invalid_choices[1] in choice.cards)
	expect_false(invalid_choices[2] in choice.cards)

	# Choose a card and verify it is discarded
	hand_size = len(game.player2.hand)
	expect_eq(valid_choices[0].zone, Zone.HAND)
	choice.choose(valid_choices[0])
	expect_eq(game.player2.choice, None)
	expect_eq(valid_choices[0].zone, Zone.DISCARD)
	expect_eq(len(game.player2.hand), hand_size - 1)

	# Attack a unit and verify there is no discard choice
	slug.attack(defender)
	expect_true(game.player2.choice == None)

def test_emerge():
	"""
	Emerge: Following effect activated when the unit is played.
	"""
	game = Game()

def test_aftermath():
	"""
	Aftermath: Following effect activated on unit’s death.
	"""
	game = Game()

def test_corrupt():
	"""
	Corrupt: You may sacrifice an allied unit to gain an effect. Units
	cannot be sacrificed for multiple purposes.
	"""
	game = Game()

def test_inspire():
	"""
	Inspire X: Gain X extra Morale when this unit attacks a player.
	"""
	game = Game()

def test_spy():
	"""
	Spy: Opponent loses 1 Morale when this Unit attacks them.
	"""
	game = Game()

def test_inform():
	"""
	Inform: Draw a card when this unit damages a player.
	"""
	game = Game()

def test_wisdom():
	"""
	Wisdom: Gain this effect only if you have 5 or more cards in your hand
	when you play this card.
	"""
	game = Game()

	# Give the player 3 cards.
	game.player1.give("ScholarExile")
	game.player1.give("ScholarExile")
	game.player1.give("ScholarExile")

	# Play a wisdom cards with less than 5 cards in hand
	card = game.player1.give("ScholarExile")
	card.play()
	expect_eq(len(card.buffs), 0)
	expect_eq(card.power, 1)
	expect_eq(card.health, 1)
	expect_eq(card.inform, 0)

	# Play a wisdom cards with exactly 5 cards in hand
	game.player1.give("ScholarExile")
	card = game.player1.give("ScholarExile")
	card.play()
	expect_eq(len(card.buffs), 1)
	expect_eq(card.power, 1)
	expect_eq(card.health, 3)
	expect_eq(card.inform, 1)

	# Play a wisdom cards with more than 5 cards in hand
	game.player1.give("ScholarExile")
	card = game.player1.give("ScholarExile")
	card.play()
	expect_eq(len(card.buffs), 1)
	expect_eq(card.power, 1)
	expect_eq(card.health, 3)
	expect_eq(card.inform, 1)

def test_toxic():
	"""
	Toxic: Units dealt damage in combat drop to 1 health if they would
	survive.
	"""
	game = Game()
	attacker = game.player1.give("BreweryServant", Zone.PLAY) # 1/2 Toxic
	defender = game.player2.give("RageheartThug", Zone.PLAY) # 2/4

	# Attack, defender should drop to 1 health
	attacker.attack(defender)
	expect_false(defender.dead)
	expect_eq(defender.health, 1)

	# Attack again, defender should die
	attacker.attack(defender)
	expect_true(defender.dead)


def test_conduit():
	"""
	Conduit: Gain X effect where X is the number of allied units in play
	(if emerge, unit does not count itself)
	"""
	game = Game()

	# Opponent's hand should not affect conduit
	game.player2.give("InfestedWhale")

	# Spell: Static Snap
	# Conduit: Deal 2 damage to a Unit X+1 times.
	# Play with 0 cards in hand. 2*(0+1) = 2
	card = game.player1.give("StaticSnap")
	target = game.player2.give("SunkenGoliath", Zone.PLAY)
	card.play(targets=[target])
	expect_eq(target.damage, 2)

	# Unit: Thunderblood Pontiff
	# Conduit: +2X/+2X
	pontiff = game.player1.give("ThunderbloodPontiff").play()
	expect_eq(pontiff.health, 1)
	expect_eq(pontiff.power, 1)

	# Opponent's hand should not affect conduit
	game.player2.give("InfestedWhale")
	game.player2.give("InfestedWhale")

	# Play with 1 cards in hand. 2*(1+1) = 4
	game.player1.give("InfestedWhale")
	card = game.player1.give("StaticSnap")
	target = game.player2.give("SunkenGoliath", Zone.PLAY)
	card.play(targets=[target])
	expect_eq(target.damage, 4)

	pontiff = game.player1.give("ThunderbloodPontiff").play()
	expect_eq(pontiff.health, 3)
	expect_eq(pontiff.power, 3)

	# Play with 2 cards in hand. 2*(2+1) = 6
	game.player1.give("InfestedWhale")
	card = game.player1.give("StaticSnap")
	target = game.player2.give("SunkenGoliath", Zone.PLAY)
	card.play(targets=[target])
	expect_eq(target.damage, 6)

	pontiff = game.player1.give("ThunderbloodPontiff").play()
	expect_eq(pontiff.health, 5)
	expect_eq(pontiff.power, 5)


def test_renew():
	"""
	Renew: Unit heals to full at the start of your turn
	"""
	game = Game()
	# DraconicTitan: 6/9 Renew
	card = game.player1.give("DraconicTitan", Zone.PLAY)
	card.damage = 5
	expect_eq(card.damage, 5)
	# TODO: begin turn


def test_fury():
	"""
	Fury: When this unit attacks or intercepts, it gets +1/+1.
	"""
	game = Game()

def test_reinforce():
	"""
	Reinforce: If you already have a Unit in play of the same type as the
	reinforce card, gain an effect.
	"""
	game = Game()

def test_verdict():
	"""
	Verdict:
	"""
	game = Game()

#------------------------------------------------------------------------------
# Actions
#------------------------------------------------------------------------------

def test_bounce_from_field():
	game = Game()
	card = game.player1.give("WarlordHeir").play()
	expect_eq(card.zone, Zone.PLAY)
	expect_true(card in game.player1.field)
	game.queue_actions(game.player1, [Bounce(card)])
	expect_eq(card.zone, Zone.HAND)
	expect_true(card in game.player1.hand)

def test_bounce_from_discard():
	game = Game()
	card = game.player1.give("WarlordHeir", zone=Zone.DISCARD)
	expect_eq(card.zone, Zone.DISCARD)
	expect_false(card in game.player1.hand)
	game.queue_actions(game.player1, [Bounce(card)])
	expect_eq(card.zone, Zone.HAND)
	expect_true(card in game.player1.hand)

#------------------------------------------------------------------------------
# Choosing
#------------------------------------------------------------------------------

def test_choose_action():
	game = Game()

	# Aftermath: destroy an enemy unit with less attack
	card = game.player1.give("SunkenGoliath").play()

	valid_targets = [
		game.player2.give("OctopiExile", Zone.PLAY),		# 2 attack
		game.player2.give("UnstableLurker", Zone.PLAY),		# 3 attack
	]
	invalid_targets = [
		game.player2.give("SunkenGoliath", Zone.PLAY),		# 4 attack
		game.player2.give("RageheartScreamer", Zone.PLAY),	# 5 attack
		game.player2.give("WarpackHowler", Zone.PLAY),		# 6 attack (after swarm)
	]

	attacker = game.player2.give("OctopiExile", Zone.PLAY)
	attacker.attack(card)
	attacker = game.player2.give("OctopiExile", Zone.PLAY)
	attacker.attack(card)
	attacker = game.player2.give("OctopiExile", Zone.PLAY)
	attacker.attack(card)
	attacker = game.player2.give("OctopiExile", Zone.PLAY)
	attacker.attack(card)

	choice = game.player1.choice.cards[1]
	choices = game.player1.choice.cards

	expect(valid_targets[0] in choices)
	expect(valid_targets[1] in choices)
	expect(invalid_targets[0] not in choices)
	expect(invalid_targets[1] not in choices)
	expect(invalid_targets[2] not in choices)
	expect(card not in choices)

	expect_false(choice.dead)
	game.player1.choice.choose(choice)
	expect_true(choice.dead)



#------------------------------------------------------------------------------
# Targeting
#------------------------------------------------------------------------------

def test_play_target():
	game = Game()
	card = game.player1.give("AgileSquirmer")
	target = game.player2.give("SunkenGoliath").play()
	target2 = game.player2.give("SunkenGoliath").play()

	expect_eq(card.zone, Zone.HAND)
	expect_eq(target.damage, 0)

	card.play(targets=[target, target2])

	expect_eq(card.zone, Zone.PLAY)
	expect_eq(target.damage, 3)


def test_corrupt_with_additional_target():
	"""Verify the play targets for a card with corrupt begins with allied
	untis"""

	game = Game()

	enemy_unit1 = game.player2.give("OctopiExile")
	enemy_unit1.play()
	enemy_unit2 = game.player2.give("OctopiExile")
	enemy_unit2.play()

	allied_unit1 = game.player1.give("OctopiExile")
	allied_unit1.play()
	allied_unit2 = game.player1.give("OctopiExile")
	allied_unit2.play()

	# Corrupt: deal 5 damage to a unit, gain 1 morale. Every unit
	# corrupted allows an additional cast.
	card = game.player1.give("SacrificialIncantation")
	play_targets = card.play_targets

	expect_eq(len(play_targets), 2)

	expect_eq(len(play_targets[0]), 2)
	expect(allied_unit1 in play_targets[0])
	expect(allied_unit2 in play_targets[0])
	expect(enemy_unit1 not in play_targets[0])
	expect(enemy_unit2 not in play_targets[0])

	expect_eq(len(play_targets[1]), 4)
	expect(allied_unit1 in play_targets[1])
	expect(allied_unit2 in play_targets[1])
	expect(enemy_unit1 in play_targets[1])
	expect(enemy_unit2 in play_targets[1])
	play_targets = card.play_targets

	# Corrupt: Deal 2 damage to an enemy unit
	card = game.player1.give("NecrolightSoldier")
	play_targets = card.play_targets
	expect_eq(len(play_targets), 2)

	expect_eq(len(play_targets[0]), 2)
	expect(allied_unit1 in play_targets[0])
	expect(allied_unit2 in play_targets[0])
	expect(enemy_unit1 not in play_targets[0])
	expect(enemy_unit2 not in play_targets[0])

	expect_eq(len(play_targets[1]), 2)
	expect(allied_unit1 not in play_targets[1])
	expect(allied_unit2 not in play_targets[1])
	expect(enemy_unit1 in play_targets[1])
	expect(enemy_unit2 in play_targets[1])



def test_allied_units():
	game = Game()

	invalid_target1 = game.player2.give("OctopiExile")
	invalid_target2 = game.player2.give("OctopiExile")
	invalid_target1.play()

	valid_target1 = game.player1.give("OctopiExile")
	valid_target2 = game.player1.give("OctopiExile")
	valid_target1.play()
	valid_target2.play()

	card = game.player1.give("ElegalthsChosen")
	play_targets = card.play_targets

	expect_eq(len(play_targets), 1)
	expect_eq(len(play_targets[0]), 2)
	expect(valid_target1 in play_targets[0])
	expect(valid_target2 in play_targets[0])
	expect(invalid_target1 not in play_targets[0])
	expect(invalid_target2 not in play_targets[0])
