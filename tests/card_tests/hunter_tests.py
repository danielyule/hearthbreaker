import random
import unittest
from hsgame.agents.basic_agents import PredictableBot, DoNothingBot
from tests.testing_agents import SpellTestingAgent, MinionPlayingAgent
from tests.testing_utils import generate_game_for
from hsgame.cards import *

__author__ = 'Daniel'


class TestHunter(unittest.TestCase):

    def setUp(self):
        random.seed(1857)

    def test_hunter_power(self):
        game = generate_game_for(HuntersMark, MogushanWarden, PredictableBot, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(28, game.other_player.hero.health)

    def test_HuntersMark(self):
        game = generate_game_for(HuntersMark, MogushanWarden, SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, game.current_player.minions[0].health)
        self.assertEqual(7, game.current_player.minions[0].max_health)

        #This will play all the hunter's marks currently in the player's hand
        game.play_single_turn()
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].max_health)
