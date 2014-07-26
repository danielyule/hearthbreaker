import random
import unittest
from tests.testing_agents import *
from tests.testing_utils import generate_game_for
from hsgame.cards import *


def create_enemy_copying_agent(turn_to_play=1):
    class EnemyCopyingAgent(SpellTestingAgent):
        def __init__(self):
            super().__init__()
            self.turn = 0

        def choose_target(self, targets):
            for target in targets:
                if target.player is not target.player.game.current_player:
                    return target
            return super().choose_target(targets)

        def do_turn(self, player):
            self.turn += 1
            if self.turn >= turn_to_play:
                return super().do_turn(player)

    return EnemyCopyingAgent


def create_friendly_copying_agent(turn_to_play=1):
    class FriendlyCopyingAgent(SpellTestingAgent):
        def __init__(self):
            super().__init__()
            self.turn = 0

        def choose_target(self, targets):
            for target in targets:
                if target.player is not target.player.game.other_player:
                    return target
            return super().choose_target(targets)

        def do_turn(self, player):
            self.turn += 1
            if self.turn >= turn_to_play:
                return super().do_turn(player)

    return FriendlyCopyingAgent


class TestCopying(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_StormwindChampion(self):
        game = generate_game_for(StormwindChampion, [Abomination, BoulderfistOgre, FacelessManipulator],
                                 MinionPlayingAgent, create_enemy_copying_agent(5))
        for turn in range(0, 14):
            game.play_single_turn()

        self.assertEqual(6, game.current_player.minions[0].calculate_attack())
        self.assertEqual(6, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(7, game.current_player.minions[1].calculate_attack())
        self.assertEqual(8, game.current_player.minions[1].calculate_max_health())
        self.assertEqual(5, game.current_player.minions[2].calculate_attack())
        self.assertEqual(5, game.current_player.minions[2].calculate_max_health())

    def test_ForceOfNature(self):
        game = generate_game_for([ForceOfNature, Innervate, FacelessManipulator], StonetuskBoar,
                                 create_friendly_copying_agent(10), DoNothingBot)
        for turn in range(0, 18):
            game.play_single_turn()

        def check_minions():
            self.assertEqual(4, len(game.current_player.minions))

            for minion in game.current_player.minions:
                self.assertEqual(2, minion.calculate_attack())
                self.assertEqual(2, minion.health)
                self.assertEqual(2, minion.calculate_max_health())
                self.assertTrue(minion.charge)
                self.assertEqual("Treant", minion.card.name)

        game.other_player.bind_once("turn_ended", check_minions)

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))

    def test_Abomination(self):
        game = generate_game_for(Abomination, FacelessManipulator,
                                 MinionPlayingAgent, create_enemy_copying_agent(5))

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].taunt)
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(28, game.current_player.hero.health)
        self.assertEqual(28, game.other_player.hero.health)
        self.assertEqual(2, game.other_player.minions[0].health)

    def test_SoulOfTheForest(self):
        game = generate_game_for([Abomination, SoulOfTheForest], FacelessManipulator,
                                 SpellTestingAgent, create_enemy_copying_agent(6))

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Treant", game.current_player.minions[0].card.name)
        self.assertEqual(28, game.current_player.hero.health)
        self.assertEqual(28, game.other_player.hero.health)

    def test_NerubianEgg(self):
        game = generate_game_for(NerubianEgg, FacelessManipulator, MinionPlayingAgent, create_enemy_copying_agent(5))

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(4, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(0, game.current_player.minions[0].calculate_attack())
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())

    def test_ScavangingHyena(self):
        game = generate_game_for([ChillwindYeti, ScavengingHyena],
                                 [StonetuskBoar, StonetuskBoar, StonetuskBoar, StonetuskBoar, FacelessManipulator],
                                 MinionPlayingAgent, create_enemy_copying_agent())

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual("Scavenging Hyena", game.current_player.minions[0].card.name)
        game.current_player.minions[1].die(None)
        game.current_player.minions[2].die(None)
        game.current_player.minions[3].die(None)
        game.current_player.minions[4].die(None)
        game.check_delayed()
        self.assertEqual(10, game.current_player.minions[0].calculate_attack())
        self.assertEqual(6, game.current_player.minions[0].calculate_max_health())

        self.assertEqual(2, game.other_player.minions[0].calculate_attack())
        self.assertEqual(2, game.other_player.minions[0].calculate_max_health())

    def test_Maexxna_and_EmperorCobra(self):
        game = generate_game_for([Maexxna, EmperorCobra], FacelessManipulator,
                                 PredictableAgentWithoutHeroPower, create_enemy_copying_agent(6))
        for turn in range(0, 13):
            game.play_single_turn()

        # The faceless should have copied Maexxna, then the following turn
        # Maexxna should attack the copy, resulting in both dying.  All that should
        # be left is the cobra played this turn

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual("Emperor Cobra", game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual("Maexxna", game.current_player.minions[0].card.name)

    def test_BestialWrath(self):
        def verify_bwrath():
            self.assertEqual(2, game.current_player.minions[1].temp_attack)
            self.assertTrue(game.current_player.minions[1].immune)
            self.assertEqual(2, game.current_player.minions[0].temp_attack)
            self.assertTrue(game.current_player.minions[0].immune)

        game = generate_game_for([StampedingKodo, BestialWrath, FacelessManipulator], StonetuskBoar,
                                 create_friendly_copying_agent(5), DoNothingBot)

        for turn in range(0, 10):
            game.play_single_turn()

        # we need to check that there are two immune kodos at the end of the turn
        game.other_player.bind("turn_ended", verify_bwrath)

        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))

    def test_HarvestGolem(self):
        game = generate_game_for(FacelessManipulator, HarvestGolem, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(1, len(game.current_player.minions))

    def test_HauntedCreeper(self):
        game = generate_game_for(FacelessManipulator, HauntedCreeper, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(2, len(game.current_player.minions))

    def test_TheBeast(self):
        game = generate_game_for(TheBeast, FacelessManipulator, MinionPlayingAgent, create_enemy_copying_agent(6))

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(2, len(game.other_player.minions))

    def test_AnubarAmbusher(self):
        game = generate_game_for(AnubarAmbusher,
                                 [StonetuskBoar, StonetuskBoar, StonetuskBoar, StonetuskBoar, FacelessManipulator],
                                 MinionPlayingAgent, create_enemy_copying_agent())

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(4, len(game.current_player.hand))

        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(5, len(game.current_player.hand))

    def test_TundraRhino(self):
        game = generate_game_for(TundraRhino, [OasisSnapjaw, FacelessManipulator],
                                 MinionPlayingAgent, create_enemy_copying_agent())

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].charge)
        self.assertTrue(game.current_player.minions[1].charge)

    def test_StarvingBuzzard(self):
        game = generate_game_for(StarvingBuzzard, [StonetuskBoar, FacelessManipulator, Maexxna, CoreHound],
                                 MinionPlayingAgent, create_enemy_copying_agent())

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(8, len(game.current_player.hand))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(9, len(game.current_player.hand))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(9, len(game.current_player.hand))