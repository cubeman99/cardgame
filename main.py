
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

class CommandResponse:
	INVALID		= -1
	NONE		= 0
	END_GAME	= 1
	NEXT_TURN	= 2
	PRINT_STATE	= 3

horizontal_line = "-" * TERMINAL_WIDTH


test_deck = [
	# Aard
	(1, "PackExile"),
	(1, "RagepackGrowler"),
	(1, "RedmawBerserker"),
	(1, "BlackbloodBruiser"),
	(1, "BonehoarderBrute"),
	(1, "WarpackChieftan"),
	(1, "RageheartThug"),
	(1, "WarlordHeir"),
	(1, "RipperPack"),
	(1, "RageheartScreamer"),
	(1, "WarpackHowler"),
	(1, "RaidpackRally"),
	(1, "Overrun"),

	# Octopi
	(1, "OctopiExile"),
	(1, "InfestedWhale"),
	(1, "EchoingFiend"),
	(1, "ServantOfElagalth"),
	(1, "StarvingCephalopod"),
	(1, "AgileSquirmer"),
	(1, "NecrolightPriestess"),
	(1, "NoxiousTentacle"),
	(1, "ElegalthsChosen"),
	(1, "AbyssalSummoning"),
	(1, "PotentAfterlife"),
	(1, "ExtremePressure"),
]


