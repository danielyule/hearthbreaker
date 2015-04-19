import copy
import random
import unittest

from hearthbreaker.agents.basic_agents import DoNothingAgent, PredictableAgent
from hearthbreaker.cards.base import MinionCard
from hearthbreaker.constants import MINION_TYPE, CARD_RARITY
from hearthbreaker.tags.status import ChangeAttack
from tests.agents.testing_agents import CardTestingAgent, OneCardPlayingAgent, PlayAndAttackAgent, \
    EnemyMinionSpellTestingAgent, HeroPowerAndCardPlayingAgent
from tests.card_tests.card_tests import TestUtilities
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *


def create_enemy_copying_agent(turn_to_play=1):
    class EnemyCopyingAgent(CardTestingAgent):
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
    class FriendlyCopyingAgent(CardTestingAgent):
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
        game = generate_game_for(StonetuskBoar, StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)

        new_game = game.copy()

        self.assertEqual(0, new_game.current_player.mana)

        for turn in range(0, 10):
            new_game.play_single_turn()

        self.assertEqual(5, len(new_game.current_player.minions))

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))

    def test_hero_copying(self):
        test_env = self
        game = None

        class PowerAndCopyAgent(DoNothingAgent):
            def do_turn(self, player):
                nonlocal game
                if player.hero.power.can_use():
                    player.hero.power.use()
                    test_env.assertEqual(1, game.current_player.hero.calculate_attack())
                    game = game.copy()
                    test_env.assertEqual(1, game.current_player.hero.calculate_attack())

        game = generate_game_for(HealingTouch, StonetuskBoar, PowerAndCopyAgent, DoNothingAgent)

        for turn in range(0, 5):
            game.play_single_turn()


