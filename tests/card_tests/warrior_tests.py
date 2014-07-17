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

    def test_Armorsmith(self):
        game = generate_game_for(Armorsmith, StonetuskBoar, MinionPlayingAgent, PredictableAgentWithoutHeroPower)

        # Armorsmith should be played
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual("Armorsmith", game.players[0].minions[0].card.name)
        self.assertEqual(0, game.players[0].hero.armor)

        # Three Stonetusks should attack, generating one armor each
        game.play_single_turn()
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].hero.armor)

    def test_CruelTaskmaster(self):
        game = generate_game_for(CruelTaskmaster, Shieldbearer, MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(0, game.players[1].minions[0].calculate_attack())
        self.assertEqual(4, game.players[1].minions[0].health)

        # Cruel Taskmaster should be played, targeting the Shieldbearer
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual("Cruel Taskmaster", game.players[0].minions[0].card.name)
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[1].minions[0].calculate_attack())
        self.assertEqual(3, game.players[1].minions[0].health)

    def test_FrothingBerserker(self):
        game = generate_game_for(FrothingBerserker, AngryChicken, MinionPlayingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(3, len(game.players[1].minions))

        # FrothingBerserker should be played
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual("Frothing Berserker", game.players[0].minions[0].card.name)

        # Three chickens should attack, generating a total of +6 attack for the Frothing Berserker
        game.play_single_turn()
        self.assertEqual(8, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)
