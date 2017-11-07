
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
import re
import traceback
import socket
from messages import *

#class ServerResponse:
#	INVALID			= 0,


"""
class ClientAction:
	def __init__(self):
		pass

class DeclareAttack(ClientAction):
	ATTACKER = ActionArg()
	DEFENDER = ActionArg()

class Play(ClientAction):
	pass
	CARD = CardArg()
	# Targets...

class Flip(ClientAction):
	pass
	CARD = CardArg()


class Server:

	def __init__(self):
		self.game = None
"""




HOST = ''
PORT = 50007


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

class Server:

	def __init__(self):
		self.game = None
		cards.db.initialize()

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

	def connect(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def run(self):
		"""Run the server"""

		# Bind the socket.
		self.socket.bind((HOST, PORT))
		self.socket.listen(1)

		# Accept client connections.
		conn, addr = self.socket.accept()
		print("Connected by %s" %(str(addr)))
		while 1:
			data = conn.recv(1024)
			if not data:
				break
			self.receive(self.game.player1, data)
			#conn.sendall(data)
		conn.close()

	def receive(self, player, data):
		"""Decode a packet of bytes received from the given player"""
		message = Message()
		message.unpack(data)
		self.decode_message(player, message)

	def decode_message(self, player, message):
		"""Decode a message received from the given player"""

		# Print out the message
		color_print("Received from %s: {yellow}%s{}\n" %("player1", message))

		if message.type == ClientMessage.PLAY:
			card = self.game.find_entity(message.args[0])
			if not card:
				print("Card ID '%s' does not exist" %(message.args[0]))
				return False
			targets = message.args[1:]

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

			if len(targets) > 0:
				card.play(target=targets[0])
			else:
				card.play()
			return True

		elif message.type == ClientMessage.DECLARE_ATTACK:
			attacker = self.game.find_entity(message.args[0])
			defender = self.game.find_entity(message.args[1])
			if not attacker:
				print("Card ID '%s' does not exist" %(message.args[0]))
				return CommandResponse.INVALID
				return False
			if not defender:
				print("Card ID '%s' does not exist" %(message.args[1]))
				return CommandResponse.INVALID
				return False

			self.game.action_block(player,
				actions.Attack(attacker, defender), type=BlockType.ATTACK)
			return True

		elif message.type == ClientMessage.PLAY:
			return False

		elif message.type == ClientMessage.DONE:
			if self.game.current_player == player:
				self.game.begin_turn(self.game.non_current_player)
			else:
				print("It is not your turn!")
				return False
			return True

		else:
			print("Unknown action")
			return False

		return False



if __name__=="__main__":
	server = Server()
	server.prepare_game()
	server.connect()
	server.run()

