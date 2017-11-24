
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


server_log = logging.Logger("Server Log")


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
		self.options = []

		if self.player.choice:
			return self.refresh_choices()

		server_log.log("Refreshing options for %s...", self.player)

		self.options.append({"Type": OptionType.DONE})
		for entity in self.game.choosing_player.actionable_entities:
			for option in self.get_options(entity):
				self.options.append(option)

		payload = {
			"Type": "Options",
			"Options": self.options,
		}
		self.queued_data.append(payload)

	def refresh_choices(self):
		server_log.log("Refreshing choices for %s...", self.player)
		choice = self.player.choice
		self.choices = {
			"ChoiceType": choice.type,
			"Entities": [e.entity_id for e in choice.cards],
			"PlayerID": self.player.entity_id,
			"SourceID": choice.source.entity_id,
			#"CountMin": choice.min_count,
			#"CountMax": choice.max_count,
		}
		payload = {
			"Type": "Choices",
			"Choices": self.choices
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
		server_log.log("Queueing a tag change for %r: %s -> %r" %(entity, tag, value))
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
					server_log.log("Removing entity %r", entity)
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
					targets = list(entity.play_targets)
					yield {
						"Type": OptionType.PLAY,
						"MainOption": {
							"ID": entity,
							"Targets": list(targets),
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
								"Targets": [targets],
							}
						}
				elif entity.can_intercept():
					targets = list(entity.intercept_targets)
					if len(targets) > 0:
						yield {
							"Type": OptionType.DECLARE,
							"MainOption": {
								"ID": entity,
								"Targets": [targets],
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

			server_log.log("Received data from %s: %s", self.player, data)

			message = self.decoder.decode(data.decode("utf-8"))
			self.server.receive_data(self.player, message)
			for connection in self.server.connections:
				connection.manager.refresh_full_state()
				connection.manager.refresh_options()
				connection.send_queued_data()

		server_log.log("Client thread for %s has terminated", self.player)

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
			packet = None
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
		server_log.log("Sending to %s: %d bytes", self.player, len(data))
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
		server_log.log("Sending to %s: %d bytes", self.player, len(data))
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

		goliath = self.game.player1.give("SunkenGoliath", Zone.PLAY)
		self.game.player1.give("TomePrinter", Zone.PLAY)
		self.game.player1.give("WarlordHeir")
		self.game.player1.give("RipperPack")
		self.game.player1.give("BonehoarderBrute")
		self.game.player1.give("WarpackChieftan")
		self.game.player1.give("RageheartThug")
		self.game.player1.give("AgileSquirmer")
		self.game.player1.give("NecrolightSoldier")

		self.game.player2.give("OctopiExile", Zone.PLAY)
		self.game.player2.give("InfestedWhale", Zone.PLAY)
		self.game.player2.give("ServantOfElagalth")
		self.game.player2.give("UnstableLurker")
		self.game.player2.give("NoxiousTentacle")
		self.game.player2.give("Overrun")

		for i in range(0, 40):
			self.game.player1.card(random.choice(test_deck)[1], zone=Zone.DECK)
			self.game.player2.card(random.choice(test_deck)[1], zone=Zone.DECK)

		self.game.player1.shuffle_deck()
		self.game.player2.shuffle_deck()
		self.game.begin_turn(self.game.player1)
		self.game.player1.morale += 100
		self.game.player1.supply += 100
		self.game.player2.morale += 100
		self.game.player2.supply += 100
		goliath.damage = 6


	def bind(self, port, host=""):
		"""Bind the server to an address"""
		server_log.log("Binding server to port %d", port)
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
				server_log.log("Error: a client tried to connect but game is full")
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
				server_log.log("%s has connected!", thread_player)
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
		server_log.log("Received message from %s: %s", player, message)

		type = message["Type"]
		data = message.get(type, None)

		if type == "Disconnect":
			server_log.log("%s has disconnected", player)
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
			targets = data["Targets"]
			for i in range(0, len(targets)):
				targets[i] = self.game.find_entity(targets[i])

			card = self.game.find_entity(entity_id)
			if not card:
				print("Card ID '%d' does not exist" %(entity_id))
				return False
			card.play(targets=targets)
			return True

		elif type == "Choose":
			data = message.get("Choose")
			entity_id = data["EntityID"]
			if player.choice == None:
				print("There is no choice for %s" %(player))
				return False
			for card in player.choice.cards:
				if card.entity_id == entity_id:
					player.choice.choose(card)
					return True
			return False

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
			attacker = self.game.find_entity(data["Attacker"])
			if not interceptor:
				print("Card ID '%s' does not exist" %(data["Interceptor"]))
				return CommandResponse.INVALID
				return False
			if not attacker:
				print("Card ID '%s' does not exist" %(data["Attacker"]))
				return CommandResponse.INVALID
				return False
			interceptor.declared_intercept = attacker
			print("%s declared intercept: %r -> %r" %(player, interceptor, attacker))

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

