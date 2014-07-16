import random
import unittest

from tests.testing_agents import *
from tests.testing_utils import generate_game_for
from hsgame.cards import *


class TestWarrior(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_ArathiWeaponsmith(self):
        game = generate_game_for(ArathiWeaponsmith, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        # Arathi Weaponsmith should be played
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual("Arathi Weaponsmith", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].hero.weapon.base_attack)
        self.assertEqual(2, game.players[0].hero.weapon.durability)
