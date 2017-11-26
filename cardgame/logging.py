
class Logger:

	def __init__(self, name):
		self.name = name
		self.enabled = True

	def info(self, message, *args):
		print(message % args)

	def log(self, message, *args):
		if self.enabled:
			print("%s: %s" %(self.name, message % args))

	def disable(self):
		self.enabled = False

	def enable(self):
		self.enabled = True

log = Logger("Default Log")


action_log = Logger("Action Log")
#entity = Logger("Entity Log")
#event = Logger("Event Log")
#protocol = Logger("Protocol Log")

