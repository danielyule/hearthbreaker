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
        self.assertEqual(1, game.current_player.minions[0].health)
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual("Novice Engineer", game.current_player.minions[0].card.name)

        #Three cards to start, two for the two turns and one from the battlecry
        self.assertEqual(24, game.current_player.deck.left)

    def test_KoboldGeomancer(self):
        game = generate_game_for(KoboldGeomancer, IronbeakOwl, MinionPlayingAgent, MinionPlayingAgent)

        for i in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual(2, game.current_player.minions[0].max_health)
        self.assertEqual(2, game.current_player.minions[0].attack_power)
        self.assertEqual(1, game.current_player.minions[0].spell_power)
        self.assertEqual(1, game.current_player.spell_power)

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].health)
        self.assertEqual(2, game.other_player.minions[0].max_health)
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
        self.assertEqual(1, game.current_player.minions[0].health)
        self.assertEqual(1, game.current_player.minions[0].max_health)
        self.assertEqual("Elven Archer", game.current_player.minions[0].card.name)

    def test_ArgentSquire(self):
        game = generate_game_for(ArgentSquire, ElvenArcher, MinionPlayingAgent, MinionPlayingAgent)
        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].divine_shield)

        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertFalse(game.other_player.minions[0].divine_shield)

    def test_SilvermoonGuardian(self):
        game = generate_game_for(SilvermoonGuardian, ElvenArcher, MinionPlayingAgent, MinionPlayingAgent)
        
        for i in range(0, 7):
            game.play_single_turn()
        
        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].divine_shield)

        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertFalse(game.other_player.minions[0].divine_shield)

    def test_TwilightDrake(self):
        game = generate_game_for(TwilightDrake, ElvenArcher, MinionPlayingAgent, DoNothingBot)
        
        for i in range(0, 7):
            game.play_single_turn()
        
        # 7 cards in hand, Twilight Drake should be played, making it 6 cards left in hand, giving the drake +6 health (a total of 7)
        self.assertEqual(6, len(game.current_player.hand))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, game.current_player.minions[0].max_health)
        self.assertEqual(7, game.current_player.minions[0].health)