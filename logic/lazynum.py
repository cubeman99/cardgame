import copy
import operator
from abc import ABCMeta, abstractmethod
from entity import *
from logic.conditions import Condition
from typing import Any, Union, List, Callable, Iterable, Optional, Set


BinaryOp = Callable[[Any, Any], bool]


class LazyValue(metaclass=ABCMeta):
	@abstractmethod
	def evaluate(self, source):
		pass


# Something that evaluates at runtime.
class LazyNum(LazyValue):
	def __init__(self):
		pass

	def evaluate(self, source) -> int:
		raise NotImplementedError

	def _cmp(op):
		def func(self, other):
			if isinstance(other, (int, LazyNum)):
				# When comparing a LazyNum with an int, turn it into an
				# Evaluator that compares the int to the result of the LazyNum
				return LazyNumEvaluator(self, other, getattr(operator, op))
			return getattr(super(), "__%s__" % (op))(other)
		return func

	__eq__ = _cmp("eq")
	__ge__ = _cmp("ge")
	__gt__ = _cmp("gt")
	__le__ = _cmp("le")
	__lt__ = _cmp("lt")

	def __neg__(self):
		# TODO: should do negation properly
		return LazyNumOperation(operator.mul, -1, self)
	def __add__(self, other):
		return LazyNumOperation(operator.add, self, other)
	def __sub__(self, other):
		return LazyNumOperation(operator.sub, self, other)
	def __mul__(self, other):
		return LazyNumOperation(operator.mul, self, other)

	def get_entities(self, source):
		from logic.selector import Selector
		if isinstance(self.selector, Selector):
			entities = self.selector.eval(source.game, source)
		elif isinstance(self.selector, LazyValue):
			entities = [self.selector.evaluate(source)]
		else:
			# TODO assert that self.selector is a TargetedAction
			entities = sum(self.selector.trigger(source), [])
		return entities


class LazyNumOperation(LazyNum):
	def __init__(self, op: BinaryOp, left, right):
		super().__init__()
		self.op = op
		self.left = left
		self.right = right

	def evaluate(self, source):
		left_value = self.left.evaluate(source)\
			if isinstance(self.left, LazyValue) else self.left
		right_value = self.right.evaluate(source)\
			if isinstance(self.right, LazyValue) else self.right
		return self.op(left_value, right_value)

	def __repr__(self):
		if self.op.__name__ == "add":
			infix = "+"
		elif self.op.__name__ == "sub":
			infix = "-"
		elif self.op.__name__ == "mul":
			infix = "*"
		else:
			infix = "UNKNOWN_OP"
		return "(%r %s %r)" %(self.left, infix, self.right)

class LazyNumEvaluator(Condition):
	def __init__(self, num, other, cmp):
		super().__init__()
		self.num = num
		self.other = other
		self.cmp = cmp

	def __repr__(self):
		return "%s(%r, %r)" % (self.cmp.__name__, self.num, self.other)

	def check(self, source):
		num = self.num.evaluate(source)
		other = self.other
		if isinstance(other, LazyNum):
			other = other.evaluate(source)
		return self.cmp(num, other)

class Count(LazyNum):
	"""
	Lazily count the matches in a selector
	"""
	def __init__(self, selector):
		super().__init__()
		self.selector = selector

	def __repr__(self):
		return "%s(%r)" % (self.__class__.__name__, self.selector)

	def evaluate(self, source):
		return len(self.get_entities(source))


class OpAttr(LazyNum):
	"""
	Lazily evaluate Op over all tags in a selector.
	This is analogous to lazynum.Attr, which is equivalent to OpAttr(..., ..., sum)
	"""
	def __init__(self, selector, tag, op):
		super().__init__()
		self.selector = selector
		self.tag = tag
		self.op = op

	def __repr__(self):
		return "%s(%r, %r)" % (self.__class__.__name__, self.selector, self.tag)

	def evaluate(self, source):
		entities = list(e for e in self.get_entities(source) if e)
		if entities:
			if isinstance(self.tag, str):
				ret = self.op(getattr(e, self.tag) for e in entities)
			else:
				# XXX: int() because of CardList counter tags
				ret = self.op(int(e.tags[self.tag]) for e in entities)
			return ret
		else:
			return None



class Attr(OpAttr):
	"""
	Lazily evaluate the sum of all tags in a selector
	"""
	def __init__(self, selector, tag):
		super().__init__(selector, tag, sum)

	def evaluate(self, source):
		return super().evaluate(source) or 0
