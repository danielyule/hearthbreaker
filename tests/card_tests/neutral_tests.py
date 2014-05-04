import random
from hsgame.agents.basic_agents import DoNothingBot
from tests.testing_agents import MinionPlayingAgent
from tests.testing_utils import generate_game_for
from hsgame.cards import *

__author__ = 'Daniel'

import unittest

class TestCommon(unittest.TestCase):

    def setUp(self):
        random.seed(1857)

    def test_NoviceEngineer(self):
        game = generate_game_for(NoviceEngineer, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].defense)
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual("Novice Engineer", game.current_player.minions[0].card.name)

        #Three cards to start, two for the two turns and one from the battlecry
        self.assertEqual(24, game.current_player.deck.left)

    def test_KoboldGeomancer(self):
        game = generate_game_for(KoboldGeomancer, IronbeakOwl, MinionPlayingAgent, MinionPlayingAgent)

        for i in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].defense)
        self.assertEqual(2, game.current_player.minions[0].max_defense)
        self.assertEqual(2, game.current_player.minions[0].attack_power)
        self.assertEqual(1, game.current_player.minions[0].spell_power)
        self.assertEqual(1, game.current_player.spell_power)

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].defense)
        self.assertEqual(2, game.other_player.minions[0].max_defense)
        self.assertEqual(2, game.other_player.minions[0].attack_power)
        self.assertEqual(0, game.other_player.minions[0].spell_power)
        self.assertEqual(0, game.other_player.spell_power)

    def test_ElvenArcher(self):
        game = generate_game_for(StonetuskBoar, ElvenArcher, MinionPlayingAgent, MinionPlayingAgent)

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual(1, game.current_player.minions[0].defense)
        self.assertEqual(1, game.current_player.minions[0].max_defense)
        self.assertEqual("Elven Archer", game.current_player.minions[0].card.name)



