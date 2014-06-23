from hsgame.agents.basic_agents import DoNothingBot
from hsgame.constants import CHARACTER_CLASS, MINION_TYPE
from hsgame.game_objects import card_lookup
from tests.testing_utils import generate_game_for
import unittest
import csv
from hsgame.cards import *

__author__ = 'Daniel'


class CardTest(unittest.TestCase):

    #Make sure that the cards have been initialized correctly based on the data in cards.csv
    def test_all_cards(self):
        fake_game = generate_game_for(StonetuskBoar, StonetuskBoar, DoNothingBot, DoNothingBot)
        file = open("cards.csv", "r")
        reader = csv.DictReader(file)
        for row in reader:
            if row['Implemented?'] == "yes":
                card = card_lookup(row["Name"])
                self.assertEqual(int(row["Cost"]), card.mana, row["Name"])
                self.assertEqual(CHARACTER_CLASS.from_str(row["Class"]), card.character_class, row["Name"])
                if row["Minion/Spell"] == "Minion":
                    minion = card.create_minion(fake_game.current_player)
                    minion.player = fake_game.current_player
                    minion.silence()
                    self.assertEqual(int(row["Attack"]), minion.attack_power, row["Name"])
                    self.assertEqual(int(row["Health"]), minion.health, row["Name"])
                    self.assertEqual(MINION_TYPE.from_str(row["Race"]), minion.minion_type, row["Name"])

        file.close()
