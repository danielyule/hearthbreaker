import random
import unittest

from hsgame.agents.basic_agents import PredictableBot
from tests.testing_agents import *
from tests.testing_utils import generate_game_for
from hsgame.cards import *


__author__ = 'Daniel'


class TestShaman(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_ShamanPower(self):
        game = generate_game_for(AlAkirTheWindlord, MogushanWarden, PredictableBot, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stoneclaw Totem", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].taunt)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Healing Totem", game.players[0].minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual("Searing Totem", game.players[0].minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual("Wrath of Air Totem", game.players[0].minions[0].card.name)
        self.assertEqual(1, game.players[0].minions[0].spell_damage)

        # All Totems are out, nothing should be summoned
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].minions))

    def test_AlAkirTheWindlord(self):
        game = generate_game_for(AlAkirTheWindlord, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Al'Akir the Windlord", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].wind_fury)
        self.assertTrue(game.players[0].minions[0].charge)
        self.assertTrue(game.players[0].minions[0].divine_shield)
        self.assertTrue(game.players[0].minions[0].taunt)

    def test_DustDevil(self):
        game = generate_game_for(DustDevil, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Dust Devil", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].wind_fury)
        self.assertEqual(2, game.players[0].overload)

        game.play_single_turn()
        # Overload should cause that we start this turn with 0 mana
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, game.players[0].overload)
        self.assertEqual(0, game.players[0].mana)
        self.assertEqual(2, game.players[0].max_mana)

    def test_EarthElemental(self):
        game = generate_game_for(EarthElemental, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        # Earth Elemental should be played
        for turn in range(0, 9):
            game.play_single_turn()
        
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Earth Elemental", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].taunt)
        self.assertEqual(3, game.players[0].overload)

    def test_FireElemental(self):
        game = generate_game_for(FireElemental, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 10):
            game.play_single_turn()
        
        self.assertEqual(30, game.players[1].hero.health)
        
        # Fire Elemental should be played, and its battlecry dealing three damage to opponent
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Fire Elemental", game.players[0].minions[0].card.name)
        self.assertEqual(27, game.players[1].hero.health)
