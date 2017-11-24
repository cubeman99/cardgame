


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


class Mechanics(pyunit.TestCase):

	def test_heroic(self):
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

	def test_swarm(self):
		game = Game()

	def test_inspire(self):
		game = Game()

	def test_wisdom(self):
		game = Game()

	def test_muddle(self):
		# Setup the game state.
		game = Game()
		slug = game.player1.give("TomePrinter", Zone.PLAY)
		valid_choices = [
			game.player2.give("TomePrinter"),
			game.player2.give("TomePrinter"),
			game.player2.give("TomePrinter"),
		]
		invalid_choices = [
			slug,
			game.player1.give("TomePrinter"),
			game.player2.give("TomePrinter", Zone.PLAY),
		]
		defender = invalid_choices[2]

		# Attack a player and verify a discard choice begins
		self.expect_true(game.player2.choice == None)
		slug.attack(game.player2)
		self.expect_true(game.player2.choice != None)

		# Verify which cards are in the choice
		choice = game.player2.choice
		self.expect_eq(len(choice.cards), 3)
		self.expect_true(valid_choices[0] in choice.cards)
		self.expect_true(valid_choices[1] in choice.cards)
		self.expect_true(valid_choices[2] in choice.cards)
		self.expect_false(invalid_choices[0] in choice.cards)
		self.expect_false(invalid_choices[1] in choice.cards)
		self.expect_false(invalid_choices[2] in choice.cards)

		# Choose a card and verify it is discarded
		self.expect_eq(valid_choices[0].zone, Zone.HAND)
		choice.choose(valid_choices[0])
		self.expect_eq(game.player2.choice, None)
		self.expect_eq(valid_choices[0].zone, Zone.DISCARD)

		# Attack a unit and verify there is no discard choice
		slug.attack(defender)
		self.expect_true(game.player2.choice == None)

	def test_toxic(self):
		game = Game()

if __name__=="__main__":
	cards.db.initialize()

	#logging.action_log.disable()
	pyunit.run_all_tests(globals())