class TextGame:

	def __init__(self):
		self.game = None
		cards.db.initialize()
		self.done = False
		self.output = ""

	def prepare_game(self):
		#player1 = Player("Player1")
		#player2 = Player("Player2")
		self.game = Game()
		#self.game = Game(players=[player1, player2])
		self.done = False

		self.game.player2.give("TestCard")
		self.game.player2.give("OctopiExile")
		self.game.player2.give("InfestedWhale")
		self.game.player2.give("EchoingFiend")
		self.game.player2.give("UnstableLurker")
		self.game.player2.give("NoxiousTentacle")

		self.game.player1.give("WarlordHeir")
		self.game.player1.give("RipperPack")
		self.game.player1.give("BonehoarderBrute")
		self.game.player1.give("WarpackChieftan")
		self.game.player1.give("RageheartThug")
		self.game.player1.give("TestCard")
		self.game.player1.give("OctopiExile")
		self.game.player1.give("InfestedWhale")
		self.game.player1.give("EchoingFiend")
		self.game.player1.give("ServantOfElagalth")
		self.game.player1.give("StarvingCephalopod")
		self.game.player1.give("AgileSquirmer")
		self.game.player1.give("NecrolightPriestess")
		self.game.player1.give("NoxiousTentacle")
		self.game.player1.give("ElegalthsChosen")
		self.game.player1.give("AbyssalSummoning")
		self.game.player1.give("PotentAfterlife")
		self.game.player1.give("ExtremePressure")

		for item in test_deck:
			for i in range(0, item[0]):
				self.game.player1.card(item[1], zone=Zone.DECK)
				self.game.player2.card(item[1], zone=Zone.DECK)

		self.game.player1.shuffle_deck()
		self.game.player2.shuffle_deck()
		self.game.begin_turn(self.game.player1)

	def play(self):
		print("Playing game!")

		response = CommandResponse.PRINT_STATE

		print("")
		self.print_game_state()
		print("")

		while not self.done:

			# Get the next command.
			done_input = False
			response = CommandResponse.NONE
			while response == CommandResponse.NONE or\
				  response == CommandResponse.INVALID:
				sys.stdout.write("Your action: ")
				text = input()
				response = self.parse_input(text)

			# Begin the next turn
			if response == CommandResponse.NEXT_TURN:
				self.game.begin_turn(self.game.non_current_player)

			# Print the game state.
			if response == CommandResponse.NEXT_TURN or\
				response == CommandResponse.PRINT_STATE:
				print("")
				self.print_game_state()
				print("")

			#if not self.done:
			#	self.game.begin_turn(self.game.non_current_player)
			#self.game.current_player = self.game.non_current_player

	def parse_input(self, text):
		self.output = ""
		args = text.split()
		if len(args) == 0:
			return None
		command = args[0]
		args = args[1:]
		return self.parse_command(command, args)

	def find_entity_by_id(self, id):
		card = [e for e in self.game if str(e.entity_id) == id]
		if len(card) > 0:
			return card[0]
		return None


	def parse_command(self, command, args):
		player = self.game.current_player
		opponent = self.game.non_current_player
		#print(command)
		#print(args)
		if command == "play":
			card = self.find_entity_by_id(args[0])
			targets = []
			if len(args) > 1:
				targets = args[1:]
			if not card:
				print("Card ID '%s' does not exist" %(args[0]))
				return CommandResponse.INVALID
			for i in range(0, len(targets)):
				targets[i] = self.find_entity_by_id(targets[i])
			if len(targets) == 0:
				print("Playing %s" %(card.name))
			else:
				color_print("Playing {card_name}%s{} targeting [" %(card.name))
				first = True
				for target in targets:
					if not first:
						color_print(", ")
					color_print("{card_name}%s{}" %(target.name))
					first = False
				print("]")
		#	self.game.current_player.play(card)
			if len(targets) > 0:
				card.play(target=targets[0])
			else:
				card.play()
			#self.game.action_block(self.game.current_player,
			#	actions.Play(card), type=BlockType.ATTACK)

			#test = IN_HAND.eval(self.game, self.game.current_player)
			#print(test)

		elif command == "corrupt":
			corruptor = self.find_entity_by_id(args[0])
			if not corruptor:
				print("Card ID '%s' does not exist" %(args[0]))
				return CommandResponse.INVALID
			target = self.find_entity_by_id(args[1])
			if not target:
				print("Card ID '%s' does not exist" %(args[1]))
				return CommandResponse.INVALID

			self.game.queue_actions(player, actions.Play(corruptor, None))
			self.game.action_block(player,
				actions.Corrupt(corruptor, target), type=BlockType.ATTACK)

		elif command == "attack":
			attacker = self.find_entity_by_id(args[0])
			if not attacker:
				print("Card ID '%s' does not exist" %(args[0]))
				return CommandResponse.INVALID
			defender = self.find_entity_by_id(args[1])
			if not defender:
				print("Card ID '%s' does not exist" %(args[1]))
				return CommandResponse.INVALID

			self.game.action_block(player,
				actions.Attack(attacker, defender), type=BlockType.ATTACK)

		elif command == "info":
			card = self.find_entity_by_id(args[0])
			if not card:
				print("Card ID '%s' does not exist" %(args[0]))
				return CommandResponse.INVALID

			print(card)

			# Print Scripts:
			print("")
			print("SCRIPTS:")
			print(" * aftermath = %r" %(card.aftermaths))
			print(" * emerge = %r" %(card.emerges))
			print(" * corrupt = %r" %(card.get_all_actions("corrupt")))
			print(" * events = %r" %(card.events))
			print(" * update = %r" %(card.get_actions("update")))
			print("")

			print("BUFFS:")
			for buff in card.buffs:
				print(" %d. %r" %(buff.entity_id, buff))
			print("")

			# Print tags
			print("TAGS:")
			max_name_length = 0
			for key in card.tags.keys():
				max_name_length = max(max_name_length, len(str(key)))
			for key, value in card.tags.items():
				format = "  %%-%ds %%s" %(max_name_length + 2)
				print(format %(str(key) + ":", value))
			print("")

			return CommandResponse.NONE

		elif command == "view":
			if args[0] == "discard":
				print("Opponent's discard pile:")
				self.print_card_list_columns(opponent.discarded)
				print("Your discard pile:")
				self.print_card_list_columns(player.discarded)
				return CommandResponse.NONE
			if args[0] == "deck":
				print("Opponent's deck:")
				self.print_card_list_columns(opponent.deck)
				print("Your deck:")
				self.print_card_list_columns(player.deck)
				return CommandResponse.NONE
			if args[0] == "hand":
				self.print_hand_options(self.game.non_current_player)
				self.print_hand_options(self.game.current_player)
				return CommandResponse.NONE
			if args[0] == "field":
				self.print_field(self.game.non_current_player)
				self.print_field(self.game.current_player)
				return CommandResponse.NONE

		elif command == "help":
			pass # TODO
			return CommandResponse.NONE

		elif command == "end" or command == "done" or command == "pass":
			pass
			return CommandResponse.NEXT_TURN

		elif command == "concede":
			self.done = True
			return CommandResponse.END_GAME

		elif command == "exit":
			self.done = True
			return CommandResponse.END_GAME

		else:
			print("Unknown command '%s'" %(command))
			return False
		return CommandResponse.PRINT_STATE

	def player_pronoun(self, player):
		if player is self.game.current_player:
			return "Your"
		else:
			return "Opponent's"

	def print_player_info(self, player):
		color_print(" %d. {card_name}%s{} - Morale: %d, Supply: %d, Territory: %d. Max-Hand-Size: %d\n" %(
			player.entity_id,
			player.name,
			player.morale,
			player.supply,
			player.territory,
			player.max_hand_size))


	def print_game_state(self):
		print("Turn %d:" %(self.game.turn))
		self.print_player_info(self.game.non_current_player)
		print(horizontal_line)
		self.print_hand_options(self.game.non_current_player)
		print(horizontal_line)
		self.print_field(self.game.non_current_player)
		self.print_field(self.game.current_player)
		print(horizontal_line)
		self.print_hand_options(self.game.current_player)
		print(horizontal_line)
		self.print_deck(self.game.current_player)
		print("")
		self.print_player_info(self.game.current_player)

	def print_field(self, player):
		print("%s field:" %(self.player_pronoun(player)))
		self.print_card_list(player.field)

	def print_deck(self, player):
		print("%s deck:" %(self.player_pronoun(player)))
		self.print_card_list_columns(player.deck)

	def print_hand_options(self, player):
		self.print_card_list(player.hand, "%s hand:" %(self.player_pronoun(player)))

	def print_card_list(self, card_list, name=None):
		if name != None:
			print("%s" %(name))
		if len(card_list) == 0:
			print("  (empty)")

		max_name_length = 1
		for card in card_list:
			max_name_length = max(max_name_length, len(card.data.name))

		for card in card_list:
			id_color = ""
			if card.is_playable():
				id_color = "playable"
			color_print("  {%s}%3d.{} %dm/%ds - " %(
				id_color,
				card.entity_id,
				card.morale,
				card.supply))

			if card.type == CardType.UNIT:
				# Colorize power: buffed = green
				power_color = "default"
				if card.power > card.data.power:
					power_color = "buffed_stat"
				# Colorize health: damaged = red, else buffed = green
				health_color = "default"
				if card.damaged:
					health_color = "damaged_health"
				elif card.max_health > card.data.health:
					health_color = "buffed_stat"

				color_print("{%s}%d{}/{%s}%d{}" %(
					power_color, card.power,
					health_color, card.health
				))
			else:
				sys.stdout.write("   ")

			format = " {card_name}%-" + str(max_name_length) + "s{}  {card_text}%s{}\n"
			color_print(format %(
				card.name,
				card.data.text))

	def print_card_list_columns(self, card_list):
		if len(card_list) == 0:
			print("  (empty)")
		else:
			items = ["%d. %s" %(card.entity_id, card.name) for card in card_list]
			print_in_columns(items)

	def custom_print(self, text):
		self.output += text + "\n"

	def custom_write(self, text):
		self.output += text


