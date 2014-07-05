import random
import unittest
from tests.testing_agents import *
from tests.testing_utils import generate_game_for
from hsgame.cards import *


class TestRogue(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_DefiasRingleader(self):
        game = generate_game_for(DefiasRingleader, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Defias Ringleader", game.players[0].minions[0].card.name)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))

        # Combo should activate this turn
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual("Defias Bandit", game.players[0].minions[1].card.name)
        self.assertEqual(2, game.players[0].minions[1].attack_power)
        self.assertEqual(1, game.players[0].minions[1].health)
