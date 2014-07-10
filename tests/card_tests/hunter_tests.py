import random
import unittest
import unittest.mock
from hsgame.agents.basic_agents import PredictableBot, DoNothingBot
from tests.testing_agents import SpellTestingAgent, MinionPlayingAgent, WeaponTestingAgent, \
    PredictableAgentWithoutHeroPower
from tests.testing_utils import generate_game_for
from hsgame.cards import *


class TestHunter(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_HuntersMark(self):
        game = generate_game_for(HuntersMark, MogushanWarden, SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, game.current_player.minions[0].health)
        self.assertEqual(7, game.current_player.minions[0].calculate_max_health())

        # This will play all the hunter's marks currently in the player's hand
        game.play_single_turn()
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].calculate_max_health())

    def test_TimberWolf(self):
        game = generate_game_for([StonetuskBoar, FaerieDragon, KoboldGeomancer, TimberWolf],
                                 StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[3].calculate_attack())
        self.assertEqual(3, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(6, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[5].calculate_attack())
        self.assertEqual(3, game.current_player.minions[4].calculate_attack())
        self.assertEqual(2, game.current_player.minions[3].calculate_attack())
        self.assertEqual(1, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())

        game.current_player.minions[1].die(None)
        game.current_player.minions[1].activate_delayed()
        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[4].calculate_attack())
        self.assertEqual(3, game.current_player.minions[3].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())

        game.current_player.minions[3].die(None)
        game.current_player.minions[3].activate_delayed()
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[3].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())

        wolf = game.current_player.minions[1]
        wolf.die(None)
        wolf.activate_delayed()
        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())

    def test_ArcaneShot(self):
        game = generate_game_for(ArcaneShot, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        game.players[0].spell_damage = 1
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
        self.assertEqual(3, game.current_player.hero.weapon.base_attack)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, game.current_player.hero.weapon.durability)
        self.assertEqual(3, game.current_player.hero.weapon.base_attack)

    def test_GladiatorsLongbow(self):
        game = generate_game_for(GladiatorsLongbow, WaterElemental, WeaponTestingAgent,
                                 MinionPlayingAgent)
        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertFalse(game.current_player.hero.frozen)
        self.assertFalse(game.current_player.hero.immune)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(4, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[1].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertFalse(game.current_player.hero.frozen)
        self.assertFalse(game.current_player.hero.immune)
        self.assertEqual(0, len(game.current_player.events))

    def test_Tracking(self):
        game = generate_game_for([Tracking, Tracking, Tracking, Tracking,
                                  StonetuskBoar, BloodfenRaptor, KoboldGeomancer],
                                 StonetuskBoar, SpellTestingAgent, DoNothingBot)

        game.play_single_turn()
        self.assertEqual(4, len(game.current_player.hand))
        self.assertEqual("Stonetusk Boar", game.current_player.hand[3].name)
        self.assertEqual(23, game.current_player.deck.left)

    def test_ExplosiveTrap(self):
        game = generate_game_for(ExplosiveTrap, StonetuskBoar, SpellTestingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(1, len(game.other_player.minions))

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(28, game.current_player.hero.health)
        self.assertEqual(29, game.other_player.hero.health)

        random.seed(1857)
        game = generate_game_for(ExplosiveTrap, Frostbolt, SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.secrets))
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(27, game.other_player.hero.health)

    def test_FreezingTrap(self):
        game = generate_game_for(FreezingTrap, StonetuskBoar, SpellTestingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(4, len(game.current_player.hand))
        self.assertEqual(3, game.current_player.hand[3].mana_cost(game.current_player))

    def test_FreezingTrap_many_cards(self):
        class FreezingTrapAgent(DoNothingBot):
            def do_turn(self, player):
                if player.mana == 6:
                    game.play_card(player.hand[0])
                if player.mana == 7:
                    player.minions[0].attack()
        game = generate_game_for(FreezingTrap, BoulderfistOgre, SpellTestingAgent, FreezingTrapAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        death_mock = unittest.mock.Mock()
        game.players[1].minions[0].bind_once("died", death_mock)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(10, len(game.current_player.hand))
        self.assertEqual(0, len(game.current_player.minions))
        for card in game.current_player.hand:
            self.assertEqual(6, card.mana_cost(game.current_player))
        self.assertEqual(30, game.other_player.hero.health)
        death_mock.assert_called_once_with(None)

    def test_Misdirection(self):
        game = generate_game_for(Misdirection, StonetuskBoar, SpellTestingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(28, game.other_player.hero.health)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(30, game.current_player.hero.health)