def prepare_game():
	cards.db.initialize()
	player1 = Player("Player1")
	player2 = Player("Player2")
	game = Game(players=[player1, player2])
	return game

def test_game():
	game = prepare_game()
	assert game.player1.name == "Player1"
	assert game.player2.name == "Player2"
	game.print_state()
	game.player1.summon(["InfestedWhale", "Token_Tentacle"])
	game.player2.summon(["Token_Tentacle"] * 3)
	game.player1.summon(["OctopiExile"])

	c1 = game.player1.field[2]
	c2 = game.player2.field[0]

	game.print_state()
	game.action_block(game.player1, actions.Attack(c1, c2), type=BlockType.ATTACK)
	game.print_state()
	#unit = game.player1.summon("Tentacle")

	#s = selector.OWNER == selector.OWNER
	#s = selector.OWNER
	#print(s)
	#s.eval(game.entities, c1)


if __name__=="__main__":
	push_color(Colors.DEFAULT)

	import struct

	data = struct.pack("iii", 4, 12, 10)
	print(data)
	print(data[:4])
	print(list(struct.unpack("i", data[:4])))

	#print(struct.unpack('i', fin.read(4)))

	exit()

	try:
		game = TextGame()
		game.prepare_game()
		game.play()
	except KeyboardInterrupt:
		color_print("\n{exception}KeyboardInterrupt, Terminating...{}\n")
		exit(1)
	except Exception as e:
		set_text_color(Colors.EXCEPTION)
		sys.stdout.write(traceback.format_exc())
		sys.stdout.flush()
		exit(1)

	set_text_color(Colors.DEFAULT)



