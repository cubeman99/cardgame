
import socket
from threading import Thread
from colors import *
from messages import *
from enums import *
from client.entities import Entity, Game, Player, Card
import traceback

HOST = 'localhost'
PORT = 50007


class ReceiveThread(Thread):

	def __init__(self, client, socket):
		Thread.__init__(self)
		self.client = client
		self.socket = socket

	def start(self):
		self.run()

	def run(self):
		"""Run the receive thread"""
		while True:
			#data = self.socket.recv(2048)
			data = self.recv_msg()
			if not data:
				break
			print("Received %d bytes from server" %(len(data)))
			#try:
			self.client.receive_data(data)
			self.client.print_game_state()
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
			packet = self.socket.recv(n - len(data))
			if not packet:
				return None
			data += packet
			return data


class Client:

	def __init__(self):
		self.game = Game(0)
		self.game.create({})

	def connect(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((HOST, PORT))
		print("Connected to server!")

		# Start the receiving thread.
		thread = ReceiveThread(self, self.socket)
		thread.start()

	def run(self):
		while True:
			action, args = self.prompt_action()
			if action != None:
				message = self.parse_action(action, args)
				if message != None:
					self.send(message)

	def prompt_action(self, prompt="Your action: "):
		color_print(prompt)
		action = input()
		args = action.split()
		if len(args) == 0:
			return None, []
		action = args[0]
		args = args[1:]
		return action, args

	def send(self, message):
		color_print("Sending to server: {yellow}%s{}\n" %(message))
		packet = message.pack()
		self.socket.sendall(packet)
		pass

	def parse_action(self, action, args):
		msg = Message(ClientMessage.INVALID)

		if action == "play":
			msg.type = ClientMessage.PLAY
			msg.args = [int(args[0])]

		elif action == "flip":
			msg.type = ClientMessage.FLIP
			msg.args = [int(args[0])]

		elif action == "attack":
			msg.type = ClientMessage.DECLARE_ATTACK
			msg.args = [int(args[0]), int(args[1])]

		elif action == "intercept":
			msg.type = ClientMessage.DECLARE_INTERCEPT
			msg.args = [int(args[0]), int(args[1])]

		elif action == "done":
			msg.type = ClientMessage.DONE
			msg.args = []

		if msg.type == ClientMessage.INVALID:
			return None
		return msg


		#color_print("{red}%s:{} %s\n" %(action, args))
		#pass


	def receive_data(self, data):
		"""Decode a packet of bytes received from the server"""
		data = MessageData(ServerMessage.INVALID, data)
		data.type = data.read_int()
		#message = Message()
		#message.unpack(data)
		self.receive_message(data.type, data)

	def receive_message(self, type, data):
		"""Decode a message received from the server"""

		# Print out the message
		#color_print("Received from server: {yellow}%s{}\n" %(MESSAGE_NAMES[type]))
		color_print("Received from server: {yellow}%d{}\n" %(type))

		if type == ServerMessage.GAME_FULL:
			print("GAME FULL!!")

		elif type == ServerMessage.CREATE_GAME:
			pass
			entities = data.read_game_state()
			for id, tags in entities:
				if tags[GameTag.CARD_TYPE] == CardType.PLAYER:
					entity = Player(id, "Player")
				else:
					entity = Entity(id)

				entity.tags = tags
				self.game.register_entity(entity)
				#print("Creating entity ID %d" %(id))

		elif type == ServerMessage.TAG_CHANGE:
			id, tags = data.read_tags()
			entity = self.game.find_entity_by_id(id)
			if not entity:
				entity = Entity(id)
				self.game.register_entity(id)
				print("Creating entity id %d" %(id))
			for tag in tags:
				entity.tags[tag] = value
				print("Setting tag %d to %d for entity %d" %(tag, value, id))

	def print_game_state(self):
		max_name_length = 0
		for entity in self.game.entities:
			if GameTag.CARD_TYPE in entity.tags.keys() and\
				entity.tags[GameTag.CARD_TYPE] == CardType.UNIT:
				max_name_length = max(max_name_length, len(entity.tags[GameTag.NAME]))
		format = " %3d. %dm%ds - %d/%d {card_name}" + "%%-%ds" %(max_name_length + 2) + "{} {card_text}%s{}\n"

		self.print_card_list(self.game.players[0].field)

		for entity in self.game.entities:

			if GameTag.CARD_TYPE in entity.tags.keys() and\
				entity.tags[GameTag.CARD_TYPE] == CardType.UNIT:
				#print("Entity %d: %s"%(entity.id, entity.tags))
				power = entity.tags[GameTag.POWER]
				health = entity.tags[GameTag.HEALTH]
				morale = entity.tags[GameTag.MORALE]
				supply = entity.tags[GameTag.SUPPLY]
				name = entity.tags[GameTag.NAME]
				text = entity.tags[GameTag.TEXT]
				color_print(format %(entity.id, morale, supply, power, health, name, text))

	def print_card_list(self, card_list, name=None):
		if name != None:
			print("%s" %(name))

		max_name_length = 1
		count = 0
		for card in card_list:
			max_name_length = max(max_name_length, len(card.data.name))

		for card in card_list:
			count += 1
			id_color = ""
			#if card.is_playable():
			#	id_color = "playable"
			color_print("  {%s}%3d.{} %dm/%ds - " %(
				id_color,
				card.id,
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

		if count == 0:
			print("  (empty)")

if __name__=="__main__":
	client = Client()
	client.connect()
	client.run()
	#game = Game(1)
	#game.create({})
	#card = Card(3, "RageheartThug")
	#game.register_entity(card)
	#x = game.find_entity_by_id(3)



