
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
import json
#from SocketServer import ThreadingMixIn


# This will by default convert things to integers (entities will become entity IDs)
class GameSerializer(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, CardList):
			return len(o)
		return int(o)


class ServerManager:
	def __init__(self, game, player):
		self.game = game
		self.player = player
		self.game_state = {}
		self.queued_data = []

	def add_to_state(self, entity):
		state = {}
		self.game_state[entity.entity_id] = state
		for tag, value in entity.tags.items():
			# Value is default to card data.
			if not value:
				continue
			#if isinstance(value, str):
			#	continue
			state[tag] = value

	def refresh_options(self):
		print("Refreshing options...")
		self.options = []

		#if self.game.current_player.choice:
		#	return self.refresh_choices()

		if self.game.choosing_player == self.player:
			self.options.append({"Type": OptionType.DONE})
			for entity in self.game.choosing_player.actionable_entities:
				for option in self.get_options(entity):
					self.options.append(option)

		payload = {
			"Type": "Options",
			"Options": self.options,
		}
		self.queued_data.append(payload)

	def new_entity(self, entity):
		self.add_to_state(entity)
		#if isinstance(entity, Player):
		#	payload = self.player_entity(entity)
		#else:
		payload = self.full_entity(entity)
		self.queued_data.append(payload)

	def tag_change(self, entity, tag, value):
		if tag < 0:
			return
		print("Queueing a tag change for %r: %s -> %r" %(entity, tag, value))
		payload = {
			"Type": "TagChange",
			"TagChange": {
				"EntityID": entity.entity_id,
				"Tag": tag,
				"Value": value,
			}
		}
		self.queued_data.append(payload)

	def full_entity(self, entity):
		return {
			"Type": "FullEntity",
			"FullEntity": {
				"CardID": entity.id,
				"EntityID": entity.entity_id,
				"Tags": self.game_state[entity.entity_id],
			}
		}

	def refresh_tag(self, entity, tag):
		state = self.game_state[entity.entity_id]
		value = entity.tags.get(tag, 0)
		#if tag == GameTag.DAMAGE:
		#	print("TAG power: %r = %r" %(tag, value))
		#if isinstance(value, str):
		#	return
		if value == None:
			value = 0
		if not value:
			if state.get(tag, 0):
				self.tag_change(entity, tag, 0)
				del state[tag]
		#elif int(value) != state.get(tag, 0):
		#	self.tag_change(entity, tag, int(value))
		#	state[tag] = int(value)
		elif value != state.get(tag, 0):
			self.tag_change(entity, tag, value)
			state[tag] = value

	def refresh_full_state(self):
		#if self.game.step < Step.BEGIN_MULLIGAN:
		#	return
		for entity in self.game:
			if entity.entity_id in self.game_state:
				self.refresh_state(entity.entity_id)
			else:
				self.new_entity(entity)

		# Check for removed entities (these usually being buffs)
		items = [item for item in self.game_state.items()]
		for entity_id, state in items:
			if self.game.find_entity(entity_id) == None:
				entity = self.game.find_removed_entity(entity_id)
				if entity:
					# First, refresh the state for the client to know
					print("Removing entity %r" %(entity))
					self.refresh_state(entity_id)
					# Then, remove it from our state.
					self.game_state.pop(entity_id)


	def refresh_state(self, entity_id):
		assert entity_id in self.game_state
		entity = self.game.find_entity(entity_id)
		if not entity:
			entity = self.game.find_removed_entity(entity_id)
		state = self.game_state[entity.entity_id]

		for tag in entity.tags:
			self.refresh_tag(entity, tag)

	def get_options(self, entity):
		if entity.zone == Zone.HAND:
			if entity.type in [CardType.SPELL, CardType.UNIT]:
				if entity.is_playable():
					yield {
						"Type": OptionType.PLAY,
						"MainOption": {
							"ID": entity,
							"Targets": list(entity.targets),
						},
					}

		elif entity.zone == Zone.PLAY:
			if entity.type in [CardType.UNIT]:
				if entity.can_attack():
					targets = list(entity.attack_targets)
					if len(targets) > 0:
						yield {
							"Type": OptionType.DECLARE,
							"MainOption": {
								"ID": entity,
								"Targets": targets,
							}
						}
				elif entity.can_intercept():
					targets = list(entity.intercept_targets)
					if len(targets) > 0:
						yield {
							"Type": OptionType.DECLARE,
							"MainOption": {
								"ID": entity,
								"Targets": targets,
							}
						}










