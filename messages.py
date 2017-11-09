from enum import IntEnum
from enums import *
import struct

class ServerMessage(IntEnum):
	INVALID				= 0
	EXCEPTION			= 1 # A python exception happened in the server
	#ACTION_SUCCESS		= 2 # The action requested by the client was successful
	#ACTION_INVALID		= 3 # The client tried to do an invalid action

	TAG_CHANGE			= 4 # A card's tag has changed
	ACTION_START		= 5
	ACTION_END			= 6
	CREATE_GAME			= 7 # Create the initial game state
	CREATE_ENTITY		= 8 # Create an entity

	GAME_FULL			= 9 # Game is full


class ClientMessage(IntEnum):
	INVALID				= 100
	DONE				= 101 # Equivilent to end turn
	CONCEDE				= 102
	PLAY				= 103 # Play a card
	FLIP				= 104 # Flip a card (or cancel a flip)
	DECLARE_ATTACK		= 105 # Declare an attack (or undeclare an attack)
	DECLARE_INTERCEPT	= 106 # Declare an intercept (or undeclare an intercept)
	CHOOSE_TARGETS		= 107


# Create dictionary of message names.
# NOTE: Client and Server message IDs do not intersect.
MESSAGE_NAMES = {}
members = [(getattr(ServerMessage, attr), attr) for attr in dir(ServerMessage) if not callable(getattr(ServerMessage, attr)) and not attr.startswith("__")]
members += [(getattr(ClientMessage, attr), attr) for attr in dir(ClientMessage) if not callable(getattr(ClientMessage, attr)) and not attr.startswith("__")]
for message, name in members:
	MESSAGE_NAMES[message] = name


# num _entities, entities[id, num_tags, tags[name, value]]

class MessageData:
	def __init__(self, type, data=b""):
		self.type = type
		self.data = data
		self.index = 0
		#self.write_int(int(self.type))

	def read_game_state(self):
		num_entities = self.read_int()
		entities = []
		for i in range(0, num_entities):
			id, tags = self.read_entity()
			entities.append((id, tags))
		return entities

	def read_entity(self):
		id = self.read_int()
		tags = self.read_tags()
		print("ENTITY ID %d" %(id))
		return id, tags

	def read_tags(self):
		num_tags = self.read_int()
		tags = {}
		for i in range(0, num_tags):
			key, value = self.read_tag()
			tags[key] = value
		return tags

	def read_tag(self):
		key = self.read_int()
		if key in STRING_TAGS:
			value = self.read_string()
		else:
			value = self.read_int()
		print("    %s = %r" %(TAG_NAMES[key], value))
		return key, value

	def read_int(self):
		value = struct.unpack("i", self.data[self.index : self.index + 4])
		self.index += 4
		return value[0]

	def read_string(self):
		size = self.read_int()
		byte_string = self.data[self.index : self.index + size]
		self.index += size
		return byte_string.decode(encoding='utf-8')

	def write_int(self, value):
		self.data += struct.pack("i", value)

	def write_string(self, value):
		byte_string = bytearray(value, encoding='utf-8')
		self.data += struct.pack("i", len(byte_string))
		self.data += byte_string

	def write_tag(self, key, value):
		self.write_int(key)
		if key in STRING_TAGS:
			self.write_string(value)
		else:
			self.write_int(value)

	def write_tags(self, tags):
		valid_tags = 0
		for key, value in tags.items():
			if isinstance(value, int) or key in STRING_TAGS:
				valid_tags += 1
		self.write_int(valid_tags)
		for key, value in tags.items():
			if isinstance(value, int) or key in STRING_TAGS:
				self.write_tag(key, value)

	def write_entity(self, id, tags):
		self.write_int(id)
		self.write_tags(tags)

	def write_game_state(self, entities):
		self.write_int(len(entities))
		for id, tags in entities:
			self.write_entity(id, tags)

class Message:

	def __init__(self, type=ClientMessage.INVALID, *args):
		self.type = type
		self.args = args[:]

	def pack(self):
		data = b""
		data += struct.pack("ii", self.type, len(self.args))
		for arg in self.args:
			data += struct.pack("i", arg)
		return data

	def unpack(self, data):
		self.type, num_args = struct.unpack("ii", data[:8])
		self.args = list(struct.unpack("i" * num_args, data[8:]))

	def __str__(self):
		ret = MESSAGE_NAMES[self.type]
		if len(self.args) > 0:
			ret += "("
			for i in range(0, len(self.args)):
				if i > 0:
					ret += ", "
				ret += "%s" %(str(self.args[i]))
			ret += ")"
		return ret



