import copy
import re
from ..enums import *
from ..utils import listify
from .lazynum import LazyNum


class Condition:
	"""
	Lazily evaluate a condition at runtime.

	Condition must implement the check() method, which determines whether they
	evaluate to True in the current state.
	"""
	def __init__(self):
		self._if = None
		self._else = None
		self._neg = False

	def __repr__(self):
		condition_text = ""
		if hasattr(self, "text"):
			args = re.findall("{([_a-zA-Z0-9]+)}", self.text)
			condition_text = self.text
			for arg in args:
				condition_text = condition_text.replace("{%s}" %(arg), str(getattr(self, arg)))
		else:
			condition_text =  "%s" % (self.__class__.__name__)
		return "If %s, then %r" % (condition_text, self._if)

	# Negation acts as a NOT operator
	def __neg__(self):
		ret = copy.copy(self)
		ret._neg = not self._neg
		return ret

	# Negation acts as a NOT operator
	def __invert__(self):
		ret = copy.copy(self)
		ret._neg = not self._neg
		return ret

	# AND operator acts as a "then" clause
	def __and__(self, action):
		ret = copy.copy(self)
		ret._if = action
		return ret

	def then(self, action):
		ret = copy.copy(self)
		ret._if = action
		return ret

	# OR operator acts as an "else" clause
	def __or__(self, action):
		ret = copy.copy(self)
		ret._else = action
		return ret

	def evaluate(self, source):
		"""
		Evaluates the board state from `source` and returns an iterable of
		Actions as a result.
		"""
		return self.check(source)
		ret = self.check(source)
		if self._neg:
			ret = not ret
		if ret:
			if self._if:
				return self._if
		elif self._else:
			return self._else

	def trigger(self, source):
		"""
		Triggers all actions meant to trigger on the board state from `source`.
		"""
		actions = self.evaluate(source)
		if actions:
			if not hasattr(actions, "__iter__"):
				actions = (actions, )
			source.game.trigger_actions(source, actions)

#------------------------------------------------------------------------------
# Conditions
#------------------------------------------------------------------------------

class Dead(LazyNum):
	"""
	Evaluates to True if every target in \a selector is dead
	"""
	text = "{selector} is dead"

	def evaluate(self, source, selector):
		for target in listify(selector):
			if not target.dead:
				return False
		return True


class Alive(LazyNum):
	"""
	Evaluates to True if every target in \a selector is alive.
	"""
	text = "{selector} is alive"

	def evaluate(self, source, selector):
		for target in listify(selector):
			if target.dead:
				return False
		return True

class Exists(LazyNum):
	"""
	Evaluates to True if \a selector has a match.
	"""
	def evaluate(self, source, selector, count=1):
		return bool(len(selector) >= count)


IfExists = Exists

