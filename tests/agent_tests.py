from hsgame.agents.user_agents import Observer
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Deck, Game
from hsgame.agents.basic_agents import DoNothingBot

__author__ = 'Daniel'

import unittest
import sys
from hsgame.cards.minions import StonetuskBoar, NoviceEngineer

class TestObserver(unittest.TestCase):

    def setUp(self):
        card_set1 = []
        card_set2 = []

        for cardIndex in range(0, 30):
            card_set1.append(StonetuskBoar())
            card_set2.append(NoviceEngineer())

        self.deck1 = Deck(card_set1, CHARACTER_CLASS.DRUID)
        self.deck2 = Deck(card_set2, CHARACTER_CLASS.MAGE)

    def test_observeBasicGame(self):
        agent1 = DoNothingBot()
        agent2 = DoNothingBot()
        game = Game([self.deck1, self.deck2], [agent1, agent2])
        obs = Observer(sys.stdout)
        obs.observe(game)
        game.start()
