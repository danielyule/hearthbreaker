import copy
import random
import unittest

from hearthbreaker.agents.basic_agents import DoNothingBot, PredictableBot
from hearthbreaker.constants import MINION_TYPE
from tests.agents.testing_agents import SpellTestingAgent, MinionPlayingAgent, PredictableAgentWithoutHeroPower, \
    EnemyMinionSpellTestingAgent
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
        self.assertEqual(MINION_TYPE.DEMON, game.other_player.minions[0].card.minion_type)

    def test_SorcerersApprentice(self):
        game = generate_game_for([SorcerersApprentice, ArcaneMissiles, SorcerersApprentice, Frostbolt, Frostbolt,
                                  Frostbolt], StonetuskBoar, SpellTestingAgent, DoNothingBot)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual("Sorcerer's Apprentice", game.current_player.minions[0].card.name)

        # Arcane missiles should also have been played, since it is now free
        self.assertEqual(27, game.other_player.hero.health)

        game = game.copy()
        # Make sure the other frostbolts have been properly reduced
        self.assertEqual(1, game.current_player.hand[1].mana_cost(game.current_player))
        self.assertEqual(1, game.current_player.hand[2].mana_cost(game.current_player))

        game.play_single_turn()
        game.play_single_turn()

        # Both Sorcer's Apprentices are killed by friendly Frostbolts.
        self.assertEqual(0, len(game.current_player.minions))

        # Make sure that the cards in hand are no longer reduced
        self.assertEqual(2, game.current_player.hand[0].mana_cost(game.current_player))

    def test_Loatheb(self):
        game = generate_game_for(Loatheb, [Assassinate, BoulderfistOgre], MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        game = game.copy()

        self.assertEqual(10, game.other_player.hand[0].mana_cost(game.other_player))
        self.assertEqual(6, game.other_player.hand[1].mana_cost(game.other_player))

        game.play_single_turn()

        self.assertEqual(5, game.current_player.hand[0].mana_cost(game.current_player))
        self.assertEqual(6, game.current_player.hand[1].mana_cost(game.current_player))

    def test_KirinTorMage(self):
        game = generate_game_for([KirinTorMage, BoulderfistOgre, Spellbender],
                                 StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 4):
            game.play_single_turn()

        def check_secret_cost():
            new_game = game.copy()
            self.assertEqual(1, len(new_game.current_player.minions))
            self.assertEqual("Kirin Tor Mage", new_game.current_player.minions[0].card.name)
            self.assertEqual(0, new_game.current_player.hand[1].mana_cost(game.current_player))
            self.assertEqual("Spellbender", new_game.current_player.hand[1].name)

        game.other_player.bind_once("turn_ended", check_secret_cost)
        game.play_single_turn()

    def test_WaterElemental(self):
        game = generate_game_for(WaterElemental, StonetuskBoar, PredictableBot, DoNothingBot)

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(25, game.other_player.hero.health)
        self.assertFalse(game.other_player.hero.frozen_this_turn)
        self.assertFalse(game.other_player.hero.frozen)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertEqual(6, game.current_player.minions[0].health)
        self.assertEqual("Water Elemental", game.current_player.minions[0].card.name)

        game = game.copy()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(22, game.other_player.hero.health)

        # Always false after the end of a turn
        self.assertFalse(game.other_player.hero.frozen_this_turn)
        self.assertTrue(game.other_player.hero.frozen)

        # Now make sure that attacking the Water Elemental directly will freeze a character
        random.seed(1857)
        game = generate_game_for(WaterElemental, IronbarkProtector, MinionPlayingAgent, PredictableBot)
        for turn in range(0, 7):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(5, game.other_player.minions[0].health)
        # The player won't have taken damage because of armor, and so shouldn't be frozen
        self.assertEqual(30, game.current_player.hero.health)
        self.assertFalse(game.current_player.hero.frozen)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(28, game.current_player.hero.health)
        self.assertTrue(game.current_player.hero.frozen)

    def test_BlessingOfWisdom(self):
        game = generate_game_for([OasisSnapjaw, BlessingOfWisdom, CoreHound], [FacelessManipulator, CoreHound],
                                 MinionPlayingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 12):
            game.play_single_turn()

        # The blessing of wisdom should be attached to the Oasis Snapjaw, which the Faceless has copied.
        # The copied snapjaw should still draw cards for the first player

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Oasis Snapjaw", game.current_player.minions[0].card.name)

        self.assertEqual(8, len(game.other_player.hand))

    def test_TirionFordring(self):
        game = generate_game_for(TirionFordring, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        # Tirion Fordring should be played
        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)
        self.assertEqual("Tirion Fordring", game.players[0].minions[0].card.name)
        self.assertEqual(None, game.players[0].hero.weapon)

        game = game.copy()

        # Let Tirion Fordring die, and a weapon should be equiped
        tirion = game.players[0].minions[0]
        tirion.die(None)
        tirion.activate_delayed()
        self.assertEqual(5, game.players[0].hero.weapon.base_attack)
        self.assertEqual(3, game.players[0].hero.weapon.durability)

    def test_Undertaker(self):
        game = generate_game_for([Undertaker, GoldshireFootman, HarvestGolem, AnubarAmbusher], HauntedCreeper,
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual("Goldshire Footman", game.current_player.minions[0].card.name)
        self.assertEqual("Undertaker", game.current_player.minions[1].card.name)
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())

        new_game = game.copy()

        new_game.play_single_turn()

        self.assertEqual(1, new_game.other_player.minions[1].calculate_attack())
        self.assertEqual(2, new_game.other_player.minions[1].calculate_max_health())

        new_game.play_single_turn()

        self.assertEqual(3, len(new_game.current_player.minions))
        self.assertEqual("Harvest Golem", new_game.current_player.minions[0].card.name)
        self.assertEqual("Goldshire Footman", new_game.current_player.minions[1].card.name)
        self.assertEqual("Undertaker", new_game.current_player.minions[2].card.name)
        self.assertEqual(2, new_game.current_player.minions[2].calculate_attack())
        self.assertEqual(3, new_game.current_player.minions[2].calculate_max_health())

        self.assertEqual("Undertaker", game.current_player.minions[1].card.name)
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())

        new_game.current_player.minions[2].silence()

        new_game.play_single_turn()
        new_game.play_single_turn()

        self.assertEqual(1, new_game.current_player.minions[3].calculate_attack())
        self.assertEqual(2, new_game.current_player.minions[3].calculate_max_health())

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual("Undertaker", game.current_player.minions[2].card.name)
        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(3, game.current_player.minions[2].calculate_max_health())

    def test_ZombieChow(self):
        game = generate_game_for([ZombieChow, ZombieChow, ZombieChow, AuchenaiSoulpriest], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)

        game.play_single_turn()

        game = game.copy()

        game.other_player.hero.health = 10
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Zombie Chow", game.current_player.minions[0].card.name)
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(15, game.other_player.hero.health)

    def test_DarkCultist(self):
        game = generate_game_for([StonetuskBoar, DarkCultist], StonetuskBoar, SpellTestingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual("Dark Cultist", game.current_player.minions[0].card.name)
        self.assertEqual("Stonetusk Boar", game.current_player.minions[1].card.name)
        self.assertEqual(1, game.current_player.minions[1].health)
        game = game.copy()
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(4, game.current_player.minions[0].health)

    def test_Feugen(self):
        game = generate_game_for([Stalagg, Feugen], Assassinate, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        # Stalagg should have been played and assassinated, leaving no minions behind

        self.assertEqual(0, len(game.other_player.minions))
        game = game.copy()

        game.play_single_turn()
        game.play_single_turn()

        # Feugen is assassinated, which should summon Thaddius
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Thaddius", game.other_player.minions[0].card.name)

    def test_Stalagg(self):
        game = generate_game_for([Feugen, Stalagg], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 9):
            game.play_single_turn()

        # Feugen should have been played we will silence and kill him, which should still summon Thaddius so long as
        # Stalagg isn't also silenced

        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].silence()
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(0, len(game.current_player.minions))

        game.play_single_turn()
        game.play_single_turn()

        # Stalagg is played,  We will kill him, which should summon Thaddius
        self.assertEqual(1, len(game.current_player.minions))
        game = game.copy()
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual("Thaddius", game.current_player.minions[0].card.name)

    def test_DeathsBite(self):
        game = generate_game_for([IronfurGrizzly, DeathsBite], Deathlord,
                                 PredictableAgentWithoutHeroPower, MinionPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertIsNotNone(game.current_player.hero.weapon)
        self.assertEqual(1, game.other_player.minions[0].health)

        game = game.copy()

        game.play_single_turn()
        game.play_single_turn()

        # The Death's Bite attacks the new Deathlord, triggering the weapon's deathrattle
        # This finishes off the other Deathlord and the first friendly Grizzly
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(3, game.other_player.minions[0].health)
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[1].health)

    def test_EchoingOoze(self):
        new_game = None

        class OozeAgent(SpellTestingAgent):
            def __init__(self):
                super().__init__()
                self.turn = 0

            def do_turn(self, player):
                nonlocal new_game
                self.turn += 1
                if self.turn == 2:
                    super().do_turn(player)
                    new_game = player.game.copy()

        game = generate_game_for(EchoingOoze, StoneskinGargoyle, OozeAgent, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        # new_game is still in the middle of a turn, as it was copied in the middle of a turn.  We have to
        # manually end it.
        new_game._end_turn()
        self.assertEqual(2, len(new_game.current_player.minions))
        self.assertEqual(1, new_game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, new_game.current_player.minions[0].calculate_max_health())
        self.assertEqual(1, new_game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, new_game.current_player.minions[1].calculate_max_health())

    def test_ShadeOfNaxxramas(self):
        game = generate_game_for(ShadeOfNaxxramas, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(3, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[1].calculate_max_health())

        game = game.copy()
        game.current_player.minions[0].silence()
        game = game.copy()

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())
        self.assertEqual(4, game.current_player.minions[2].calculate_attack())
        self.assertEqual(4, game.current_player.minions[2].calculate_max_health())

    def test_KelThuzad(self):
        game = generate_game_for([StonetuskBoar, IronfurGrizzly, MagmaRager, KelThuzad], [WarGolem, Flamestrike],
                                 MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))

        game = game.copy()

        game.play_single_turn()

        # All but Kel'Thuzad should have died and then come back to life

        self.assertEqual(4, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].health)

    def test_KelThuzad_with_silence(self):
        game = generate_game_for([StonetuskBoar, IronfurGrizzly, MagmaRager, KelThuzad], [WarGolem, Flamestrike],
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        game = game.copy()
        game.current_player.minions[0].silence()
        game = game.copy()

        game.play_single_turn()

        # The minions should not be brought back

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].health)

    def test_KelThuzad_on_friendly_turn(self):
        game = generate_game_for([StonetuskBoar, IronfurGrizzly, MagmaRager, KelThuzad, Hellfire], StonetuskBoar,
                                 MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 16):
            game.play_single_turn()

        self.assertEqual(4, len(game.other_player.minions))

        game = game.copy()

        game.play_single_turn()

        # All but Kel'Thuzad should have died and then come back to life, but not the Boars

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(0, len(game.other_player.minions))

    def test_Preparation(self):
        new_game = None

        class PrepAgent(PredictableBot):
            def __init__(self):
                super().__init__()
                self.turn = 0

            def do_turn(self, player):
                nonlocal new_game
                done_something = True
                player.game.play_card(player.hand[0])
                new_game = player.game.copy()
                while done_something:
                    done_something = False
                    for card in copy.copy(new_game.current_player.hand):
                        if card.can_use(new_game.current_player, new_game):
                            new_game.play_card(card)
                            done_something = True

        game = generate_game_for([Preparation, BloodfenRaptor, Headcrack], StoneskinGargoyle, PrepAgent, DoNothingBot)

        # Preparation should be played. Bloodfen shouldn't be played, since that isn't a spell, but Headcrack should.
        game.play_single_turn()
        self.assertEqual(28, new_game.players[1].hero.health)
        self.assertEqual(0, len(new_game.players[0].minions))

    def test_Conceal(self):
        new_game = None

        class ConcealAgent(SpellTestingAgent):
            def __init__(self):
                super().__init__()
                self.turn = 0

            def do_turn(self, player):
                nonlocal new_game
                self.turn += 1
                super().do_turn(player)
                if self.turn == 2:
                    new_game = player.game.copy()

        game = generate_game_for([StonetuskBoar, Conceal, MogushanWarden], StonetuskBoar, ConcealAgent, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        # Stonetusk and Conceal should have been played
        self.assertEqual(1, len(new_game.players[0].minions))
        self.assertTrue(new_game.players[0].minions[0].stealth)

        new_game.play_single_turn()
        # Conceal should fade off
        new_game.play_single_turn()
        self.assertEqual(1, len(new_game.players[0].minions))
        self.assertFalse(new_game.players[0].minions[0].stealth)

    def test_Headcrack(self):
        new_game = None

        class HCAgent(SpellTestingAgent):
            def __init__(self):
                super().__init__()
                self.turn = 0

            def do_turn(self, player):
                nonlocal new_game
                self.turn += 1
                super().do_turn(player)
                if self.turn == 6:
                    new_game = player.game.copy()
        game = generate_game_for(Headcrack, StonetuskBoar, HCAgent, DoNothingBot)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(5, len(game.players[0].hand))

        # Headcrack should be played, without combo
        game.play_single_turn()
        self.assertEqual(28, game.players[1].hero.health)
        self.assertEqual(5, len(game.players[0].hand))

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(24, game.players[1].hero.health)
        self.assertEqual(5, len(game.players[0].hand))

        # Headcrack should be played, with combo
        game.play_single_turn()
        new_game._end_turn()
        self.assertEqual(20, new_game.players[1].hero.health)
        self.assertEqual(5, len(new_game.players[0].hand))
        self.assertEqual("Headcrack", new_game.players[0].hand[0].name)

    def test_QuestingAdventurer(self):
        game = generate_game_for(QuestingAdventurer, StonetuskBoar, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        game = game.copy()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)
        game.players[0].minions[0].silence()
        game = game.copy()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertEqual(4, game.players[0].minions[2].calculate_attack())
        self.assertEqual(4, game.players[0].minions[2].health)

    def test_FreezingTrap(self):
        game = generate_game_for(FreezingTrap, BluegillWarrior, SpellTestingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 4):
            game.play_single_turn()
        game = game.copy()
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(7, len(game.players[1].hand))
        self.assertEqual(4, game.players[1].hand[6].mana_cost(game.players[1]))
        self.assertEqual(0, len(game.players[0].secrets))
        self.assertEqual(30, game.players[0].hero.health)
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].hand))
        game.play_single_turn()
        game = game.copy()
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(8, len(game.players[1].hand))
        self.assertEqual(4, game.players[1].hand[5].mana_cost(game.players[1]))
        self.assertEqual(4, game.players[1].hand[7].mana_cost(game.players[1]))

    def test_Shadowstep(self):
        game = generate_game_for([StonetuskBoar, Shadowstep], StonetuskBoar, PredictableAgentWithoutHeroPower,
                                 DoNothingBot)

        # The Boar should be played, Shadowstep will follow targeting the Boar
        game.play_single_turn()
        game = game.copy()
        self.assertEqual(3, len(game.players[0].hand))
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(0, game.players[0].hand[2].mana_cost(game.players[0]))

    def test_UnboundElemental(self):
        game = generate_game_for([UnboundElemental, DustDevil, DustDevil], StonetuskBoar, MinionPlayingAgent,
                                 DoNothingBot)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Unbound Elemental", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].calculate_max_health())

        game = game.copy()

        # One Dust Devil should be played, giving the Unbound Elemental +1/+1
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[-1].calculate_attack())
        self.assertEqual(5, game.players[0].minions[-1].calculate_max_health())
        # Test the silence
        game = game.copy()
        game.players[0].minions[-1].silence()
        self.assertEqual(2, game.players[0].minions[-1].calculate_attack())
        self.assertEqual(4, game.players[0].minions[-1].calculate_max_health())
        # Another Dust Devil, nothing should happen because of silence
        game.play_single_turn()
        game.play_single_turn()
        game = game.copy()
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[-1].calculate_attack())
        self.assertEqual(4, game.players[0].minions[-1].calculate_max_health())

    def test_PowerOverwhelming(self):
        game = generate_game_for(PowerOverwhelming, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        imp = FlameImp()
        imp.summon(game.players[0], game, 0)
        self.assertEqual(1, len(game.players[0].minions))

        def verify_poweroverwhelming():
            nonlocal game
            game = game.copy()
            self.assertEqual(7, game.players[0].minions[0].calculate_attack())
            self.assertEqual(6, game.players[0].minions[0].health)

        game.players[0].minions[0].bind("health_changed", verify_poweroverwhelming)
        game.play_single_turn()
        game._end_turn()
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[0].hand))

    def test_Corruption(self):
        game = generate_game_for(Corruption, StonetuskBoar, EnemyMinionSpellTestingAgent, DoNothingBot)
        imp = FlameImp()
        imp.summon(game.players[1], game, 0)
        self.assertEqual(1, len(game.players[1].minions))

        game.play_single_turn()
        # Casts Corruption on enemy Imp
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(3, len(game.players[0].hand))

        game.play_single_turn()
        # Enemy minion still alive until start of my turn
        self.assertEqual(1, len(game.players[1].minions))
        game = game.copy()

        game.play_single_turn()
        # Corruption resolves at start of my turn, no targets to use remaining cards on
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))
