import random
import unittest

from hearthbreaker.agents.basic_agents import DoNothingBot
from tests.agents.testing_agents import SpellTestingAgent, MinionPlayingAgent, PredictableAgentWithoutHeroPower
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *


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


class TestGameCopying(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_base_game_copying(self):
        game = generate_game_for(StonetuskBoar, StonetuskBoar, MinionPlayingAgent, MinionPlayingAgent)

        new_game = game.copy()

        self.assertEqual(0, new_game.current_player.mana)

        for turn in range(0, 10):
            new_game.play_single_turn()

        self.assertEqual(5, len(new_game.current_player.minions))

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))


class TestMinionCopying(unittest.TestCase):
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
        game.current_player.minions[4].die(None)
        game.current_player.minions[3].die(None)
        game.current_player.minions[2].die(None)
        game.current_player.minions[1].die(None)
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

    def test_SavannahHighmane(self):
        game = generate_game_for([SavannahHighmane, SiphonSoul], FacelessManipulator,
                                 MinionPlayingAgent, create_enemy_copying_agent(6))
        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual("Hyena", game.players[1].minions[0].card.name)
        self.assertEqual("Hyena", game.players[1].minions[1].card.name)

    def test_TimberWolf(self):
        game = generate_game_for(TimberWolf,
                                 [StonetuskBoar, BloodfenRaptor, IronfurGrizzly,
                                  OasisSnapjaw, FacelessManipulator, Maexxna],
                                 MinionPlayingAgent, create_enemy_copying_agent())

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(5, len(game.current_player.minions))

        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[1].calculate_attack())
        self.assertEqual(4, game.current_player.minions[2].calculate_attack())
        self.assertEqual(4, game.current_player.minions[3].calculate_attack())
        self.assertEqual(2, game.current_player.minions[4].calculate_attack())

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[2].calculate_attack())
        self.assertEqual(4, game.current_player.minions[3].calculate_attack())
        self.assertEqual(4, game.current_player.minions[3].calculate_attack())
        self.assertEqual(2, game.current_player.minions[5].calculate_attack())

    def test_UnstableGhoul(self):
        game = generate_game_for([StonetuskBoar, FaerieDragon, MagmaRager,
                                  SenjinShieldmasta, UnstableGhoul, Frostbolt], FacelessManipulator,
                                 MinionPlayingAgent, create_enemy_copying_agent(5))

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual(4, game.current_player.minions[1].health)
        self.assertEqual(1, game.current_player.minions[2].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(30, game.other_player.hero.health)

    def test_Webspinner(self):
        game = generate_game_for([OasisSnapjaw, Webspinner, MortalCoil],
                                 [GoldshireFootman, GoldshireFootman, FacelessManipulator],
                                 MinionPlayingAgent, create_enemy_copying_agent(1))

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(8, len(game.other_player.hand))
        self.assertEqual(ScavengingHyena, type(game.other_player.hand[7]))

    def test_Duplicate(self):
        game = generate_game_for([BloodfenRaptor, Duplicate], ShadowBolt, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        new_game = game.copy()

        # because copying is supposed to happen mid-turn, we have to deactivate the secrets that are
        # automatically activated.  Don't worry though, they'll be re-activated when the turn starts.
        for secret in new_game.other_player.secrets:
            secret.deactivate(new_game.other_player)
        new_game.play_single_turn()

        self.assertEqual(6, len(new_game.other_player.hand))
        self.assertEqual("Bloodfen Raptor", new_game.other_player.hand[4].name)
        self.assertEqual("Bloodfen Raptor", new_game.other_player.hand[5].name)
        self.assertEqual(0, len(new_game.other_player.secrets))

    def test_StoneskinGargoyle(self):
        game = generate_game_for(Frostbolt, StoneskinGargoyle, MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)

        new_game = game.copy()

        new_game.play_single_turn()
        self.assertEqual(2, len(new_game.current_player.minions))
        self.assertEqual(4, new_game.current_player.minions[0].health)
        self.assertEqual(4, new_game.current_player.minions[1].health)
        new_game.play_single_turn()

        self.assertEqual(2, len(new_game.other_player.minions))
        self.assertEqual(1, new_game.other_player.minions[0].health)
        self.assertEqual(4, new_game.other_player.minions[1].health)

        new_game.other_player.minions[0].silence()

        new_game.play_single_turn()

        self.assertEqual(3, len(new_game.current_player.minions))
        self.assertEqual(4, new_game.current_player.minions[0].health)
        self.assertEqual(1, new_game.current_player.minions[1].health)
        self.assertEqual(4, new_game.current_player.minions[2].health)

    def test_SludgeBelcher(self):
        game = generate_game_for([SludgeBelcher, Fireball], FacelessManipulator, MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual(5, game.current_player.minions[0].health)

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertTrue(game.other_player.minions[0].taunt)
        self.assertEqual(2, game.other_player.minions[0].health)

    def test_FaerieDragon(self):
        game = generate_game_for(FaerieDragon, Frostbolt, MinionPlayingAgent, SpellTestingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        new_game = game.copy()
        self.assertEqual(1, len(new_game.current_player.minions))

        def check_no_dragon(targets):
            self.assertNotIn(new_game.other_player.minions[0], targets)
            return targets[0]

        def check_dragon(targets):
            self.assertIn(new_game.other_player.minions[0], targets)
            return targets[0]

        new_game.other_player.agent.choose_target = check_no_dragon

        new_game.play_single_turn()
        new_game.play_single_turn()

        new_game.other_player.agent.choose_target = check_dragon
        new_game.current_player.minions[0].silence()
        new_game.play_single_turn()

    def test_BaronRivendare(self):
        game = generate_game_for([BloodmageThalnos, HarvestGolem, BaronRivendare], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 7):
            game.play_single_turn()
        game = game.copy()
        self.assertEqual(3, len(game.current_player.minions))
        game.current_player.minions[1].die(None)
        game.check_delayed()
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual("Baron Rivendare", game.current_player.minions[0].card.name)
        self.assertEqual("Damaged Golem", game.current_player.minions[1].card.name)
        self.assertEqual("Damaged Golem", game.current_player.minions[2].card.name)
        self.assertEqual("Bloodmage Thalnos", game.current_player.minions[3].card.name)

        # Check silence on the Baron
        self.assertEqual(4, len(game.current_player.hand))
        game.current_player.minions[0].silence()
        game.current_player.minions[3].die(None)
        game.check_delayed()
        self.assertEqual(5, len(game.current_player.hand))

    def test_BaronRivendareFaceless(self):
        game = generate_game_for([HarvestGolem, FacelessManipulator], BaronRivendare,
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        game.current_player.minions[1].die(None)
        game.check_delayed()

        self.assertEqual(3, len(game.current_player.minions))

    def test_DancingSwords(self):
        game = generate_game_for(DancingSwords, ShadowBolt, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, len(game.other_player.hand))
        game = game.copy()
        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(9, len(game.current_player.hand))

    def test_Deathlord(self):
        game = generate_game_for(Deathlord, [HauntedCreeper, OasisSnapjaw, Frostbolt, WaterElemental, Pyroblast],
                                 MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))

        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))

        self.assertEqual("Water Elemental", game.other_player.minions[0].card.name)

        game = game.copy()

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))

        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(2, len(game.other_player.minions))

        self.assertEqual("Oasis Snapjaw", game.other_player.minions[1].card.name)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, len(game.other_player.minions))

        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))

        self.assertEqual("Water Elemental", game.other_player.minions[2].card.name)

    def test_Reincarnate(self):
        game = generate_game_for([SylvanasWindrunner, Reincarnate], FacelessManipulator,
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 13):
            game.play_single_turn()

        # Sylvanas will die to the reincarnate, steal the Ogre, then be reborn.
        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual("Faceless Manipulator", game.other_player.minions[0].card.name)
        self.assertEqual("Sylvanas Windrunner", game.other_player.minions[1].card.name)
        self.assertEqual("Sylvanas Windrunner", game.other_player.minions[2].card.name)

    def test_Voidcaller(self):
        game = generate_game_for(Assassinate, [Voidcaller, FlameImp, ArgentSquire, BoulderfistOgre, StonetuskBoar],
                                 SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Voidcaller", game.current_player.minions[0].card.name)
        game = game.copy()
        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Flame Imp", game.other_player.minions[0].card.name)
