import random

from hsgame.agents.user_agents import Observer
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Deck, Game, card_lookup
from hsgame.agents.basic_agents import DoNothingBot


__author__ = 'Daniel'

import unittest
import io


class TestObserver(unittest.TestCase):
    def setUp(self):
        card_set1 = []
        card_set2 = []
        random.seed(1567)

        for cardIndex in range(0, 30):
            card_set1.append(card_lookup("Stonetusk Boar"))
            card_set2.append(card_lookup("Novice Engineer"))

        self.deck1 = Deck(card_set1, CHARACTER_CLASS.DRUID)
        self.deck2 = Deck(card_set2, CHARACTER_CLASS.MAGE)

    def test_observeBasicGame(self):
        agent1 = DoNothingBot()
        agent2 = DoNothingBot()
        game = Game([self.deck1, self.deck2], [agent1, agent2])
        string = io.StringIO()
        obs = Observer(string)
        obs.observe(game)
        game.start()
        self.assertEqual(6845, len(string.getvalue()))
