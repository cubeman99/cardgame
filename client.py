
import socket
import threading
from colors import *
from messages import *
from enums import *
from client.entities import Entity, Game, Player, Card, Option
import card_details
import traceback
import json
import argparse
import os


class ReceiveThread(threading.Thread):
	"""Thread responsible for receiving messages from the server"""

	def __init__(self, client, socket, event):
		threading.Thread.__init__(self)
		self.client = client
		self.socket = socket
		self.event = event

	def run(self):
		"""Run the receive thread"""
		self.socket.settimeout(1.0)
		while not self.event.is_set():
			#data = self.socket.recv(2048)
			data = self.recv_msg()
			if not data:
				continue
			print("Received %d bytes from server" %(len(data)))
			#try:
			self.client.receive_data(data)
			self.client.print_game_state()
			color_print("{green}Your action:{} ")
			#except Exception as e:
			#traceback.print_exc(file=sys.stdout)
			#color_print("Exception: {yellow}%r{}" %(e))

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
				packet = self.socket.recv(n - len(data))
			except:
				if self.event.is_set():
					return None
				else:
					continue
			if not packet:
				return None
			data += packet
		return data



class Client:

	def __init__(self, name):
		self.game = Game(0)
		self.game.create({})
		self.receive_thread = None
		self.exit = False
		self.serializer = json.JSONEncoder()
		self.player_id = None
		self.name = name

	@property
	def player(self):
		for player in self.game.players:
			if player.id == self.player_id:
				return player
		return None

	@property
	def opponent(self):
		for player in self.game.players:
			if player.id != self.player_id:
				return player
		return None

	def connect(self, host, port):
		"""Connect to the server"""
		print("Attempting connection to %s:%d as %s" %(host, port, name))
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.connect((host, port))
		except:
			return False
		print("Connected to server!")

		# Start the receiving thread.
		self.event = threading.Event()
		self.receive_thread = ReceiveThread(self, self.socket, event=self.event)
		self.receive_thread.start()
		return True

	def run(self):
		"""Run the client, endlessly prompting for actions"""
		self.exit = False
		while not self.exit:
			try:
				action, args = self.prompt_action()
				if action != None:
					message = self.parse_action(action, args)
					if message != None:
						self.send(message)
			except KeyboardInterrupt:
				print("")
				self.exit = True

		color_print("{yellow}Disconnecting...{}\n")
		# Send a disconnect packet
		self.send({"Type": "Disconnect"})
		self.event.set()

	def prompt_action(self):
		color_print("{green}Your action:{} ")
		action = input()
		args = action.split()
		if len(args) == 0:
			return None, []
		action = args[0]
		args = args[1:]
		return action, args

	def send(self, data):
		#color_print("Sending to server: {yellow}%s{}\n" %(message))
		#packet = message.pack()
		#self.socket.sendall(packet)

		# Prefix each message with a 4-byte length (network byte order)
		data = self.serializer.encode(data).encode("utf-8")
		data = struct.pack('i', len(data)) + data
		print("Sending %d bytes to server" %(len(data)))
		self.socket.sendall(data)

	def parse_action(self, action, args):
		msg = Message(ClientMessage.INVALID)

		# Play a card
		# Usage: play CARD TODO: targets
		if action == "play":
			#msg.type = ClientMessage.PLAY
			#msg.args = [int(args[0])]
			return {
				"Type": "Play",
				"Play": {
					"EntityID": int(args[0]),
				}
			}

		# Flip (or unflip) a unit
		# Usage: flip UNIT
		elif action == "flip":
			return {
				"Type": "Flip",
				"Flip": {
					"Unit": int(args[0]),
				}
			}

		# Declare an attack
		# Usage: attack ATTACKER DEFENDER
		elif action == "attack":
			return {
				"Type": "Attack",
				"Attack": {
					"Attacker": int(args[0]),
					"Defender": int(args[1]),
				}
			}

		# Declare an intercept
		# Usage: intercept INTERCEPTOR DEFENDER
		elif action == "intercept":
			return {
				"Type": "Intercept",
				"Intercept": {
					"Interceptor": int(args[0]),
					"Defender": int(args[1]),
				}
			}

		# Cancel a declared attack or intercept
		# Usage: cancel UNIT
		elif action == "cancel":
			#attacker = self.game.find_entity_by_id((int(args[0])))
			return {
				"Type": "CancelAttack",
				"CancelAttack": {
					"Attacker": int(args[0]),
				}
			}

		# Usage: done
		elif action == "done":
			return { "Type": "Done" }

		# DEBUG: perform an attack
		elif action == "atk":
			return {
				"Type": "DebugAttack",
				"DebugAttack": {
					"Attacker": int(args[0]),
					"Defender": int(args[1]),
				}
			}

		# DEBUG: Restart the game
		elif action == "restart":
			return { "Type": "DebugRestart" }

		# DEBUG: Rollback game to the beggining of the turn.
		elif action == "rollback":
			return { "Type": "DebugRollback" }

		# View the game state
		# Usage: view
		elif action == "view":
			self.print_game_state()
			return None

		# View current options
		# Usage: options
		elif action == "options":
			i = 1
			print("Available options:")
			for option in self.game.options:
				print(" %2d. %s" %(i, option))
				i += 1
			return None

		# Print out info about an entity
		# Usage: info ENTITY
		elif action == "info":
			entity = self.game.find_entity_by_id(int(args[0]))
			if entity:
				color_print("Entity %d ({card_name}%s{})\n" %(entity.id, entity.card_id))
				print("Tags:")
				for key, value in entity.tags.items():
					tag = GameTag(key)
					value_color = ""
					buff_note = ""
					buff_amount = entity.get_tag_buff_amount(key)
					if buff_amount > 0:
						value_color = "green"
						buff_note = " ({%s}+%d{})" %(value_color, buff_amount)
					elif buff_amount < 0:
						value_color = "red"
						buff_note = " ({%s}%d{})" %(value_color, buff_amount)
					color_print("   %s = {%s}%r{}%s\n" %(tag.name, value_color, value, buff_note))
				print("Buffs:")
				for buff in entity.buffs:
					color_print("   %3d. {card_name}%s{}: " %(buff.id, buff.card_id))
					for key, value in buff.tags.items():
						tag = GameTag(key)
						if tag not in (GameTag.CARD_TYPE, GameTag.OWNER,
							GameTag.CONTROLLER, GameTag.ZONE, GameTag.NAME):
							color_print("%s=%r, " %(tag.name, value))
					color_print("\n")
			return None

		# Show help information
		# Usage: help
		elif action == "help":
			color_print("{yellow}TODO{}: help is unimplemented\n")
			return None

		# Exit the game
		# Usage: exit
		elif action == "exit":
			self.exit = True
			return None

		# Concede the game.
		# Usage: concede
		elif action == "concede":
			self.exit = True
			return { "Type": "Concede" }

		# Unknown action.
		else:
			print("Invalid action '%s'" %(action))
			return None

		return None


	def receive_data(self, data):
		"""Decode a packet of bytes received from the server"""

		encoder = json.JSONDecoder()
		state = encoder.decode(data.decode("utf-8"))

		for thing in state:
			type = thing["Type"]
			data = thing[type]

			if type == "AcceptConnection":
				self.player_id = data["PlayerID"]
				print("I joined as player ID %d" %(self.player_id))
				self.send({
					"Type": "JoinGame",
					"JoinGame": {
						"Name": self.name,
					}
				})

			if type == "FullEntity":
				card_id = data["CardID"]
				entity_id = data["EntityID"]
				tags = {}
				for key, value in data["Tags"].items():
					tag = GameTag(int(key))
					tags[int(key)] = value
				entity = None
				if tags[GameTag.CARD_TYPE] == CardType.PLAYER:
					entity = Player(entity_id)
					data = card_details.find(card_id)
					entity.tags.update(data.tags)
					entity.tags.update(tags)
					self.game.register_entity(entity)
				else:
					entity = self.game.create_card(entity_id, card_id, tags)

			elif type == "TagChange":
				entity_id = data["EntityID"]
				tag = GameTag(int(data["Tag"]))
				if tag.type == Type.STRING:
					value = data["Value"]
				else:
					value = int(data["Value"])
				entity = self.game.find_entity_by_id(entity_id)
				if entity:
					entity.tags[tag] = value

			elif type == "Options":
				options = thing["Options"]
				self.game.options = []
				for option in options:
					option_type = OptionType(option["Type"])
					option_args = option.get("MainOption", {})
					self.game.options.append(Option(
						type=option_type,
						args=option_args))

	def print_game_state(self):
		max_name_length = 0
		for entity in self.game.entities:
			#print("%d. %s - %r" %(entity.id, entity.tags.get(GameTag.NAME, "?"), entity.controller))
			if GameTag.CARD_TYPE in entity.tags.keys() and\
				entity.tags[GameTag.CARD_TYPE] == CardType.UNIT:
				max_name_length = max(max_name_length, len(entity.tags[GameTag.NAME]))
		format = " %3d. %dm%ds - %d/%d {card_name}" + "%%-%ds" %(max_name_length + 2) + "{} {card_text}%s{}\n"

		player = self.player
		opponent = self.opponent

		print("")
		self.print_player_info(opponent, opponent.name)
		print("")
		self.print_card_list(list(opponent.hand), "Opponent's hand:")
		print("")
		self.print_card_list(list(opponent.field), "Opponent's field:")
		self.print_card_list(list(player.field), "Your field:")
		print("")
		self.print_card_list(list(player.hand), "Your hand:")
		print("")
		self.print_player_info(player, player.name)
		print("")

	def print_player_info(self, player, name):
		deck_size = len([card for card in player.deck])
		color_print("{yellow}%s(%d):{} Morale: %d, Supply: %d, Territory: %d, Deck: %d cards\n" %(
			name,
			player.id,
			player.morale,
			player.supply,
			player.territory,
			deck_size))

	def print_card_list(self, card_list, name=None):
		if name != None:
			color_print("{yellow}%s{}\n" %(name))

		max_name_length = 1
		count = 0
		for card in card_list:
			max_name_length = max(max_name_length, len(card.tags.get(GameTag.NAME, "?")))

		for card in card_list:
			count += 1
			id_color = ""
			options = [opt for opt in card.options]
			if len(options) > 0:
				id_color = "playable"
			color_print("  {%s}%3d.{} %dm/%ds - " %(
				id_color,
				card.id,
				card.morale,
				card.supply))

			# Print power/health
			if card.type == CardType.UNIT:
				health_buff = card.get_tag_buff_amount(GameTag.HEALTH)
				power_buff = card.get_tag_buff_amount(GameTag.POWER)

				# Colorize power: buffed = green
				power_color = "default"
				if power_buff > 0:
					power_color = "buffed_stat"

				# Colorize health: damaged = red, else buffed = green
				health_color = "default"
				if card.health < card.max_health:
					health_color = "damaged_health"
				elif health_buff > 0:
					health_color = "buffed_stat"

				color_print("{%s}%d{}/{%s}%d{}" %(
					power_color, card.power,
					health_color, card.health
				))
			else:
				sys.stdout.write("   ")

			# Print name. TODO: colorize spell/unit
			name_color = "card_name_unit" if card.type == CardType.UNIT else "card_name_spell"
			format = " {%s}%%-" %(name_color) + str(max_name_length) + "s{}"
			color_print(format %(card.name))

			# Print declared attack/intercept
			if card.type == CardType.UNIT:
				declared_attack = card.tags.get(GameTag.DECLARED_ATTACK, 0)
				declared_intercept = card.tags.get(GameTag.DECLARED_INTERCEPT, 0)
				if declared_attack:
					color_print(" {red}>> %d{}" %(declared_attack))
				elif declared_intercept:
					color_print(" {cyan}>> %d{}" %(declared_intercept))

			# Print text
			color_print("  {card_text}%s{}\n" %(card.tags.get(GameTag.TEXT, "")))

		if count == 0:
			print("      (empty)")




if __name__=="__main__":
	DEFAULT_HOST = "localhost"
	DEFAULT_PORT = 50007
	DEFAULT_NAME = os.getlogin()

	# Parse the command line arguments
	parser = argparse.ArgumentParser(description='Run the cardgame client.')
	parser.add_argument('host', metavar='HOST', type=str,
		default=DEFAULT_HOST, nargs="?",
		help="Optional host IP address and optional port to connect to (in the format \"host:port\"). The default host is '%s' and the default port is %d." %(DEFAULT_HOST, DEFAULT_PORT))
	args = parser.parse_args()

	# Parse the host IP/PORT in the format: "host:port"
	# The port is optional
	# TODO: Handle parse errors here
	split_host = args.host.split(":")
	host = split_host[0]
	port = DEFAULT_PORT
	if len(split_host) >= 2:
		port = int(split_host[1])

	name = DEFAULT_NAME

	# Initialize the Client
	client = Client(name=name)

	# Connect to the server and run the client.
	if client.connect(host=host, port=port):
		client.run()
	else:
		print("Failed to connect to server!")
		exit(2)




