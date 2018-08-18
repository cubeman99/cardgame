import copy
import operator
from abc import ABCMeta, abstractmethod
from ..entity import *
from typing import Any, Union, List, Callable, Iterable, Optional, Set



def evaluate(value, source):
	"""
	If the value is a lazy value, then evaluate it with source,
	otherwise just return the value
	"""
	if isinstance(value, LazyNum):
		return value.eval(source)
	else:
		return value


BinaryOp = Callable[[Any, Any], bool]
UnaryOp = Callable[[Any], bool]

# Helper functions for boolean operators
def _and(left, right):
	return left and right
def _or(left, right):
	return left or right
def _not(value):
	return not value


class LazyNum:
	"""
	Lazily evaluate something at runtime.
	"""
	def __init__(self, *args):
		self._args = args

	def evaluate(self, source) -> int:
		raise NotImplementedError

	def eval(self, source):
		from .selector import Selector
		# First, evaluate the arguments
		args = []
		for value in self._args:
			if isinstance(value, Selector):
				args.append(value.select(source.game, source))
			elif isinstance(value, LazyNum):
				args.append(value.eval(source))
			else:
				args.append(value)
		# Now call the abstract evaluate this LazyNum, passing in the
		# evaluated arguments
		return self.evaluate(source, *args)

	def __repr__(self):
		text = "%s(" %(self.__class__.__name__)
		for i in range(0, len(self._args)):
			if i > 0:
				text += ", "
			text += "%r" %(self._args[i])
		text += ")"
		return text

	# Unary arithmetic operators
	def __neg__(self):
		# TODO: should do unary operator properly
		return LazyUnaryOperation(operator.neg, self)

	# Unary comparison operators
	def __invert__(self):
		# TODO: should do unary operator properly
		return LazyUnaryOperation(_not, self)

	# Binary arithmetic operators
	def __add__(self, other):
		return LazyBinaryOperation(operator.add, self, other)
	def __sub__(self, other):
		return LazyBinaryOperation(operator.sub, self, other)
	def __mul__(self, other):
		return LazyBinaryOperation(operator.mul, self, other)
	def __radd__(self, other):
		return LazyBinaryOperation(operator.add, other, self)
	def __rsub__(self, other):
		return LazyBinaryOperation(operator.sub, other, self)
	def __rmul__(self, other):
		return LazyBinaryOperation(operator.mul, other, self)

	# Binary comparison operators
	def __eq__(self, other):
		return LazyBinaryOperation(operator.eq, self, other)
	def __ne__(self, other):
		return LazyBinaryOperation(operator.ne, self, other)
	def __ge__(self, other):
		return LazyBinaryOperation(operator.ge, self, other)
	def __gt__(self, other):
		return LazyBinaryOperation(operator.gt, self, other)
	def __le__(self, other):
		return LazyBinaryOperation(operator.le, self, other)
	def __lt__(self, other):
		return LazyBinaryOperation(operator.lt, self, other)

	# Binary boolean operators
	def __and__(self, other):
		return LazyBinaryOperation(_and, self, other)
	def __or__(self, other):
		return LazyBinaryOperation(_or, self, other)
	def __rand__(self, other):
		return LazyBinaryOperation(_and, other, self)
	def __ror__(self, other):
		return LazyBinaryOperation(_or, other, self)

	def get_entities(self, source):
		from .selector import Selector
		if isinstance(self.selector, Selector):
			entities = self.selector.select(source.game, source)
		elif isinstance(self.selector, LazyNum):
			entities = [self.selector.evaluate(source)]
		else:
			# TODO assert that self.selector is a TargetedAction
			entities = sum(self.selector.trigger(source), [])
		return entities


operator_symbols = {
	"add": "+",
	"sub": "-",
	"mul": "-",
	"eq": "==",
	"ne": "!=",
	"ge": ">=",
	"le": "<=",
	"gt": ">",
	"lt": "<",
	"_and": "&",
	"_or": "|",
	"_not": "!",
	"neg": "-",
}

operator_inversions = {
	operator.ne: operator.eq,
	operator.eq: operator.ne,
	operator.le: operator.gt,
	operator.lt: operator.ge,
	operator.gt: operator.le,
	operator.ge: operator.lt,
}

class LazyUnaryOperation(LazyNum):
	"""
	Lazily perform a unary operation.
	Example: -x
	"""
	def __init__(self, op: UnaryOp, value):
		super().__init__(value)
		self.op = op
		self.value = value

	def evaluate(self, source, value):
		return self.op(value)

	def __repr__(self):
		symbol = operator_symbols.get(self.op.__name__,
			"UNKNOWN_OP(%s)" %(self.op.__name__))
		return "%s%r" %(symbol, self.value)

class LazyBinaryOperation(LazyNum):
	"""
	Lazily perform a binary operation.
	Example: a + b
	"""
	def __init__(self, op: BinaryOp, left, right):
		super().__init__(left, right)
		self.op = op
		self.left = left
		self.right = right

	def evaluate(self, source, left, right):
		return self.op(left, right)

	def __repr__(self):
		infix = operator_symbols.get(self.op.__name__,
			"UNKNOWN_OP(%s)" %(self.op.__name__))
		return "(%r %s %r)" %(self.left, infix, self.right)

	def __invert__(self):
		"""
		Try to fix up redundant inversions:
		For example:
		  == will become !=
		  <= will become >
		  > will become <=
		  etc.
		"""
		inverted_op = operator_inversions.get(self.op, None)
		if inverted_op != None:
			self.op = inverted_op
			return self
		return super().__invert__()


class Count(LazyNum):
	"""
	Lazily count the matches in a selector
	"""
	def evaluate(self, source, selector):
		return len(selector)


class OpAttr(LazyNum):
	"""
	Lazily evaluate Op over all tags in a selector.
	This is analogous to lazynum.Attr, which is equivalent to
	OpAttr(..., ..., sum)
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
