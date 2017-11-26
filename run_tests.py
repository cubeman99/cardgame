from cardgame.enums import *
from cardgame.game import Game
from tests import *
import inspect

# Initialize the card database
db.initialize()

run_all_tests([
	test_octopi,
	test_aard,
	test_mole,
	test_eel,
	test_pheasant,
	test_slug,
	test_drake,
	test_logic,
	test_misc,
	test_mechanics,
])
