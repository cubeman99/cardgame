
import socket
from colors import *
from messages import *
from server import Server

HOST = 'localhost'
PORT = 50007


class Client:

	def __init__(self):
		pass

	def connect(self):
		pass
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((HOST, PORT))
		print("Connected to server!")

	def run(self):
		#self.socket.sendall(b"Hello, world")
		#data = self.socket.recv(1024)
		#self.socket.close()
		#print("Received %s" %(str(data.decode())))
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


if __name__=="__main__":
	client = Client()
	client.connect()
	client.run()

