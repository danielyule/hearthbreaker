import random
import unittest
from hsgame.replay import SavedGame
from tests.testing_agents import SpellTestingAgent, MinionPlayingAgent
from tests.testing_utils import generate_game_for

from hsgame.cards import *

__author__ = 'Daniel'

class TestMage(unittest.TestCase):

    def setUp(self):
        random.seed(1857)

    def testArcaneMissiles(self):
        game = generate_game_for(MogushanWarden, ArcaneMissiles, MinionPlayingAgent,SpellTestingAgent)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(27, game.other_player.health)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Mogu'shan Warden", game.current_player.minions[0].card.name)

        game.play_single_turn()
        #The random numbers work so that both arcane missiles hit the Warden twice and the other player once
        self.assertEqual(10, game.other_player.health)
        self.assertEqual(3, game.other_player.minions[0].defense)

    def testArcaneMissilesWithSpellPower(self):
        game = SavedGame("tests/replays/card_tests/ArcaneMissilesWithSpellDamage.rep")
        game.start()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].defense)
        self.assertEqual(2, game.other_player.minions[0].max_defense)
        self.assertEqual(27, game.other_player.health)

        return game
