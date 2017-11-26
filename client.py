

from cardgame.text_based_client import *
from cardgame import card_details
from cardgame.game import Game
import os
import argparse


if __name__=="__main__":
	card_details.initialize()

	DEFAULT_HOST = "localhost"
	DEFAULT_PORT = 32764
	DEFAULT_NAME = os.getlogin()

	# Parse the command line arguments
	parser = argparse.ArgumentParser(description="Run the cardgame client.")
	parser.add_argument("host", metavar="HOST", type=str,
		default=DEFAULT_HOST, nargs="?",
		help="optional host IP address and optional port to connect to (in the format \"host:port\"). The default host is '%s' and the default port is %d." %(DEFAULT_HOST, DEFAULT_PORT))
	parser.add_argument("-p", "--prompt", action="store_true",
		help="prompt the user for the server's IP address")
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

	# Prompt fot the server's IP address.
	if args.prompt:
		print("Enter the IP address of the server, or just hit ENTER for localhost.")
		sys.stdout.write("IP Address: ")
		sys.stdout.flush()
		host = input()
		if host == "":
			host = "localhost"

	# Initialize the Client
	client = Client(name=name)

	# Connect to the server and run the client.
	if client.connect(host=host, port=port):
		client.run()
	else:
		print("Failed to connect to server!")
		exit(2)
