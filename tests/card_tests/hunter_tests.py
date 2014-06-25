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

    def test_TimberWolf(self):
        game = generate_game_for([StonetuskBoar, FaerieDragon, KoboldGeomancer, TimberWolf],
                                 StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[3].attack_power)
        self.assertEqual(3, game.current_player.minions[2].attack_power)
        self.assertEqual(2, game.current_player.minions[1].attack_power)
        self.assertEqual(1, game.current_player.minions[0].attack_power)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(6, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[5].attack_power)
        self.assertEqual(3, game.current_player.minions[4].attack_power)
        self.assertEqual(2, game.current_player.minions[3].attack_power)
        self.assertEqual(1, game.current_player.minions[2].attack_power)
        self.assertEqual(2, game.current_player.minions[1].attack_power)
        self.assertEqual(3, game.current_player.minions[0].attack_power)

        game.current_player.minions[1].die(None)
        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[4].attack_power)
        self.assertEqual(3, game.current_player.minions[3].attack_power)
        self.assertEqual(2, game.current_player.minions[2].attack_power)
        self.assertEqual(1, game.current_player.minions[1].attack_power)
        self.assertEqual(3, game.current_player.minions[0].attack_power)

        game.current_player.minions[3].die(None)
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[3].attack_power)
        self.assertEqual(2, game.current_player.minions[2].attack_power)
        self.assertEqual(1, game.current_player.minions[1].attack_power)
        self.assertEqual(3, game.current_player.minions[0].attack_power)

        wolf = game.current_player.minions[1]
        wolf.die(None)
        wolf.activate_delayed()
        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[2].attack_power)
        self.assertEqual(2, game.current_player.minions[1].attack_power)
        self.assertEqual(3, game.current_player.minions[0].attack_power)

    def test_ArcaneShot(self):
        game = generate_game_for(ArcaneShot, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        game.players[0].spell_power = 1
        game.play_single_turn()
        self.assertEqual(27, game.other_player.hero.health)

    def test_BestialWrath(self):

        def verify_bwrath():
            self.assertEqual(2, game.other_player.minions[0].temp_attack)
            self.assertTrue(game.other_player.minions[0].immune)

        game = generate_game_for(StonetuskBoar, BestialWrath, MinionPlayingAgent, SpellTestingAgent)
        game.play_single_turn()
        game.other_player.bind("turn_ended", verify_bwrath)
        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertFalse(game.other_player.minions[0].immune)
        self.assertEqual(0, game.other_player.minions[0].temp_attack)

    def test_Flare(self):

        game = generate_game_for(Vaporize, [WorgenInfiltrator, WorgenInfiltrator, ArcaneShot, Flare],
                                 SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(2, len(game.other_player.minions))
        self.assertTrue(game.other_player.minions[0].stealth)
        self.assertTrue(game.other_player.minions[1].stealth)
        self.assertEqual(3, len(game.other_player.hand))

        old_play = game.other_player.agent.do_turn

        def _play_and_attack(player):
            old_play(player)
            player.minions[2].attack()

        game.other_player.agent.do_turn = _play_and_attack
        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual(4, len(game.current_player.minions))
        self.assertFalse(game.current_player.minions[2].stealth)
        self.assertFalse(game.current_player.minions[3].stealth)
        self.assertEqual(2, len(game.current_player.hand))

    def test_EaglehornBow(self):
        game = generate_game_for(EaglehornBow, EyeForAnEye, PredictableBot, SpellTestingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(2, game.current_player.hero.weapon.durability)
        self.assertEqual(3, game.current_player.hero.weapon.attack_power)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, game.current_player.hero.weapon.durability)
        self.assertEqual(3, game.current_player.hero.weapon.attack_power)

