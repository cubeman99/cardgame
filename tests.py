


from game import Game
from enums import *
from player import Player
import cards
from logic.actions import *
from logic.selector import *
from utils import *
from colors import *
import sys
import random
import os
import traceback
import time
import tests.unit_test_framework as pyunit




class CardTests(pyunit.TestCase):

	def test_infested_whale(self):
		"""
		Aftermath: Summon 2 1/1 Tentacles
		"""
		game = Game()
		whale = game.player1.give("InfestedWhale")
		attacker = game.player2.give("SunkenGoliath")
		whale.play()
		attacker.play()

		self.expect_eq(len(game.player1.field), 1)

		attacker.attack(whale)

		self.expect_eq(len(game.player1.field), 2)
		self.expect_eq(whale.zone, Zone.DISCARD)

	def test_warpack_chieftan(self):
		"""
		When this Unit attacks, put a 1/1 Aard Whelp into play attacking the
		opponent.
		"""
		game = Game()
		chief = game.player1.give("WarpackChieftan")
		chief.play()
		defender = game.player2.give("InfestedWhale")
		defender.play()

		self.expect_eq(defender.health, 3)
		self.expect_eq(game.player1.territory, 0)
		self.expect_eq(len(game.player1.field), 1)

		chief.attack(game.player2)

		self.expect_eq(defender.health, 3)
		self.expect_eq(game.player1.territory, 3)
		self.expect_eq(len(game.player1.field), 2)

		chief.attack(defender)

		self.expect_eq(defender.health, 1)
		self.expect_eq(game.player1.territory, 4)
		self.expect_eq(len(game.player1.field), 3)


	def test_necrolight_soldier(self):
		"""
		Corrupt: Deal 2 damage to an enemy unit
		"""
		game = Game()
		target1 = game.player1.give("InfestedWhale").play()
		target2 = game.player2.give("InfestedWhale").play()
		card = game.player1.give("NecrolightSoldier")
		self.expect(card.corrupts)

		self.expect_eq(len(game.player1.field), 1)
		self.expect_eq(len(game.player2.field), 1)
		self.expect_eq(target2.damage, 0)

		card.play(targets=[target1, target2])

		self.expect_eq(len(game.player1.field), 3)
		self.expect_eq(len(game.player2.field), 1)
		self.expect_eq(target2.damage, 2)

	def test_necrolight_follower(self):
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

		self.expect_true(game.player1.choice != None)
		self.expect_eq(len(game.player1.choice.cards), 3)
		self.expect_true(valid_choices[0] in game.player1.choice.cards)
		self.expect_true(valid_choices[1] in game.player1.choice.cards)
		self.expect_true(valid_choices[2] in game.player1.choice.cards)
		self.expect_false(invalid_choices[0] in game.player1.choice.cards)
		self.expect_false(invalid_choices[1] in game.player1.choice.cards)
		self.expect_false(invalid_choices[2] in game.player1.choice.cards)
		self.expect_false(card in game.player1.choice.cards)


class PlayTargets(pyunit.TestCase):

	def test_play_target(self):
		game = Game()
		card = game.player1.give("AgileSquirmer")
		target = game.player2.give("SunkenGoliath").play()
		target2 = game.player2.give("SunkenGoliath").play()

		self.expect_eq(card.zone, Zone.HAND)
		self.expect_eq(target.damage, 0)

		card.play(targets=[target, target2])

		self.expect_eq(card.zone, Zone.PLAY)
		self.expect_eq(target.damage, 3)


	def test_corrupt_with_additional_target(self):
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

		self.expect_eq(len(play_targets), 2)

		self.expect_eq(len(play_targets[0]), 2)
		self.expect(allied_unit1 in play_targets[0])
		self.expect(allied_unit2 in play_targets[0])
		self.expect(enemy_unit1 not in play_targets[0])
		self.expect(enemy_unit2 not in play_targets[0])

		self.expect_eq(len(play_targets[1]), 4)
		self.expect(allied_unit1 in play_targets[1])
		self.expect(allied_unit2 in play_targets[1])
		self.expect(enemy_unit1 in play_targets[1])
		self.expect(enemy_unit2 in play_targets[1])
		play_targets = card.play_targets

		# Corrupt: Deal 2 damage to an enemy unit
		card = game.player1.give("NecrolightSoldier")
		play_targets = card.play_targets
		self.expect_eq(len(play_targets), 2)

		self.expect_eq(len(play_targets[0]), 2)
		self.expect(allied_unit1 in play_targets[0])
		self.expect(allied_unit2 in play_targets[0])
		self.expect(enemy_unit1 not in play_targets[0])
		self.expect(enemy_unit2 not in play_targets[0])

		self.expect_eq(len(play_targets[1]), 2)
		self.expect(allied_unit1 not in play_targets[1])
		self.expect(allied_unit2 not in play_targets[1])
		self.expect(enemy_unit1 in play_targets[1])
		self.expect(enemy_unit2 in play_targets[1])



	def test_allied_units(self):
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

		self.expect_eq(len(play_targets), 1)
		self.expect_eq(len(play_targets[0]), 2)
		self.expect(valid_target1 in play_targets[0])
		self.expect(valid_target2 in play_targets[0])
		self.expect(invalid_target1 not in play_targets[0])
		self.expect(invalid_target2 not in play_targets[0])

