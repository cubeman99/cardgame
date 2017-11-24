
import logic.actions as actions
import inspect
from colors import *


# Print information about all actions
if __name__ == "__main__":

	action_dict = {}

	# Compile a list of actions.
	for key in dir(actions):
		value = getattr(actions, key)
		if inspect.isclass(value) and\
			issubclass(value, actions.Action) and\
			value != actions.Action and\
			value != actions.GameAction and\
			value != actions.TargetedAction:

			action_dict[key] = value

	for name, value in action_dict.items():
		args = inspect.getargspec(value.invoke).args[2:]
		arg_list = ""
		for i in range(0, len(args)):
			if i > 0:
				arg_list += ", "
			arg_list += args[i]
		color_print("{yellow}%s{}(%s)\n" %(name, arg_list))

		if value.__doc__ != None:
			words = value.__doc__.split()
			doc = ""
			arg = False
			for word in words:
				if word == "\a":
					arg = True
					continue
				if arg:
					doc += "{red}"
				doc += word + " "
				if arg:
					doc += "{}"
				arg = False
			color_print("%s\n" %(doc))

		color_print("\n")

