import json
from pprint import pprint
from enums import *
from enum import IntEnum
import inspect


class CardData:
	def __init__(self, id):
		self.id = id
		self.tags = {}

	def __repr__(self):
		return self.id

	def __str__(self):
		return self.id

	@property
	def name(self):
		return self.tags[GameTag.NAME]

cards = []

def initialize():

	print("Initializing card details")

	# Load the json file.
	data = None
	with open("card_details.json") as data_file:
		data = json.load(data_file)

	# Parse each card.
	for id, tags in data.items():
		card = load_card(id, tags)
		if card:
			cards.append(card)

def load_card(id, tags):
	card = CardData(id)

	for key, value in tags.items():

		key = getattr(GameTag, key.upper(), None)
		if key == None:
			pass

		type = TAG_TYPES.get(key, int)
		if inspect.isclass(type) and issubclass(type, IntEnum):
			value = getattr(type, value.upper(), None)
			if value == None:
				pass
		card.tags[key] = value
	return card

def find(id):
	"""Find a card by it's card ID"""
	for card in cards:
		if card.id == id:
			return card
	return None

initialize()