class Serialization(pyunit.TestCase):

	def test_serialize(self):
		game1 = Game()
		game1.player1.give("OctopiExile")
		c1 = game1.player1.give("OctopiExile").play()
		c2 = game1.player2.give("OctopiExile").play()
		game1.player2.give("OctopiExile").play()
		c1.attack(c2)

		state1 = game1.serialize_state()

		game2 = Game()
		game2.deserialize_state(state1)
		state2 = game2.serialize_state()

		# DEBUG: Print out state differences.
		for id, tags1 in state1.items():
			tags2 = state2[id]
			for tag, value1 in tags1.items():
				value2 = tags2[tag]
				if value1 != value2:
					print("%d. %-30s: %-5s  %s == %s" %(id, tag, value1 == value2, value1, value2))
					print(state1[id][GameTag.CARD_ID])
					print(state2[id][GameTag.CARD_ID])

		self.expect_eq(str(state2), str(state1))

class Choosing(pyunit.TestCase):

	def test_choose_action(self):
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

		self.expect(valid_targets[0] in choices)
		self.expect(valid_targets[1] in choices)
		self.expect(invalid_targets[0] not in choices)
		self.expect(invalid_targets[1] not in choices)
		self.expect(invalid_targets[2] not in choices)
		self.expect(card not in choices)

		self.expect_false(choice.dead)
		game.player1.choice.choose(choice)
		self.expect_true(choice.dead)

class Actions(pyunit.TestCase):
	def test_bounce_from_field(self):
		game = Game()
		card = game.player1.give("WarlordHeir").play()
		self.expect_eq(card.zone, Zone.PLAY)
		self.expect_true(card in game.player1.field)
		game.queue_actions(game.player1, [Bounce(card)])
		self.expect_eq(card.zone, Zone.HAND)
		self.expect_true(card in game.player1.hand)

	def test_bounce_from_discard(self):
		game = Game()
		card = game.player1.give("WarlordHeir", zone=Zone.DISCARD)
		self.expect_eq(card.zone, Zone.DISCARD)
		self.expect_false(card in game.player1.hand)
		game.queue_actions(game.player1, [Bounce(card)])
		self.expect_eq(card.zone, Zone.HAND)
		self.expect_true(card in game.player1.hand)


