import random
import sys

TERMINAL_WIDTH = 110

def print_in_columns(items, spacing=2, left_padding=2):

	column_widths = [0]
	failed = True

	column_size = 1
	while column_size < len(items) and failed:
		index = 0
		total_width = left_padding
		col = 0
		failed = False

		while index < len(items):
			for i in range(index, index + column_size):
				if i < len(items):
					column_widths[col] = max(column_widths[col], len(items[i]))
			if index < len(items):
				column_widths.append(0)
				total_width += column_widths[col]
				index += column_size
				col += 1
				if total_width > TERMINAL_WIDTH:
					failed = True
					break
				total_width += spacing

		if failed:
			if column_size == len(items):
				break
			column_widths = [0]
			column_size += 1

	for row in range(0, column_size):
		if left_padding > 0:
			sys.stdout.write(" " * left_padding)
		for col in range(0, len(column_widths)):
			index = (col * column_size) + row
			if index < len(items):
				format = "%%-%ds" %(column_widths[col] + spacing)
				sys.stdout.write(format %(items[index]))
		print("")


class CardList(list):
	def __contains__(self, x):
		for item in self:
			if x is item:
				return True
		return False

	def __getitem__(self, key):
		ret = super().__getitem__(key)
		if isinstance(key, slice):
			return self.__class__(ret)
		return ret

	def empty(self):
		return len(self) == 0

	def __int__(self):
		# Used in Kettle to easily serialize CardList to json
		return len(self)

	def contains(self, x):
		"True if list contains any instance of x"
		for item in self:
			if x == item:
				return True
		return False

	def index(self, x):
		for i, item in enumerate(self):
			if x is item:
				return i
		raise ValueError

	def remove(self, x):
		for i, item in enumerate(self):
			if x is item:
				del self[i]
				return
		raise ValueError

	def exclude(self, *args, **kwargs):
		if args:
			return self.__class__(e for e in self for arg in args if e is not arg)
		else:
			return self.__class__(e for k, v in kwargs.items() for e in self if getattr(e, k) != v)

	def filter(self, **kwargs):
		return self.__class__(e for k, v in kwargs.items() for e in self if getattr(e, k, 0) == v)



if __name__=="__main__":
	import os
	print(os.getlogin())
	from logic.actions import *
	a = Summon.CARD
	print(isinstance(a, CardArg))
	a = Summon(SELF, "")
	a = a.CARD
	print(isinstance(a, CardArg))
		#.evaluate()

