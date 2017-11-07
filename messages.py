from enum import IntEnum
import struct

class ServerMessage(IntEnum):
	INVALID				= 0
	EXCEPTION			= 1 # A python exception happened in the server
	ACTION_SUCCESS		= 2 # The action requested by the client was successful
	ACTION_INVALID		= 3 # The client tried to do an invalid action

class ClientMessage(IntEnum):
	INVALID				= 0
	DONE				= 1 # Equivilent to end turn
	CONCEDE				= 2
	PLAY				= 3 # Play a card
	FLIP				= 4 # Flip a card (or cancel a flip)
	DECLARE_ATTACK		= 5 # Declare an attack (or undeclare an attack)
	DECLARE_INTERCEPT	= 6 # Declare an intercept (or undeclare an intercept)
	CHOOSE_TARGETS		= 7

SERVER_MESSAGE_NAMES = {
	ServerMessage.INVALID:			"invalid",
	ServerMessage.EXCEPTION:		"exception",
	ServerMessage.ACTION_SUCCESS:	"action_success",
	ServerMessage.ACTION_INVALID:	"action_invalid",
}

CLIENT_MESSAGE_NAMES = {
	ClientMessage.INVALID:				"invalid",
	ClientMessage.DONE:					"done",
	ClientMessage.CONCEDE:				"concede",
	ClientMessage.PLAY:					"play",
	ClientMessage.FLIP:					"flip",
	ClientMessage.DECLARE_ATTACK:		"attack",
	ClientMessage.DECLARE_INTERCEPT:	"intercept",
	ClientMessage.CHOOSE_TARGETS:		"flip",
}


class Message:

	def __init__(self, type=ClientMessage.INVALID):
		self.type = type
		self.args = []

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
		ret = "%s(" %(CLIENT_MESSAGE_NAMES[self.type])
		for i in range(0, len(self.args)):
			if i > 0:
				ret += ", "
			ret += "%s" %(str(self.args[i]))
		ret += ")"
		return ret



