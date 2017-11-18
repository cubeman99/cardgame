


from game import Game
from enums import *
from player import Player
import cards
import logic.actions as actions
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
		return
		game = Game()
		whale = game.player1.give("InfestedWhale")
		attacker = game.player2.give("SunkenGoliath")
		whale.play()
		attacker.play()

		self.expect_eq(len(game.player1.field), 1)

		game.action_block(game.player2,
			actions.Attack(attacker, whale), type=BlockType.ATTACK)

		self.expect_eq(len(game.player1.field), 2)
		self.expect_eq(whale.zone, Zone.DISCARD)

	def test_warpack_chieftan(self):
		return
		game = Game()
		chief = game.player1.give("WarpackChieftan")
		chief.play()
		defender = game.player2.give("InfestedWhale")
		defender.play()

		self.expect_eq(defender.health, 3)
		self.expect_eq(game.player1.territory, 0)
		self.expect_eq(len(game.player1.field), 1)

		game.action_block(game.player1,
			actions.Attack(chief, game.player2), type=BlockType.ATTACK)

		self.expect_eq(defender.health, 3)
		self.expect_eq(game.player1.territory, 3)
		self.expect_eq(len(game.player1.field), 2)

		game.action_block(game.player1,
			actions.Attack(chief, defender), type=BlockType.ATTACK)

		self.expect_eq(defender.health, 1)
		self.expect_eq(game.player1.territory, 4)
		self.expect_eq(len(game.player1.field), 3)


class PlayTargets(pyunit.TestCase):

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

class Serialiazation(pyunit.TestCase):

	def test_serialize(self):
		game1 = Game()
		game1.player1.give("OctopiExile")
		c1 = game1.player1.give("OctopiExile").play()
		c2 = game1.player2.give("OctopiExile").play()
		game1.player2.give("OctopiExile").play()
		game1.action_block(game1.player1,
			actions.Attack(c1, c2), type=BlockType.ATTACK)

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


if __name__=="__main__":
	cards.db.initialize()
	pyunit.run_all_tests(globals())