class ClientThread(Thread):

	def __init__(self, server, player, connection, ip, port):
		Thread.__init__(self)
		self.server = server
		self.player = player
		self.connection = connection
		self.ip = ip
		self.port = port
		self.manager = ServerManager(self.server.game, self.player)
		self.serializer = GameSerializer()
		self.decoder = json.JSONDecoder()

	def run(self):
		"""Run the client thread"""
		self.disconnected = False
		while not self.disconnected:
			data = self.recv_msg()
			if not data:
				continue

			message = self.decoder.decode(data.decode("utf-8"))
			self.server.receive_data(self.player, message)
			for connection in self.server.connections:
				connection.manager.refresh_full_state()
				connection.manager.refresh_options()
				connection.send_queued_data()

		print("Client thread for %s has terminated" %(self.player))

	def recv_msg(self):
		"""Read message length and unpack it into an integer"""
		raw_msglen = self.recvall(4)
		if not raw_msglen:
			return None
		msglen = struct.unpack('i', raw_msglen)[0]
		# Read the message data
		return self.recvall(msglen)

	def recvall(self, n):
		"""Helper function to recv n bytes or return None if EOF is hit"""
		data = b""
		while len(data) < n:
			try:
				packet = self.connection.recv(n - len(data))
			except:
				if self.disconnected:
					return None
			if not packet:
				return None
			data += packet
			return data

	def send_data(self, data):
		"""Send data to the client"""
		print("Sending to %s: %d bytes" %(self.player, len(data)))
		# Prefix each message with a 4-byte length (network byte order)
		data = struct.pack('i', len(data)) + data
		self.connection.send(data)

	def send_queued_data(self):
		"""Send all queued data to the client"""
		if len(self.manager.queued_data) > 0:
			self.send(self.manager.queued_data)
			self.manager.queued_data = []

	def send(self, data):
		"""Send data (dictionary) to the client"""
		data = self.serializer.encode(data).encode("utf-8")
		data = struct.pack('i', len(data)) + data
		print("Sending to %s: %d bytes" %(self.player, len(data)))
		self.connection.send(data)


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
	#(1, "RaidpackRally"),
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
	#(1, "ElegalthsChosen"),
	#(1, "AbyssalSummoning"),
	#(1, "PotentAfterlife"),
	#(1, "ExtremePressure"),
]


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

		#self.game.player2.give("TestCard")
		self.game.player2.give("OctopiExile")
		self.game.player2.give("InfestedWhale")
		#self.game.player2.give("EchoingFiend")
		self.game.player2.give("ServantOfElagalth")
		self.game.player2.give("UnstableLurker")
		self.game.player2.give("NoxiousTentacle")
		#self.game.player2.give("ElegalthsChosen")
		self.game.player2.give("Overrun")

		self.game.player1.give("WarlordHeir")
		self.game.player1.give("RipperPack")
		self.game.player1.give("BonehoarderBrute")
		self.game.player1.give("WarpackChieftan")
		#self.game.player1.give("PotentAfterlife")
		#self.game.player1.give("ExtremePressure")
		self.game.player1.give("RageheartThug")
		self.game.player1.give("AgileSquirmer")

		"""self.game.player1.give("RageheartThug")
		self.game.player1.give("OctopiExile")
		self.game.player1.give("TestCard")
		self.game.player1.give("InfestedWhale")
		self.game.player1.give("EchoingFiend")
		self.game.player1.give("ServantOfElagalth")
		self.game.player1.give("StarvingCephalopod")
		self.game.player1.give("AgileSquirmer")
		self.game.player1.give("NecrolightPriestess")
		self.game.player1.give("NoxiousTentacle")
		self.game.player1.give("ElegalthsChosen")
		self.game.player1.give("AbyssalSummoning")"""


		#for i in range(0, 40):
		#	self.game.player1.card("OctopiExile", zone=Zone.DECK)
		#	self.game.player2.card("OctopiExile", zone=Zone.DECK)

		for i in range(0, 40):
			self.game.player1.card(random.choice(test_deck)[1], zone=Zone.DECK)
			self.game.player2.card(random.choice(test_deck)[1], zone=Zone.DECK)

		#for count, card_id in test_deck:
		#	for i in range(0, count):
		#		self.game.player1.card(card_id, zone=Zone.DECK)
		#		self.game.player2.card(card_id, zone=Zone.DECK)

		self.game.player1.shuffle_deck()
		self.game.player2.shuffle_deck()
		self.game.begin_turn(self.game.player1)
		#self.game.player1.hand[0].play()

		deck_size = len([card for card in self.game.player1.deck])
		print("Deck size = %d" %(deck_size))


	def bind(self, port, host=""):
		"""Bind the server to an address"""
		print("Binding server to port %d" %(port))
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((host, port))

	def run(self):
		"""Run the server"""

		# Accept client connections.
		while True:
			self.socket.listen(4)
			conn, (ip, port) = self.socket.accept()

			# Assign the connection to a player and create a thread for it
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
				thread.manager.queued_data += [{
					"Type": "RefuseConnection",
					"RefuseConnection": {
						"Reason": "GameFull",
					}
				}]
				thread.send_queued_data()
				conn.close()
			else:
				print("%s has connected!" %(thread_player))
				thread = ClientThread(self, thread_player, conn, ip, port)
				thread_player.connection = thread
				thread.start()
				self.connections.append(thread)

				thread.manager.queued_data += [{
					"Type": "AcceptConnection",
					"AcceptConnection": {
						"PlayerID": thread.player.entity_id,
					}
				}]
				thread.manager.refresh_full_state()
				thread.manager.refresh_options()
				thread.send_queued_data()

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

	def receive_data(self, player, message):
		"""Decode a packet of bytes received from the given player"""
		print("Received message from %s: %s" %(player, message))

		type = message["Type"]
		data = message.get(type, None)

		if type == "Disconnect":
			print("%s has disconnected" %(player))
			player.connection.disconnected = True
			self.connections.remove(player.connection)
			player.connection = None

		if type == "Concede":
			print("%s concedes!" %(player))

		if type == "Done":
			self.game.end_step()

		elif type == "JoinGame":
			data = message.get("JoinGame")
			name = data["Name"]
			player.name = name

		elif type == "Play":
			data = message.get("Play")
			entity_id = data["EntityID"]

			card = self.game.find_entity(entity_id)
			if not card:
				print("Card ID '%d' does not exist" %(entity_id))
				return False
			print("Playing %s" %(card.name))
			card.play()
			return True

		elif type == "Attack":
			data = message.get("Attack")
			attacker = self.game.find_entity(data["Attacker"])
			defender = self.game.find_entity(data["Defender"])
			if not attacker:
				print("Card ID '%s' does not exist" %(data["Attacker"]))
				return CommandResponse.INVALID
				return False
			if not defender:
				print("Card ID '%s' does not exist" %(data["Defender"]))
				return CommandResponse.INVALID
				return False
			attacker.declared_attack = defender
			print("%s declared attack: %r -> %r" %(player, attacker, defender))

		elif type == "Intercept":
			data = message.get("Intercept")
			interceptor = self.game.find_entity(data["Interceptor"])
			defender = self.game.find_entity(data["Defender"])
			if not interceptor:
				print("Card ID '%s' does not exist" %(data["Interceptor"]))
				return CommandResponse.INVALID
				return False
			if not defender:
				print("Card ID '%s' does not exist" %(data["Defender"]))
				return CommandResponse.INVALID
				return False
			interceptor.declared_intercept = defender
			print("%s declared intercept: %r -> %r" %(player, interceptor, defender))

		elif type == "DebugAttack":
			data = message.get("DebugAttack")
			attacker = self.game.find_entity(data["Attacker"])
			defender = self.game.find_entity(data["Defender"])
			if not attacker:
				print("Card ID '%s' does not exist" %(data["Attacker"]))
				return CommandResponse.INVALID
				return False
			if not defender:
				print("Card ID '%s' does not exist" %(data["Defender"]))
				return CommandResponse.INVALID
				return False
			self.game.action_block(player,
				actions.Attack(attacker, defender), type=BlockType.ATTACK)

		elif type == "DebugDraw":
			data = message.get("DebugDraw")
			count = data["Count"]
			player.draw(count)

		elif type == "DebugRestart":
			print("DEBUG: Restarting the game.")

		elif type == "DebugRollback":
			print("DEBUG: Rolling game state back to the beginning of the current player's turn.")

		elif type == "CancelAttack":
			data = message.get("CancelAttack")
			attacker = self.game.find_entity(data["Attacker"])
			if not attacker:
				print("Card ID '%s' does not exist" %(message.args[0]))
				return CommandResponse.INVALID
				return False

			attacker.declared_attack = None
			print("%s canceled attack for %r" %(player, attacker))
			return True


if __name__=="__main__":
	DEFAULT_PORT = 32764
	server = Server()
	server.prepare_game()
	server.bind(port=DEFAULT_PORT)
	server.run()