class Keywords(pyunit.TestCase):

	def test_heroic(self):
		"""
		Heroic: Bonuses when sent into combat alone until end of combat.
		"""
		game = Game()

		# Heroic: +5/+4 inspire
		card = game.player1.give("WarlordHeir").play()
		self.expect_eq(card.power, 5)
		self.expect_eq(card.health, 5)
		self.expect_eq(card.inspire, 1)
		self.expect_eq(len(card.buffs), 1)
		self.expect_eq(card.buffs[0].owner, card)
		self.expect_eq(card.buffs[0].source, card)

		game.player1.give("WarlordHeir").play()
		self.expect_eq(card.power, 0)
		self.expect_eq(card.health, 1)
		self.expect_eq(card.inspire, 0)
		self.expect_eq(len(card.buffs), 0)

		# Allied Units gain +2/+1
		game.player1.give("Overrun").play()
		self.expect_eq(card.power, 2)
		self.expect_eq(card.health, 2)
		self.expect_eq(card.inspire, 0)
		self.expect_eq(len(card.buffs), 1)

		# TODO: until end of combat

	def test_swarm(self):
		"""
		Swarm: Bonuses while combat when with 3 allies until end of combat.
		"""
		game = Game()

	def test_muddle(self):
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
		self.expect_true(game.player2.choice == None)
		slug.attack(game.player2)
		self.expect_true(game.player2.choice != None)

		# Verify the choice and which cards it gives
		choice = game.player2.choice
		self.expect_eq(choice.source, slug)
		self.expect_eq(choice.player, game.player2)
		self.expect_eq(choice.type, ChoiceType.GENERAL) # TODO: Discard type
		self.expect_eq(len(choice.cards), 3)
		self.expect_true(valid_choices[0] in choice.cards)
		self.expect_true(valid_choices[1] in choice.cards)
		self.expect_true(valid_choices[2] in choice.cards)
		self.expect_false(invalid_choices[0] in choice.cards)
		self.expect_false(invalid_choices[1] in choice.cards)
		self.expect_false(invalid_choices[2] in choice.cards)

		# Choose a card and verify it is discarded
		hand_size = len(game.player2.hand)
		self.expect_eq(valid_choices[0].zone, Zone.HAND)
		choice.choose(valid_choices[0])
		self.expect_eq(game.player2.choice, None)
		self.expect_eq(valid_choices[0].zone, Zone.DISCARD)
		self.expect_eq(len(game.player2.hand), hand_size - 1)

		# Attack a unit and verify there is no discard choice
		slug.attack(defender)
		self.expect_true(game.player2.choice == None)

	def test_emerge(self):
		"""
		Emerge: Following effect activated when the unit is played.
		"""
		game = Game()

	def test_aftermath(self):
		"""
		Aftermath: Following effect activated on unit’s death.
		"""
		game = Game()

	def test_corrupt(self):
		"""
		Corrupt: You may sacrifice an allied unit to gain an effect. Units
		cannot be sacrificed for multiple purposes.
		"""
		game = Game()

	def test_inspire(self):
		"""
		Inspire X: Gain X extra Morale when this unit attacks a player.
		"""
		game = Game()

	def test_spy(self):
		"""
		Spy: Opponent loses 1 Morale when this Unit attacks them.
		"""
		game = Game()

	def test_inform(self):
		"""
		Inform: Draw a card when this unit damages a player.
		"""
		game = Game()

	def test_wisdom(self):
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
		self.expect_eq(len(card.buffs), 0)
		self.expect_eq(card.power, 1)
		self.expect_eq(card.health, 1)
		self.expect_eq(card.inform, 0)

		# Play a wisdom cards with exactly 5 cards in hand
		game.player1.give("ScholarExile")
		card = game.player1.give("ScholarExile")
		card.play()
		self.expect_eq(len(card.buffs), 1)
		self.expect_eq(card.power, 1)
		self.expect_eq(card.health, 3)
		self.expect_eq(card.inform, 1)

		# Play a wisdom cards with more than 5 cards in hand
		game.player1.give("ScholarExile")
		card = game.player1.give("ScholarExile")
		card.play()
		self.expect_eq(len(card.buffs), 1)
		self.expect_eq(card.power, 1)
		self.expect_eq(card.health, 3)
		self.expect_eq(card.inform, 1)

	def test_toxic(self):
		"""
		Toxic: Units dealt damage in combat drop to 1 health if they would
		survive.
		"""
		game = Game()

	def test_conduit(self):
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
		self.expect_eq(target.damage, 2)

		# Unit: Thunderblood Pontiff
		# Conduit: +2X/+2X
		pontiff = game.player1.give("ThunderbloodPontiff").play()
		self.expect_eq(pontiff.health, 1)
		self.expect_eq(pontiff.power, 1)

		# Opponent's hand should not affect conduit
		game.player2.give("InfestedWhale")
		game.player2.give("InfestedWhale")

		# Play with 1 cards in hand. 2*(1+1) = 4
		game.player1.give("InfestedWhale")
		card = game.player1.give("StaticSnap")
		target = game.player2.give("SunkenGoliath", Zone.PLAY)
		card.play(targets=[target])
		self.expect_eq(target.damage, 4)

		pontiff = game.player1.give("ThunderbloodPontiff").play()
		self.expect_eq(pontiff.health, 3)
		self.expect_eq(pontiff.power, 3)

		# Play with 2 cards in hand. 2*(2+1) = 6
		game.player1.give("InfestedWhale")
		card = game.player1.give("StaticSnap")
		target = game.player2.give("SunkenGoliath", Zone.PLAY)
		card.play(targets=[target])
		self.expect_eq(target.damage, 6)

		pontiff = game.player1.give("ThunderbloodPontiff").play()
		self.expect_eq(pontiff.health, 5)
		self.expect_eq(pontiff.power, 5)


	def test_renew(self):
		"""
		Renew: Unit heals to full at the start of your turn
		"""
		game = Game()

	def test_fury(self):
		"""
		Fury: When this unit attacks or intercepts, it gets +1/+1.
		"""
		game = Game()

	def test_reinforce(self):
		"""
		Reinforce: If you already have a Unit in play of the same type as the
		reinforce card, gain an effect.
		"""
		game = Game()

if __name__=="__main__":
	cards.db.initialize()

	test_list = None
	if len(sys.argv) > 1:
		single_test = sys.argv[1]
		test_list = [single_test]

	#logging.action_log.disable()
	pyunit.run_all_tests(globals(),
		test_list=test_list)


