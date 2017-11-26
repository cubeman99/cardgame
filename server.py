
from cardgame.server import Server


if __name__=="__main__":
	DEFAULT_PORT = 32764
	server = Server()
	server.prepare_game()
	server.bind(port=DEFAULT_PORT)
	server.run()

