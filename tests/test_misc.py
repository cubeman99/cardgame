
from .utils import *


def test_serialize():
	game1 = Game()
	game1.player1.give("OctopiExile")
	c1 = game1.player1.give("OctopiExile").play()
	c2 = game1.player2.give("OctopiExile").play()
	game1.player2.give("OctopiExile").play()
	c1.attack(c2)

	state1 = game1.serialize_state()

	game2 = Game()
	game2.deserialize_state(state1)
	state2 = game2.serialize_state()

	# DEBUG: Print out state differences.
	for id, tags1 in state1.items():
		tags2 = state2[id]
		for tag, value1 in tags1.items():
			value2 = tags2[tag]
			if value1 != value2:
				print("%d. %-30s: %-5s  %s == %s" %(id, tag, value1 == value2, value1, value2))
				print(state1[id][GameTag.CARD_ID])
				print(state2[id][GameTag.CARD_ID])

	expect_eq(str(state2), str(state1))