import logging

class Logger:

	def __init__(self, name):
		self.name = name

	def info(self, message, *args):
		print(message % args)

	def log(self, message, *args):
		print("%s: %s" %(self.name, message % args))

log = Logger("Default Log")


action_log = Logger("Action Log")
entity = Logger("Entity Log")
event = Logger("Event Log")
protocol = Logger("Protocol Log")

#logging.actions.log()