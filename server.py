
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
from threading import Thread
#from SocketServer import ThreadingMixIn


class ClientThread(Thread):

	def __init__(self, server, player, connection, ip, port):
		Thread.__init__(self)
		self.server = server
		self.player = player
		self.connection = connection
		self.ip = ip
		self.port = port

	def run(self):
		"""Run the client thread"""
		while True:
			data = self.connection.recv(2048)
			if not data:
				break
			self.server.receive_data(self.player, data)

	def send_message(self, message):
		data = message.pack()
		self.send_data(data)

	def send_data(self, data):
		print("Sending to %s: %d bytes" %(self.player, len(data)))
		# Prefix each message with a 4-byte length (network byte order)
		data = struct.pack('i', len(data)) + data
		self.connection.send(data)


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

test_deck = []

class Server:

	def __init__(self):
		self.game = None
		self.connections = []
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
		self.game.player1.hand[0].play()

		self.game.print_state()

	def bind(self):
		"""Bind the server to an address"""
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((HOST, PORT))

	def run(self):
		"""Run the server"""

		# Accept client connections.
		while True:
			self.socket.listen(4)

			self.socket.listen(1)
			conn, (ip, port) = self.socket.accept()

			# Find a player that hasn't Connected
			thread_player = None
			for player in self.game.players:
				success = True
				for thread in self.connections:
					if thread.player == player:
						success = False
						break
				if success:
					thread_player = player
					break

			if not thread_player:
				print("Error: a client tried to connect but game is full")
				data = Message(ServerMessage.GAME_FULL).pack()
				conn.send_data(data)
				conn.close()
			else:
				print("%s has connected!" %(thread_player))
				thread_player.connection = conn
				thread = ClientThread(self, thread_player, conn, ip, port)
				thread.start()
				#thread.send_message(Message(ServerMessage.GAME_FULL))
				self.connections.append(thread)

				data = MessageData(ServerMessage.CREATE_GAME)
				data.write_int(data.type)
				entities = []
				for entity in self.game:
					entities.append((entity.entity_id, entity.tags))
				data.write_game_state(entities)
				thread.send_data(data.data)

				#self.send(thread_player, Message(ServerMessage.GAME_FULL))
				#self.send(thread_player, Message(ServerMessage.TAG_CHANGE, 14, GameTag.HEALTH, 69))

		# Wait for all threads to finish.
		for thread in self.connections:
			thread.join()

	def send(self, players, message):
		"""Send a message to a set of players"""
		if not isinstance(players, list):
			players = [players]
		data = message.pack()
		for connection in self.connections:
			if connection.player in players:
				color_print("Sending to %s: {yellow}%s{}\n" %(connection.player, message))
				connection.send_data(data)

	def broadcast(self, player, message):
		"""Send a message to all players"""
		color_print("Broadcasting message: {yellow}%s{}\n" %(message))
		data = message.pack()
		self.socket.sendall(data)
		pass

	def receive_data(self, player, data):
		"""Decode a packet of bytes received from the given player"""
		message = Message()
		message.unpack(data)
		self.decode_message(player, message)

	def decode_message(self, player, message):
		"""Decode a message received from the given player"""

		# Print out the message
		color_print("Received from %s: {yellow}%s{}\n" %(player, message))

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
	server.bind()
	server.run()