class TestMinionCopying(unittest.TestCase, TestUtilities):
    def setUp(self):
        random.seed(1857)

    def test_StormwindChampion(self):
        game = generate_game_for(StormwindChampion, [Abomination, BoulderfistOgre, FacelessManipulator],
                                 OneCardPlayingAgent, create_enemy_copying_agent(5))
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
                                 create_friendly_copying_agent(10), DoNothingAgent)
        for turn in range(0, 18):
            game.play_single_turn()

        def check_minions():
            self.assertEqual(4, len(game.current_player.minions))

            for minion in game.current_player.minions:
                self.assertEqual(2, minion.calculate_attack())
                self.assertEqual(2, minion.health)
                self.assertEqual(2, minion.calculate_max_health())
                self.assertTrue(minion.charge())
                self.assertEqual("Treant", minion.card.name)

        game.other_player.bind_once("turn_ended", check_minions)

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))

    def test_Abomination(self):
        game = generate_game_for(Abomination, FacelessManipulator,
                                 OneCardPlayingAgent, create_enemy_copying_agent(5))

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
                                 CardTestingAgent, create_enemy_copying_agent(6))

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
        game = generate_game_for(NerubianEgg, FacelessManipulator, OneCardPlayingAgent, create_enemy_copying_agent(5))

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
                                 OneCardPlayingAgent, create_enemy_copying_agent())

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
                                 PlayAndAttackAgent, create_enemy_copying_agent(6))
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
            self.assertEqual(5, game.current_player.minions[1].calculate_attack())
            self.assertTrue(game.current_player.minions[1].immune)
            self.assertEqual(5, game.current_player.minions[0].calculate_attack())
            self.assertTrue(game.current_player.minions[0].immune)

        game = generate_game_for([StampedingKodo, BestialWrath, FacelessManipulator], StonetuskBoar,
                                 create_friendly_copying_agent(5), DoNothingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        # we need to check that there are two immune kodos at the end of the turn
        game.other_player.bind("turn_ended", verify_bwrath)

        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))

    def test_HarvestGolem(self):
        game = generate_game_for(FacelessManipulator, HarvestGolem, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(1, len(game.current_player.minions))

    def test_HauntedCreeper(self):
        game = generate_game_for(FacelessManipulator, HauntedCreeper, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(2, len(game.current_player.minions))

    def test_TheBeast(self):
        game = generate_game_for(TheBeast, FacelessManipulator, OneCardPlayingAgent, create_enemy_copying_agent(6))

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
                                 OneCardPlayingAgent, create_enemy_copying_agent())

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
                                 OneCardPlayingAgent, create_enemy_copying_agent())

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].charge())
        self.assertTrue(game.current_player.minions[1].charge())

    def test_StarvingBuzzard(self):
        game = generate_game_for(StarvingBuzzard, [StonetuskBoar, FacelessManipulator, Maexxna, CoreHound],
                                 OneCardPlayingAgent, create_enemy_copying_agent())

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
                                 OneCardPlayingAgent, create_enemy_copying_agent(6))
        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual("Hyena", game.players[1].minions[0].card.name)
        self.assertEqual("Hyena", game.players[1].minions[1].card.name)

    def test_TimberWolf(self):
        game = generate_game_for(TimberWolf,
                                 [StonetuskBoar, BloodfenRaptor, IronfurGrizzly,
                                  OasisSnapjaw, FacelessManipulator, Maexxna],
                                 OneCardPlayingAgent, create_enemy_copying_agent())

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
                                 OneCardPlayingAgent, create_enemy_copying_agent(5))

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
                                 OneCardPlayingAgent, create_enemy_copying_agent(1))

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(8, len(game.other_player.hand))
        self.assertEqual(MINION_TYPE.BEAST, game.other_player.hand[7].minion_type)

    def test_Duplicate(self):
        game = generate_game_for([BloodfenRaptor, Duplicate], ShadowBolt, OneCardPlayingAgent, CardTestingAgent)

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
        game = generate_game_for(Frostbolt, StoneskinGargoyle, OneCardPlayingAgent, OneCardPlayingAgent)

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
        game = generate_game_for([SludgeBelcher, Fireball], FacelessManipulator,
                                 OneCardPlayingAgent, OneCardPlayingAgent)

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
        game = generate_game_for(FaerieDragon, Frostbolt, OneCardPlayingAgent, CardTestingAgent)
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
                                 OneCardPlayingAgent, DoNothingAgent)

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
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        game.current_player.minions[1].die(None)
        game.check_delayed()

        self.assertEqual(3, len(game.current_player.minions))

    def test_DancingSwords(self):
        game = generate_game_for(DancingSwords, ShadowBolt, OneCardPlayingAgent, CardTestingAgent)

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
                                 OneCardPlayingAgent, DoNothingAgent)

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

        self.assertTrue(isinstance(game.other_player.minions[1].card, MinionCard))

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
                                 OneCardPlayingAgent, OneCardPlayingAgent)

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
                                 CardTestingAgent, OneCardPlayingAgent)

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
                                  Frostbolt], StonetuskBoar, CardTestingAgent, DoNothingAgent)

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
        self.assertEqual(1, game.current_player.hand[1].mana_cost())
        self.assertEqual(1, game.current_player.hand[2].mana_cost())

        game.play_single_turn()
        game.play_single_turn()

        # Both Sorcer's Apprentices are killed by friendly Frostbolts.
        self.assertEqual(0, len(game.current_player.minions))

        # Make sure that the cards in hand are no longer reduced
        self.assertEqual(2, game.current_player.hand[0].mana_cost())

    def test_Loatheb(self):
        game = generate_game_for(Loatheb, [Assassinate, BoulderfistOgre], OneCardPlayingAgent, CardTestingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        game = game.copy()

        self.assertEqual(10, game.other_player.hand[0].mana_cost())
        self.assertEqual(6, game.other_player.hand[1].mana_cost())

        game.play_single_turn()

        self.assertEqual(5, game.current_player.hand[0].mana_cost())
        self.assertEqual(6, game.current_player.hand[1].mana_cost())

    def test_KirinTorMage(self):
        game = generate_game_for([KirinTorMage, BoulderfistOgre, Spellbender],
                                 StonetuskBoar, CardTestingAgent, DoNothingAgent)
        new_game = None
        for turn in range(0, 4):
            game.play_single_turn()

        def check_secret_cost():
            nonlocal new_game
            new_game = game.copy()
            self.assertEqual(1, len(new_game.current_player.minions))
            self.assertEqual("Kirin Tor Mage", new_game.current_player.minions[0].card.name)
            self.assertEqual(0, new_game.current_player.hand[1].mana_cost())
            self.assertEqual("Spellbender", new_game.current_player.hand[1].name)

        game.other_player.bind_once("turn_ended", check_secret_cost)
        game.play_single_turn()
        new_game._end_turn()
        self.assertEqual(3, new_game.current_player.hand[1].mana_cost())
        self.assertEqual("Spellbender", new_game.current_player.hand[1].name)

    def test_WaterElemental(self):
        game = generate_game_for(WaterElemental, StonetuskBoar, PredictableAgent, DoNothingAgent)

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(25, game.other_player.hero.health)
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
        self.assertTrue(game.other_player.hero.frozen)

        # Now make sure that attacking the Water Elemental directly will freeze a character
        random.seed(1857)
        game = generate_game_for(WaterElemental, IronbarkProtector, OneCardPlayingAgent, PredictableAgent)
        for turn in range(0, 7):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(5, game.other_player.minions[0].health)
        # The player won't have taken damage because of armor, but should be frozen anyway
        self.assertEqual(30, game.current_player.hero.health)
        self.assertTrue(game.current_player.hero.frozen)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(30, game.current_player.hero.health)

    def test_BlessingOfWisdom(self):
        game = generate_game_for([OasisSnapjaw, BlessingOfWisdom, CoreHound], [FacelessManipulator, CoreHound],
                                 OneCardPlayingAgent, PlayAndAttackAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        # The blessing of wisdom should be attached to the Oasis Snapjaw, which the Faceless has copied.
        # The copied snapjaw should still draw cards for the first player

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Oasis Snapjaw", game.current_player.minions[0].card.name)

        self.assertEqual(8, len(game.other_player.hand))

    def test_TirionFordring(self):
        game = generate_game_for(TirionFordring, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

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
                                 OneCardPlayingAgent, OneCardPlayingAgent)

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
        self.assertEqual(2, new_game.current_player.minions[2].calculate_max_health())

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
        self.assertEqual(2, game.current_player.minions[2].calculate_max_health())

    def test_ZombieChow(self):
        game = generate_game_for([ZombieChow, ZombieChow, ZombieChow, AuchenaiSoulpriest], StonetuskBoar,
                                 OneCardPlayingAgent, DoNothingAgent)

        game.play_single_turn()

        game = game.copy()

        game.other_player.hero.health = 10
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Zombie Chow", game.current_player.minions[0].card.name)
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(15, game.other_player.hero.health)

    def test_DarkCultist(self):
        game = generate_game_for([StonetuskBoar, DarkCultist], StonetuskBoar, CardTestingAgent, DoNothingAgent)

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
        game = generate_game_for([Stalagg, Feugen], Assassinate, OneCardPlayingAgent, CardTestingAgent)

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

    def test_Fuegen_no_Stalagg(self):
        game = generate_game_for(Feugen, Assassinate, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        # Feugen should have been played and assassinated, leaving no minions behind

        self.assertEqual(0, len(game.other_player.minions))

        game.play_single_turn()
        game = game.copy()
        game.play_single_turn()

        # Feugen is assassinated again, which should not summon Thaddius
        self.assertEqual(0, len(game.other_player.minions))

    def test_Stalagg(self):
        game = generate_game_for([Feugen, Stalagg], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

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
                                 PlayAndAttackAgent, OneCardPlayingAgent)

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

        class OozeAgent(CardTestingAgent):
            def __init__(self):
                super().__init__()
                self.turn = 0

            def do_turn(self, player):
                nonlocal new_game
                self.turn += 1
                if self.turn == 2:
                    super().do_turn(player)
                    new_game = player.game.copy()

        game = generate_game_for(EchoingOoze, StoneskinGargoyle, OozeAgent, DoNothingAgent)

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
        game = generate_game_for(ShadeOfNaxxramas, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

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
                                 OneCardPlayingAgent, CardTestingAgent)

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
                                 OneCardPlayingAgent, OneCardPlayingAgent)

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
                                 OneCardPlayingAgent, DoNothingAgent)

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

        class PrepAgent(PredictableAgent):
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

        game = generate_game_for([Preparation, BloodfenRaptor, Headcrack], StoneskinGargoyle, PrepAgent, DoNothingAgent)

        # Preparation should be played. Bloodfen shouldn't be played, since that isn't a spell, but Headcrack should.
        game.play_single_turn()
        self.assertEqual(28, new_game.players[1].hero.health)
        self.assertEqual(0, len(new_game.players[0].minions))

    def test_Conceal(self):
        new_game = None

        class ConcealAgent(CardTestingAgent):
            def __init__(self):
                super().__init__()
                self.turn = 0

            def do_turn(self, player):
                nonlocal new_game
                self.turn += 1
                super().do_turn(player)
                if self.turn == 2:
                    new_game = player.game.copy()

        game = generate_game_for([StonetuskBoar, Conceal, MogushanWarden], StonetuskBoar, ConcealAgent, DoNothingAgent)

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

        class HCAgent(CardTestingAgent):
            def __init__(self):
                super().__init__()
                self.turn = 0

            def do_turn(self, player):
                nonlocal new_game
                self.turn += 1
                super().do_turn(player)
                if self.turn == 6:
                    new_game = player.game.copy()
        game = generate_game_for(Headcrack, StonetuskBoar, HCAgent, DoNothingAgent)

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
        game = generate_game_for(QuestingAdventurer, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
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
        game = generate_game_for(FreezingTrap, BluegillWarrior, CardTestingAgent, PlayAndAttackAgent)

        for turn in range(0, 4):
            game.play_single_turn()
        game = game.copy()
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(7, len(game.players[1].hand))
        self.assertEqual(4, game.players[1].hand[6].mana_cost())
        self.assertEqual(0, len(game.players[0].secrets))
        self.assertEqual(30, game.players[0].hero.health)
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].hand))
        game.play_single_turn()
        game = game.copy()
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(8, len(game.players[1].hand))
        self.assertEqual(4, game.players[1].hand[5].mana_cost())
        self.assertEqual(4, game.players[1].hand[7].mana_cost())

    def test_Shadowstep(self):
        game = generate_game_for([StonetuskBoar, Shadowstep], StonetuskBoar, PlayAndAttackAgent,
                                 DoNothingAgent)

        # The Boar should be played, Shadowstep will follow targeting the Boar
        game.play_single_turn()
        game = game.copy()
        self.assertEqual(3, len(game.players[0].hand))
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(0, game.players[0].hand[2].mana_cost())

    def test_UnboundElemental(self):
        game = generate_game_for([UnboundElemental, DustDevil, DustDevil], StonetuskBoar, OneCardPlayingAgent,
                                 DoNothingAgent)

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
        game = generate_game_for(PowerOverwhelming, StonetuskBoar, CardTestingAgent, DoNothingAgent)
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
        game = generate_game_for(Corruption, StonetuskBoar, EnemyMinionSpellTestingAgent, DoNothingAgent)
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

    def test_ManaAddict(self):
        game = generate_game_for([ManaAddict, ArcaneIntellect], StonetuskBoar, CardTestingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        def check_attack(m):
            self.assertEqual(3, game.players[0].minions[0].calculate_attack())

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        game = game.copy()

        game.players[0].bind("spell_cast", check_attack)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, len(game.players[0].hand))

    def test_VentureCoMercenary(self):
        game = generate_game_for([VentureCoMercenary, Silence], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 10):
            game.play_single_turn()
        game = game.copy()
        self.assertEqual(0, game.players[0].hand[0].mana_cost())
        self.assertEqual(8, game.players[0].hand[1].mana_cost())

        game.play_single_turn()

        self.assertEqual(5, game.players[0].hand[0].mana_cost())
        self.assertEqual(0, game.players[0].hand[1].mana_cost())

    def test_BaronGeddon(self):
        game = generate_game_for(BaronGeddon, MassDispel, OneCardPlayingAgent, CardTestingAgent)
        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(28, game.players[0].hero.health)
        self.assertEqual(28, game.players[1].hero.health)
        self.assertEqual(5, game.players[0].minions[0].health)

        game = game.copy()

        game.play_single_turn()  # Silences the Baron Geddon on the field
        game.play_single_turn()  # Only the new Baron Geddon triggers

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(26, game.players[0].hero.health)
        self.assertEqual(26, game.players[1].hero.health)
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[1].health)

    def test_RagnarosTheFirelord(self):
        game = generate_game_for(RagnarosTheFirelord, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)
        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(22, game.players[1].hero.health)
        game = game.copy()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(6, game.players[1].hero.health)
        # 3 rag balls to the face, but no attacks

    def test_AncientWatcher(self):
        game = generate_game_for(AncientWatcher, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(30, game.players[1].hero.health)

    def test_Demolisher(self):
        game = generate_game_for(Demolisher, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(4, game.players[0].minions[1].health)
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(28, game.players[1].hero.health)

    def test_Doomsayer(self):
        game = generate_game_for(Doomsayer, StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))

        game = game.copy()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

    def test_Gruul(self):
        game = generate_game_for(Gruul, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 16):
            game.play_single_turn()

        game = game.copy()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(9, game.players[0].minions[0].calculate_attack())
        self.assertEqual(9, game.players[0].minions[0].health)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(8, game.players[0].minions[0].calculate_attack())
        self.assertEqual(8, game.players[0].minions[0].health)
        self.assertEqual(10, game.players[0].minions[1].calculate_attack())
        self.assertEqual(10, game.players[0].minions[1].health)

    def test_Hogger(self):
        game = generate_game_for(Hogger, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].health)
        game = game.copy()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertEqual(4, game.players[0].minions[2].calculate_attack())
        self.assertEqual(4, game.players[0].minions[2].health)
        self.assertEqual(2, game.players[0].minions[3].calculate_attack())
        self.assertEqual(2, game.players[0].minions[3].health)
        self.assertEqual(2, game.players[0].minions[4].calculate_attack())
        self.assertEqual(2, game.players[0].minions[4].health)

    def test_ImpMaster(self):
        game = generate_game_for([ImpMaster, MindControl], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)
        game = game.copy()

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(5, len(game.players[0].minions))
        for index in range(0, 5):
            self.assertEqual("Imp", game.players[0].minions[index].card.name)

    def test_MasterSwordsmith(self):
        game = generate_game_for(MasterSwordsmith, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        game = game.copy()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())

    def test_Armorsmith(self):
        game = generate_game_for(Armorsmith, StonetuskBoar, OneCardPlayingAgent, PlayAndAttackAgent)

        # Armorsmith should be played
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual("Armorsmith", game.players[0].minions[0].card.name)
        self.assertEqual(0, game.players[0].hero.armor)

        game = game.copy()

        # Three Stonetusks should attack, generating one armor each
        game.play_single_turn()
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].hero.armor)

    def test_GrommashHellscream(self):
        game = generate_game_for(GrommashHellscream, ExplosiveTrap, PlayAndAttackAgent, CardTestingAgent)

        for turn in range(0, 14):
            game.play_single_turn()

        # Hellscream should be played, attacking (charge) and getting 2 damage by trap that will trigger enrage,
        # dealing 10 damage as result
        game = game.copy()
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(10, game.players[0].minions[0].calculate_attack())
        self.assertEqual(7, game.players[0].minions[0].health)
        self.assertEqual(20, game.players[1].hero.health)

        game.players[0].minions[0].heal(2, None)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        game.players[0].minions[0].damage(2, None)
        self.assertEqual(10, game.players[0].minions[0].calculate_attack())
        game = game.copy()
        game.players[0].minions[0].silence()
        game = game.copy()
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        game.players[0].minions[0].heal(2, None)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        game.players[0].minions[0].damage(2, None)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())

    def test_WarsongCommander(self):
        game = generate_game_for(WarsongCommander, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)

        # Super special test cases - http://www.hearthhead.com/card=1009/warsong-commander#comments:id=1935295
        game.players[0].mana = 100

        # Play the Warsong Commander
        commander = WarsongCommander()
        commander.player = game.players[0]
        commander.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[0].charge())  # Should not give charge to itself
        game = game.copy()
        # Test so that enrage doesn't remove the charge
        worgen = RagingWorgen()
        worgen.player = game.players[0]
        worgen.use(game.players[0], game)
        game.players[0].minions[0].damage(1, None)  # Trigger enrage, charge should still be active
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertTrue(game.players[0].minions[0].charge())

        # Remove the Warsong Commander
        game.players[0].minions[-1].die(None)
        game.check_delayed()
        game = game.copy()
        # The previous charged minions should still have charge
        self.assertTrue(game.players[0].minions[0].charge())
        self.assertTrue(game.players[0].minions[-1].charge())

        # Test so that a minion played before Warsong doesn't get charge
        shield = Shieldbearer()
        shield.summon(game.players[0], game, 0)
        self.assertFalse(game.players[0].minions[0].charge())
        commander.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[1].charge())
        # Remove the Warsong again
        game.players[0].minions[0].die(None)
        game.players[0].minions[0].activate_delayed()
        # Buff a minion to above 3
        game.players[0].minions[0].change_attack(5)
        # Play Warsong, the buffed minion should not get charge
        game = game.copy()
        commander.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[1].charge())

        # Auras!
        stormwind = StormwindChampion()
        stormwind.player = game.players[0]
        stormwind.use(game.players[0], game)
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())
        self.assertEqual(4, game.players[0].minions[1].health)
        # Kill the worgen
        game.players[0].minions[-1].die(None)
        game.players[0].minions[-1].activate_delayed()
        game = game.copy()
        # And play it again. It should get the aura FIRST, making it a 4/4 minion, and thus DOES NOT gain charge!
        worgen.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[0].charge())

    def test_CommandingShout(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, StonetuskBoar, BoulderfistOgre,
                                  CommandingShout, FacelessManipulator], RecklessRocketeer,
                                 PlayAndAttackAgent, OneCardPlayingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Reckless Rocketeer", game.current_player.minions[0].card.name)

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].health)
        self.assertEqual("Reckless Rocketeer", game.current_player.minions[0].card.name)

    def test_Gorehowl(self):
        game = generate_game_for(Gorehowl, [BoulderfistOgre, Deathwing],
                                 PlayAndAttackAgent, CardTestingAgent)

        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(1, game.current_player.hero.weapon.durability)

        game = game.copy()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(23, game.other_player.hero.health)
        self.assertIsNone(game.current_player.hero.weapon)

    def test_NerubarWeblord(self):
        game = generate_game_for([NerubarWeblord, EarthenRingFarseer], [NoviceEngineer, IronfurGrizzly],
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 3):
            game.play_single_turn()
        game = game.copy()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.hand[0].mana_cost())
        self.assertEqual(4, game.other_player.hand[0].mana_cost())
        self.assertEqual(3, game.other_player.hand[1].mana_cost())
        game.current_player.minions[0].silence()
        game = game.copy()
        self.assertEqual(3, game.current_player.hand[0].mana_cost())
        self.assertEqual(2, game.other_player.hand[0].mana_cost())
        self.assertEqual(3, game.other_player.hand[1].mana_cost())

    def test_Lightwell(self):
        game = generate_game_for(Lightwell, StonetuskBoar, OneCardPlayingAgent, PredictableAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(28, game.players[0].hero.health)
        self.assertEqual(2, game.players[0].minions[0].health)

        # Lightwell is out, it should heal at the beginning of this turn
        game = game.copy()
        game.play_single_turn()
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertEqual(30, game.players[0].hero.health)

    def test_Lightwarden(self):
        game = generate_game_for([Lightwarden, MindControl],
                                 [StonetuskBoar, BoulderfistOgre, BoulderfistOgre, BoulderfistOgre, BoulderfistOgre],
                                 PredictableAgent, PredictableAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)

        game = game.copy()

        game.play_single_turn()  # Heal Lightwarden

        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

        game.players[0].hero.health = 28
        game.players[0].hero.heal(2, None)
        game = game.copy()
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())

    def test_Lightspawn(self):
        game = generate_game_for(Lightspawn, StonetuskBoar, OneCardPlayingAgent, PredictableAgent)

        # Lightspawn should be played
        for turn in range(0, 7):
            game.play_single_turn()

        game = game.copy()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(5, game.players[0].minions[0].health)

        # Lightspawn should have taken some hits
        game.play_single_turn()
        game = game.copy()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)

        game.players[0].minions[0].heal(2, None)
        game = game.copy()
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

        game.players[0].minions[0].increase_health(4)
        game = game.copy()
        self.assertEqual(7, game.players[0].minions[0].calculate_attack())
        self.assertEqual(7, game.players[0].minions[0].health)

        game = game.copy()
        game.players[0].minions[0].decrease_health(2)  # max_health goes from 9 to 7
        self.assertEqual(7, game.players[0].minions[0].calculate_attack())
        self.assertEqual(7, game.players[0].minions[0].health)

    def test_NorthshireCleric(self):
        game = generate_game_for(NorthshireCleric, StonetuskBoar, PredictableAgent, PredictableAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(26, game.players[0].deck.left)

        game = game.copy()
        # Northshire is damaged, should get a heal and a card should be drawn
        game.play_single_turn()
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(24, game.players[0].deck.left)

        game.players[0].hero.health = 28
        game.players[0].hero.heal(2, None)
        self.assertEqual(24, game.players[0].deck.left)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game = game.copy()
        # Silence one Northshire, the other one should still work
        game.players[0].minions[0].silence()
        game = game.copy()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(22, game.players[0].deck.left)
        game.play_single_turn()
        self.assertEqual(20, game.players[0].deck.left)

    def test_ShadowMadness(self):
        game = generate_game_for([Deathwing],
                                 [Humility, ShadowMadness, FacelessManipulator], OneCardPlayingAgent,
                                 CardTestingAgent)

        for turn in range(0, 20):
            game.play_single_turn()

        # Deathwing should have humility played on it, which should enable shadow madness to be played.
        # Then the faceless should copy it, so there are two deathwings with one attack.  At the end of the turn
        # both should return to the other played.

        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual("Deathwing", game.other_player.minions[0].card.name)
        self.assertEqual("Deathwing", game.other_player.minions[1].card.name)
        self.assertEqual(1, game.other_player.minions[0].calculate_attack())
        self.assertEqual(1, game.other_player.minions[1].calculate_attack())

    def test_ProphetVelen(self):
        game = generate_game_for([ProphetVelen, ProphetVelen, MindBlast], StonetuskBoar, OneCardPlayingAgent,
                                 DoNothingAgent)

        # Prophet Velen should be played
        for turn in range(0, 13):
            game.play_single_turn()
        game = game.copy()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Prophet Velen", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].spell_multiplier)
        self.assertEqual(2, game.players[0].heal_multiplier)

        game.play_single_turn()
        # Another Prophet Velen should be played
        game.play_single_turn()
        game = game.copy()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].spell_multiplier)
        self.assertEqual(4, game.players[0].heal_multiplier)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        # Mind Blast should be played, dealing 5 * 4 = 20 damage
        game.play_single_turn()

        self.assertEqual(10, game.players[1].hero.health)
        velen = game.players[0].minions[0]
        velen.die(None)
        velen.activate_delayed()
        game = game.copy()
        self.assertEqual(2, game.players[0].spell_multiplier)
        self.assertEqual(2, game.players[0].heal_multiplier)
        game.players[0].minions[0].silence()
        game = game.copy()
        self.assertEqual(1, game.players[0].spell_multiplier)
        self.assertEqual(1, game.players[0].heal_multiplier)

    def test_SpitefulSmith(self):
        game = generate_game_for(LightsJustice, [MortalCoil, AcidicSwampOoze, CircleOfHealing],
                                 PlayAndAttackAgent, OneCardPlayingAgent)
        smith = SpitefulSmith()
        smith.summon(game.players[0], game, 0)
        for turn in range(0, 2):
            game.play_single_turn()

        game = game.copy()

        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(29, game.players[1].hero.health)  # No enrage, only LJ

        game.play_single_turn()
        self.assertEqual(3, game.players[0].hero.calculate_attack())
        self.assertEqual(22, game.players[1].hero.health)  # Enrage LJ for 3 + Smith for 4

        game = game.copy()

        game.play_single_turn()  # Ooze

        self.assertEqual(1, len(game.players[1].minions))

        game.play_single_turn()  # New weapon

        game = game.copy()

        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(27, game.players[0].hero.health)  # Enrage LJ for 3 to kill Ooze
        self.assertEqual(18, game.players[1].hero.health)  # Smith to face for 4

        game.play_single_turn()  # Circle of Healing
        game = game.copy()
        game.play_single_turn()  # Unenraged LJ for 1 + Smith for 4

        self.assertEqual(13, game.players[1].hero.health)

    def test_CultMaster(self):
        game = generate_game_for([StonetuskBoar, FacelessManipulator], CultMaster,
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))

        self.assertEqual(6, len(game.other_player.hand))
        self.assertEqual(8, len(game.current_player.hand))

        # The faceless copies the Cult master, and then the stonetusk boar attacks and dies, resulting in a card draw
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))

        self.assertEqual(7, len(game.current_player.hand))
        self.assertEqual(8, len(game.other_player.hand))

    def test_AcolyteOfPain(self):
        game = generate_game_for(AcolyteOfPain, [MortalCoil, ShadowWordPain], OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[0].hand))

        game = game.copy()

        game.play_single_turn()  # Mortal Coils the Acolyte

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[0].hand))

        game.play_single_turn()  # Plays 2nd Acolyte
        game = game.copy()
        game.play_single_turn()  # Pains 1 Acolyte, no draw

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[0].hand))

    def test_MurlocTidecaller(self):
        game = generate_game_for(MurlocTidecaller, FacelessManipulator, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[2].calculate_attack())
        self.assertEqual(4, game.current_player.minions[3].calculate_attack())
        self.assertEqual(5, game.current_player.minions[4].calculate_attack())

        game.play_single_turn()

        self.assertEqual(2, game.other_player.minions[0].calculate_attack())
        self.assertEqual(3, game.other_player.minions[1].calculate_attack())
        self.assertEqual(4, game.other_player.minions[2].calculate_attack())
        self.assertEqual(5, game.other_player.minions[3].calculate_attack())
        self.assertEqual(6, game.other_player.minions[4].calculate_attack())

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())

    def test_VioletTeacher(self):
        game = generate_game_for([VioletTeacher, CircleOfHealing], CircleOfHealing,
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

        game = game.copy()

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

    def test_GadgetzanAuctioneer(self):
        game = generate_game_for([GadgetzanAuctioneer, CircleOfHealing, SinisterStrike], CircleOfHealing,
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(8, len(game.players[0].hand))

        game = game.copy()

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(9, len(game.players[0].hand))

        game.players[0].minions[0].silence()

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(9, len(game.players[0].hand))

    def test_IllidanStormrage(self):
        game = generate_game_for([IllidanStormrage, CircleOfHealing], CircleOfHealing,
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

        game = game.copy()

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

    def test_FlesheatingGhoul(self):
        game = generate_game_for(CircleOfHealing, StonetuskBoar, OneCardPlayingAgent, PlayAndAttackAgent)
        ghoul = FlesheatingGhoul()
        ghoul.summon(game.players[0], game, 0)
        game.play_single_turn()
        game = game.copy()
        game.play_single_turn()

        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

        game.play_single_turn()  # Circle
        game = game.copy()
        game.play_single_turn()  # Two Boars into Ghoul
        game = game.copy()
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(30, game.players[0].hero.health)

    def test_GurubashiBerserker(self):
        game = generate_game_for([GurubashiBerserker, BoulderfistOgre],
                                 MortalCoil, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 9):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()

        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

        game.play_single_turn()
        game = game.copy()
        game.play_single_turn()

        self.assertEqual(5, game.players[0].minions[1].calculate_attack())
        self.assertEqual(6, game.players[0].minions[1].health)

    def test_WildPyromancer(self):
        game = generate_game_for([WildPyromancer, MindBlast, PowerWordShield], Shieldbearer,
                                 CardTestingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].health)

        game = game.copy()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual("Wild Pyromancer", game.players[0].hand[0].name)

        game.play_single_turn()
        game = game.copy()
        game.play_single_turn()

        # The two pyros killed each other with the effect after mind blast
        self.assertEqual(0, len(game.players[0].minions))

    def test_AlarmOBot(self):
        game = generate_game_for(AlarmoBot, [FacelessManipulator,
                                             Pyroblast, Pyroblast, Pyroblast, Pyroblast,
                                             Pyroblast, Pyroblast, Pyroblast, Deathwing],
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(10):
            game.play_single_turn()

        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Alarm-o-Bot", game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(4, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Faceless Manipulator", game.current_player.minions[0].card.name)

    def test_MillhouseManastorm(self):
        game = generate_game_for([MillhouseManastorm, MagmaRager], SiphonSoul, OneCardPlayingAgent, CardTestingAgent)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        game = game.copy()
        game.play_single_turn()
        self.assertEqual(0, len(game.players[0].minions))
        game = game.copy()
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))

    def test_Ysera(self):
        game = generate_game_for(Innervate, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        ysera = Ysera()
        ysera.summon(game.players[0], game, 0)
        game = game.copy()
        for turn in range(0, 2):
            game.play_single_turn()

        def check_nightmare():
            game.play_single_turn()
            game.play_single_turn()
            for minion in game.players[0].minions:
                if minion.card.name == "Ysera":
                    self.assertEqual(9, minion.calculate_attack())
                    self.assertEqual(17, minion.health)
                    break
            ysera.summon(game.players[0], game, 0)  # Backup Ysera strats

        def check_laughing_sister():
            game.play_single_turn()
            game.play_single_turn()
            self.assertEqual("Laughing Sister", game.players[0].minions[0].card.name)
            self.assertFalse(game.players[0].minions[0].spell_targetable())

        def check_dream():
            game.players[0].max_mana = 8
            name = game.players[0].minions[0].card.name
            game.play_single_turn()
            self.assertEqual(name, game.players[0].hand[-2].name)
            game.play_single_turn()

        def check_ysera_awakens():
            health_list = {}
            for player in game.players:
                for minion in player.minions:
                    health_list[minion] = minion.health

                health_list[player.hero] = player.hero.health

            game.play_single_turn()
            game.play_single_turn()

            for player in game.players:
                for minion in player.minions:
                    if minion.card.name == "Ysera":
                        self.assertEqual(health_list[minion], minion.health)
                    else:
                        self.assertEqual(health_list[minion] - 5, minion.health)
                self.assertEqual(health_list[player.hero] - 5, player.hero.health)

        def check_emerald_drake():
            game.play_single_turn()
            game.play_single_turn()
            self.assertEqual("Emerald Drake", game.players[0].minions[0].card.name)

        required = ["Nightmare", "Dream", "Ysera Awakens", "Emerald Drake", "Laughing Sister"]

        while len(required) > 0:
            card_name = game.players[0].hand[0].name
            if card_name in required:
                required.remove(card_name)
                game = game.copy()
                if card_name == "Nightmare":
                    check_nightmare()
                elif card_name == "Dream":
                    check_dream()
                elif card_name == "Ysera Awakens":
                    check_ysera_awakens()
                elif card_name == "Emerald Drake":
                    check_emerald_drake()
                elif card_name == "Laughing Sister":
                    check_laughing_sister()
            else:
                game.players[0].hand.remove(game.players[0].hand[0])
                if len(game.players[0].hand) == 0:
                    game.play_single_turn()
                    game.play_single_turn()

    def test_LorewalkerCho(self):
        game = generate_game_for([FreezingTrap, MagmaRager], SinisterStrike, OneCardPlayingAgent, OneCardPlayingAgent)
        cho = LorewalkerCho()
        cho.summon(game.players[0], game, 0)

        game = game.copy()
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(27, game.players[0].hero.health)
        self.assertEqual(5, len(game.players[0].hand))
        self.assertEqual("Sinister Strike", game.players[0].hand[4].name)

        game.play_single_turn()

        self.assertEqual(6, len(game.players[1].hand))
        self.assertEqual("Freezing Trap", game.players[1].hand[5].name)

        game = game.copy()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(6, len(game.players[1].hand))
        self.assertNotEqual("Magma Rager", game.players[1].hand[5].name)

    def test_OldMurkEye(self):
        game = generate_game_for([OldMurkEye, ArcaneExplosion], BluegillWarrior,
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 6):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())

        game = game.copy()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())

        game = game.copy()
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())

    def test_PilotedShredder(self):
        game = generate_game_for(Assassinate, PilotedShredder, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Piloted Shredder", game.current_player.minions[0].card.name)

        # The assassinate will kill the shredder, and leave the other player with
        game = game.copy()
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].card.mana)

    def test_PilotedSkyGolem(self):
        game = generate_game_for(PilotedSkyGolem, Assassinate, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Piloted Sky Golem", game.current_player.minions[0].card.name)

        game = game.copy()

        # The assassinate will kill the golem, and leave the other player with a 4 mana card
        game.play_single_turn()

        self.assertLessEqual(1, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].card.mana)

    def test_SneedsOldShredder(self):
        game = generate_game_for(SneedsOldShredder, Assassinate, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Sneed's Old Shredder", game.current_player.minions[0].card.name)

        game = game.copy()

        # The assassinate will kill the shredder, and leave the other player with a legendary minion
        game.play_single_turn()

        self.assertLessEqual(1, len(game.other_player.minions))
        self.assertEqual(CARD_RARITY.LEGENDARY, game.other_player.minions[0].card.rarity)

    def test_AntiqueHealbot(self):
        game = generate_game_for(AntiqueHealbot, Frostbolt, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(21, game.other_player.hero.health)
        game = game.copy()
        game.play_single_turn()
        self.assertEqual(29, game.current_player.hero.health)

    def test_MechanicalYeti(self):
        game = generate_game_for(MechanicalYeti, Fireball, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[0].hand))
        self.assertEqual(8, len(game.players[1].hand))

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(7, len(game.players[0].hand))
        self.assertSparePart(game.players[0].hand[-1])
        self.assertEqual(9, len(game.players[1].hand))
        self.assertSparePart(game.players[1].hand[-1])

    def test_FelCannon(self):
        game = generate_game_for([FelCannon, BoulderfistOgre], [BloodfenRaptor, HarvestGolem, Deathwing],
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(6):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))

        # Fel Cannon should target the Bloodfen Raptor
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Harvest Golem", game.other_player.minions[0].card.name)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)

        game = game.copy()
        game.play_single_turn()
        game.play_single_turn()

        # Fel Cannon should target nothing
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Harvest Golem", game.other_player.minions[0].card.name)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)

        game = game.copy()
        game.play_single_turn()
        game.play_single_turn()

        # Fel Cannon should target ogre

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Harvest Golem", game.other_player.minions[0].card.name)
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(5, game.current_player.minions[1].health)

    def test_OneEyedCheat(self):
        game = generate_game_for([BloodsailCorsair, OneeyedCheat, SouthseaCaptain], BloodsailRaider,
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(MINION_TYPE.PIRATE, game.players[0].minions[0].card.minion_type)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(MINION_TYPE.PIRATE, game.players[0].minions[0].card.minion_type)
        self.assertEqual(MINION_TYPE.PIRATE, game.players[0].minions[1].card.minion_type)
        self.assertFalse(game.players[0].minions[0].stealth)
        game = game.copy()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(MINION_TYPE.PIRATE, game.players[0].minions[0].card.minion_type)
        self.assertEqual(MINION_TYPE.PIRATE, game.players[0].minions[1].card.minion_type)
        self.assertFalse(game.players[0].minions[0].stealth)
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(MINION_TYPE.PIRATE, game.players[1].minions[0].card.minion_type)

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(MINION_TYPE.PIRATE, game.players[0].minions[0].card.minion_type)
        self.assertEqual(MINION_TYPE.PIRATE, game.players[0].minions[1].card.minion_type)
        self.assertEqual(MINION_TYPE.PIRATE, game.players[0].minions[2].card.minion_type)
        self.assertTrue(game.players[0].minions[1].stealth)

    def test_DunemaulShaman(self):
        game = generate_game_for(DunemaulShaman,
                                 [StonetuskBoar, GoldshireFootman, SilverbackPatriarch, MogushanWarden, FenCreeper],
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))
        game = game.copy()
        game.play_single_turn()
        # The shaman's forgetful ability triggers twice.  It hits the boar and and the enemy hero, but not the warden
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual("Mogu'shan Warden", game.other_player.minions[0].card.name)
        self.assertEqual("Silverback Patriarch", game.other_player.minions[1].card.name)
        self.assertEqual(25, game.other_player.hero.health)

    def test_Toshley(self):
        game = generate_game_for(Toshley, Assassinate, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(11):
            game.play_single_turn()

        # The last card in the player's hand should be a spare part.

        self.assertSparePart(game.current_player.hand[-1])
        self.assertNotSparePart(game.other_player.hand[-1])

        # The assassinate should kill Toshley, resulting in yet another spare part.
        game = game.copy()
        game.play_single_turn()
        self.assertSparePart(game.other_player.hand[-1])
        self.assertSparePart(game.other_player.hand[-2])
        self.assertNotSparePart(game.current_player.hand[-1])

    def test_FelReaver(self):
        game = generate_game_for(FelReaver, [ShadowBolt, Wisp, LightsJustice], OneCardPlayingAgent, CardTestingAgent)

        for turn in range(9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(22, game.current_player.deck.left)
        self.assertEqual(7, len(game.current_player.hand))
        self.assertEqual(22, game.other_player.deck.left)
        self.assertEqual(9, len(game.other_player.hand))

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(13, game.other_player.deck.left)
        self.assertEqual(7, len(game.other_player.hand))
        self.assertEqual(21, game.current_player.deck.left)
        self.assertEqual(7, len(game.current_player.hand))

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(12, game.current_player.deck.left)
        self.assertEqual(7, len(game.current_player.hand))
        self.assertEqual(21, game.other_player.deck.left)
        self.assertEqual(7, len(game.other_player.hand))

    def test_Cogmaster(self):
        game = generate_game_for([Cogmaster, Snowchugger], ClockworkGnome, OneCardPlayingAgent, OneCardPlayingAgent)

        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.other_player.minions[0].calculate_attack())

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[1].calculate_attack())

    def test_KingOfBeasts(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, StonetuskBoar, KingOfBeasts], StonetuskBoar,
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(9):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())

        game = game.copy()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[1].calculate_attack())

    def test_Malorne(self):
        game = generate_game_for(Malorne, Assassinate, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(13):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(20, game.current_player.deck.left)

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(21, game.other_player.deck.left)

    def test_TradePrinceGallywix(self):
        game = generate_game_for([Wisp, Wisp, Wisp, TradePrinceGallywix, SinisterStrike], ArcaneExplosion,
                                 OneCardPlayingAgent, CardTestingAgent)

        for turn in range(11):
            game.play_single_turn()

        game.other_player.max_mana += 2
        game = game.copy()
        game.play_single_turn()

        # The opponent played Arcane Explosion Twice, so we should have two copies of it (and none of Gallywix's coin)
        self.assertEqual("Arcane Explosion", game.other_player.hand[-1].name)
        self.assertEqual("Arcane Explosion", game.other_player.hand[-2].name)
        self.assertEqual("Arcane Explosion", game.other_player.hand[-3].name)
        self.assertEqual("Arcane Explosion", game.other_player.hand[-4].name)
        self.assertEqual("Trade Prince Gallywix", game.other_player.hand[-5].name)

        self.assertEqual(0, len(game.current_player.hand))

        game.play_single_turn()

        # The other player should not recieve anything for my spell_cast
        self.assertEqual(0, len(game.other_player.hand))

    def test_MalGanis(self):
        game = generate_game_for([FlameImp, MalGanis], FlameImp, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(17):
            game.play_single_turn()

        game = game.copy()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertTrue(game.current_player.hero.immune)
        self.assertFalse(game.other_player.hero.immune)
        self.assertEqual(5, game.current_player.minions[1].calculate_attack())
        self.assertEqual(4, game.current_player.minions[1].calculate_max_health())
        self.assertEqual(9, game.current_player.minions[0].calculate_attack())
        self.assertEqual(7, game.current_player.minions[0].calculate_max_health())

        for minion in game.other_player.minions:
            self.assertEqual(3, minion.calculate_attack())
            self.assertEqual(2, minion.calculate_max_health())

    def test_FloatingWatcher(self):
        game = generate_game_for(FloatingWatcher, Hellfire, HeroPowerAndCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(13):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(9, game.current_player.hero.health)
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(6, game.other_player.hero.health)
        self.assertEqual(4, game.other_player.minions[0].calculate_attack())
        self.assertEqual(4, game.other_player.minions[0].calculate_max_health())

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.hero.health)
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(6, game.current_player.minions[1].calculate_attack())
        self.assertEqual(6, game.current_player.minions[1].calculate_max_health())

    def test_SouthseaDeckhand(self):
        game = generate_game_for([SouthseaDeckhand, LightsJustice], AcidicSwampOoze,
                                 PlayAndAttackAgent, OneCardPlayingAgent)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(1, len(game.players[0].minions))
        self.assertFalse(game.players[0].minions[0].charge())

        game = game.copy()
        game.play_single_turn()
        # Old minion attacks, equip weapon and attack, new minion gets charge and attacks
        self.assertEqual(25, game.players[1].hero.health)
        self.assertEqual(2, len(game.players[0].minions))
        self.assertTrue(game.players[0].minions[0].charge())
        self.assertTrue(game.players[0].minions[1].charge())

        # Ooze destroys weapon, the deckhands no longer have charge
        game = game.copy()
        game.play_single_turn()

        self.assertFalse(game.players[0].minions[0].charge())
        self.assertFalse(game.players[0].minions[1].charge())

    def test_BolvarFordragon(self):
        game = generate_game_for([MusterForBattle, BolvarFordragon], [FanOfKnives],
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        game = game.copy()
        for turn in range(8):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(0, game.current_player.minions[0].card.calculate_stat(ChangeAttack, 0))

    def test_FoeReaper4000(self):
        game = generate_game_for(FoeReaper4000, [StonetuskBoar, AncientOfWar, AncientOfWar],
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(16):
            game.play_single_turn()
        game = game.copy()
        game.players[0].agent.choose_target = lambda targets: targets[1]
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].health)
        self.assertEqual(4, game.other_player.minions[1].health)
        self.assertEqual(4, game.current_player.minions[1].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(30, game.other_player.hero.health)

    def test_SteamwheedleSniper(self):
        game = generate_game_for(SteamwheedleSniper, StonetuskBoar, PredictableAgent, DoNothingAgent)
        for turn in range(8):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(22, game.other_player.hero.health)
        self.assertEqual(1, game.current_player.minions[1].health)
        self.assertEqual(3, game.current_player.minions[0].health)

    def test_UnstablePortal(self):
        game = generate_game_for(UnstablePortal, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(3):
            game.play_single_turn()
        game = game.copy()
        self.assertEqual(5, len(game.current_player.hand))
        self.assertTrue(game.current_player.hand[-1].is_minion())
        if game.current_player.hand[-1].mana >= 3:
            self.assertEqual(3, game.current_player.hand[-1].mana - game.current_player.hand[-1].mana_cost())

    def test_MimironsHead(self):
        game = generate_game_for([Mechwarper, SpiderTank, ChillwindYeti, MimironsHead, Deathwing], StonetuskBoar,
                                 OneCardPlayingAgent, DoNothingAgent)

        for turn in range(10):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual("V-07-TR-0N", game.current_player.minions[0].card.name)
        self.assertEqual("Chillwind Yeti", game.current_player.minions[1].card.name)

    def test_MistressOfPain(self):
        game = generate_game_for([MistressOfPain, AbusiveSergeant], SinisterStrike,
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(4):
            game.play_single_turn()

        game = game.copy()
        game.play_single_turn()
        self.assertEqual(27, game.current_player.hero.health)
