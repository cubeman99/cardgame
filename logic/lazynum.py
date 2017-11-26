import copy
import operator
from abc import ABCMeta, abstractmethod
from entity import *
from typing import Any, Union, List, Callable, Iterable, Optional, Set


BinaryOp = Callable[[Any, Any], bool]
UnaryOp = Callable[[Any], bool]

def evaluate(value, source):
	if isinstance(value, LazyNum):
		return value.eval(source)
	else:
		return value



class LazyValue(metaclass=ABCMeta):
	@abstractmethod
	def evaluate(self, source):
		pass

	def eval(self, game, source):
		return self.evaluate(source)


def _and(left, right):
	return left and right
def _or(left, right):
	return left or right
def _not(value):
	return not value

# Something that evaluates at runtime.
class LazyNum(LazyValue):
	def __init__(self, *args):
		self._args = args

	def eval(self, source):
		from logic.selector import Selector
		args = []
		for value in self._args:
			if isinstance(value, Selector):
				args.append(value.select(source.game, source))
			elif isinstance(value, LazyNum):
				args.append(value.eval(source))
			else:
				args.append(value)
		return self.evaluate(source, *args)

	def __repr__(self):
		text = "%s(" %(self.__class__.__name__)
		for i in range(0, len(self._args)):
			if i > 0:
				text += ", "
			text += "%r" %(self._args[i])
		text += ")"
		return text

	# TODO: remove this
	def then(self, _):
		pass

	def evaluate(self, source) -> int:
		raise NotImplementedError

	def _cmp(op):
		def func(self, other):
			if isinstance(other, (int, LazyNum)):
				# When comparing a LazyNum with an int, turn it into an
				# Evaluator that compares the int to the result of the LazyNum
				return LazyNumEvaluator(self, other, op)
			return getattr(super(), "__%s__" % (op))(other)
		return func

	#__eq__ = _cmp(operator.eq)
	#__ge__ = _cmp(operator.ge)
	#__gt__ = _cmp(operator.gt)
	#__le__ = _cmp(operator.le)
	#__lt__ = _cmp(operator.lt)

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
		return LazyNumOperation(operator.add, self, other)
	def __sub__(self, other):
		return LazyNumOperation(operator.sub, self, other)
	def __mul__(self, other):
		return LazyNumOperation(operator.mul, self, other)
	def __radd__(self, other):
		return LazyNumOperation(operator.add, other, self)
	def __rsub__(self, other):
		return LazyNumOperation(operator.sub, other, self)
	def __rmul__(self, other):
		return LazyNumOperation(operator.mul, other, self)

	# Binary comparison operators
	def __eq__(self, other):
		return LazyNumOperation(operator.eq, self, other)
	def __ne__(self, other):
		return LazyNumOperation(operator.ne, self, other)
	def __ge__(self, other):
		return LazyNumOperation(operator.ge, self, other)
	def __gt__(self, other):
		return LazyNumOperation(operator.gt, self, other)
	def __le__(self, other):
		return LazyNumOperation(operator.le, self, other)
	def __lt__(self, other):
		return LazyNumOperation(operator.lt, self, other)

	# Binary boolean operators
	def __and__(self, other):
		return LazyNumOperation(_and, self, other)
	def __or__(self, other):
		return LazyNumOperation(_or, self, other)
	def __rand__(self, other):
		return LazyNumOperation(_and, other, self)
	def __ror__(self, other):
		return LazyNumOperation(_or, other, self)

	def get_entities(self, source):
		from logic.selector import Selector
		if isinstance(self.selector, Selector):
			entities = self.selector.select(source.game, source)
		elif isinstance(self.selector, LazyValue):
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

class LazyNumOperation(LazyNum):
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
