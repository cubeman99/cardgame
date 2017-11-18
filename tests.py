


from game import Game
from enums import *
from player import Player
import cards
import logic.actions as actions
from logic.selector import *
from utils import *
from colors import *
import sys
import random
import os
import traceback
import time

class Test:
	def __init__(self, test_case, test_func):
		self.test_case = test_case
		self.test_func = test_func
		self.pass_count = 0
		self.fail_count = 0
		self.passed = True

	def __str__(self):
		return "%s.%s" %(self.test_case.name, self.test_func.__name__)

	def expect(self, result):
		if result:
			self.pass_count += 1
		else:
			self.fail_count += 1
			frame = inspect.stack()[2]
			color_print("%s(%d): error: %s\n" %(frame.filename,
				frame.lineno, frame.code_context[0].lstrip().rstrip()))
		return result

	def run(self):
		color_print("{test_pass}[ RUN      ]{} %s\n" %(self))

		self.pass_count = 0
		self.fail_count = 0

		self.test_case.test = self
		self.start_time = time.time()

		exception = None

		try:
			self.test_func()
		except Exception as e:
			exception = e
			self.fail_count += 1
			traceback.print_exc()

		self.end_time = time.time()
		self.elapsed = self.end_time - self.start_time
		self.test_case.test = None

		self.passed = (self.fail_count == 0)

		if self.passed:
			color_print("{test_pass}[       OK ]{}")
		else:
			color_print("{test_fail}[  FAILED  ]{}")

		color_print(" %s (%d ms)\n" %(self, self.elapsed))

		return self.passed

def plural(word, list):
	if len(list) != 1:
		return word + "s"
	else:
		return word

class TestCase:
	def __init__(self):
		self.tests = [Test(self, getattr(self, t)) \
			for t in dir(self) if t.startswith("test_")]

	def setup(self):
		pass

	def cleanup(self):
		pass

	@property
	def name(self):
		return self.__class__.__name__

	def expect_eq(self, actual, expected):
		if not self.test.expect(actual == expected):
			color_print("  Actual: %r\n" %(actual))
			color_print("Exepcted: %r\n" %(expected))


	def main(self):
		tests = [Test(self, getattr(self, t)) for t in dir(self) if t.startswith("test_")]
		color_print("{test_pass}[==========]{} Running %d %s from %s\n" %(
			len(tests), plural("test", tests), self.__class__.__name__))

		start_time = time.time()
		self.setup()


		test_pass_count = 0
		test_fail_count = 0

		passed_tests = []
		failed_tests = []

		color_print("{test_pass}[----------]{} %d %s from %s\n" %(
			len(tests), plural("test", tests), self.name))

		for test in tests:
			passed = test.run()
			if passed:
				passed_tests.append(test)
			else:
				failed_tests.append(test)

		color_print("{test_pass}[----------]{} %d %s from %s\n" %(
			len(tests), plural("test", tests), self.name))


		self.cleanup()
		end_time = time.time()
		elapsed = end_time - start_time

		color_print("{test_pass}[==========]{} %d %s from %s ran. (%d ms total)\n" %(
			len(tests), plural("test", tests), self.name, elapsed))

		self.passed = (len(failed_tests) == 0)
		color_print("{test_pass}[  PASSED  ]{} %d %s.\n" %(
			len(passed_tests), plural("test", passed_tests)))
		if not self.passed:
			color_print("{test_fail}[  FAILED  ]{} %d %s, listed below:\n" %(
				len(failed_tests), plural("test", failed_tests)))
			for test in failed_tests:
				color_print("{test_fail}[  FAILED  ]{} %s\n" %(
					test))

def run_all_tests():

	global_dict = dict(globals())
	test_cases = []
	for key, value in global_dict.items():
		if inspect.isclass(value) and issubclass(value, TestCase) and value != TestCase:
			test_cases.append(value())

	tests = []
	for test_case in test_cases:
		tests += test_case.tests

	color_print("{test_pass}[==========]{} Running %d %s from %d %s.\n" %(
		len(tests), plural("test", tests),
		len(test_cases), plural("test case", tests)))
	color_print("{test_pass}[----------]{} Global test environment setup.\n")


	passed_tests = []
	failed_tests = []

	for test_case in test_cases:
		color_print("{test_pass}[----------]{} %d %s from %s\n" %(
			len(test_case.tests), plural("test", test_case.tests),
			test_case.name))
		test_case.setup()

		for test in test_case.tests:
			passed = test.run()
			if passed:
				passed_tests.append(test)
			else:
				failed_tests.append(test)

		test_case.cleanup()
		color_print("{test_pass}[----------]{} %d %s from %s (%d ms)\n" %(
			len(test_case.tests), plural("test", test_case.tests),
			test_case.name, 0))

	color_print("{test_pass}[----------]{} Global test environment cleanup.\n")
	color_print("{test_pass}[==========]{} %d %s from %d %s ran.\n" %(
		len(tests), plural("test", tests),
		len(test_cases), plural("test case", tests)))

	passed = (len(failed_tests) == 0)
	color_print("{test_pass}[  PASSED  ]{} %d %s.\n" %(
		len(passed_tests), plural("test", passed_tests)))
	if not passed:
		color_print("{test_fail}[  FAILED  ]{} %d %s, listed below:\n" %(
			len(failed_tests), plural("test", failed_tests)))
		for test in failed_tests:
			color_print("{test_fail}[  FAILED  ]{} %s\n" %(
				test))

	if len(failed_tests) == 0:
		exit(0)
	else:
		exit(1)






class CardTests(TestCase):

	def setup(self):
		cards.db.initialize()

	def cleanup(self):
		pass

	def test_infested_whale(self):
		game = Game()
		whale = game.player1.give("InfestedWhale")
		attacker = game.player2.give("SunkenGoliath")
		whale.play()
		attacker.play()

		self.expect_eq(len(game.player1.field), 1)

		game.action_block(game.player2,
			actions.Attack(attacker, whale), type=BlockType.ATTACK)

		self.expect_eq(len(game.player1.field), 2)
		self.expect_eq(whale.zone, Zone.DISCARD)

	def test_warpack_chieftan(self):
		game = Game()
		chief = game.player1.give("WarpackChieftan")
		chief.play()
		defender = game.player2.give("InfestedWhale")
		defender.play()

		self.expect_eq(len(game.player1.field), 1)
		self.expect_eq(game.player1.territory, 0)

		game.action_block(game.player1,
			actions.Attack(chief, defender), type=BlockType.ATTACK)

		self.expect_eq(defender.health, 1)
		self.expect_eq(game.player1.territory, 1)
		self.expect_eq(len(game.player1.field), 2)



if __name__=="__main__":
	run_all_tests()
