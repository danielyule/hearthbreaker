import random
import unittest
from hsgame.agents.basic_agents import PredictableBot, DoNothingBot
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Game
from hsgame.replay import SavedGame
from tests.testing_agents import SpellTestingAgent, MinionPlayingAgent
from tests.testing_utils import generate_game_for, StackedDeck

from hsgame.cards import *

__author__ = 'Daniel'

class TestMage(unittest.TestCase):

    def setUp(self):
        random.seed(1857)

    def testArcaneMissiles(self):
        game = generate_game_for(MogushanWarden, ArcaneMissiles, MinionPlayingAgent,SpellTestingAgent)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(27, game.other_player.health)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Mogu'shan Warden", game.current_player.minions[0].card.name)

        game.play_single_turn()
        #The random numbers work so that both arcane missiles hit the Warden twice and the other player once
        self.assertEqual(10, game.other_player.health)
        self.assertEqual(3, game.other_player.minions[0].defense)

    def testArcaneMissilesWithSpellPower(self):
        game = SavedGame("tests/replays/card_tests/ArcaneMissilesWithSpellDamage.rep")
        game.start()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].defense)
        self.assertEqual(2, game.other_player.minions[0].max_defense)
        self.assertEqual(27, game.other_player.health)

        return game

    def testWaterElemental(self):
        game = generate_game_for(WaterElemental, StonetuskBoar, PredictableBot, DoNothingBot)

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(25, game.other_player.health)
        self.assertFalse(game.other_player.frozen_this_turn)
        self.assertFalse(game.other_player.frozen)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].attack_power)
        self.assertEqual(6, game.current_player.minions[0].defense)
        self.assertEqual("Water Elemental", game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(22, game.other_player.health)

        # Always false after the end of a turn
        self.assertFalse(game.other_player.frozen_this_turn)
        self.assertTrue(game.other_player.frozen)

    def testIceLance(self):
        game = generate_game_for(IceLance, OasisSnapjaw, SpellTestingAgent, MinionPlayingAgent)
        game.play_single_turn()

        self.assertTrue(game.other_player.frozen)
        self.assertEqual(30, game.other_player.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertTrue(game.other_player.frozen)
        self.assertEqual(26, game.other_player.health)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertTrue(game.other_player.minions[0].frozen)
        self.assertEqual(7, game.other_player.minions[0].defense)

    def test_ManaWyrm(self):
        deck1 = StackedDeck([ManaWyrm(), IceLance(), ManaWyrm(), IceLance(), IceLance(), IceLance()], CHARACTER_CLASS.MAGE)
        deck2 = StackedDeck([IronbeakOwl()], CHARACTER_CLASS.PALADIN)
        game = Game([deck1, deck2], [SpellTestingAgent(), MinionPlayingAgent()])
        game.pre_game()
        game.current_player = 1

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual(3, game.current_player.minions[0].defense)
        self.assertEqual(3, game.current_player.minions[0].max_defense)
        self.assertEqual("Mana Wyrm",game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual(3, game.current_player.minions[0].defense)
        self.assertEqual(3, game.current_player.minions[0].max_defense)
        self.assertEqual(2, game.current_player.minions[1].attack_power)
        self.assertEqual(3, game.current_player.minions[1].defense)
        self.assertEqual(3, game.current_player.minions[1].max_defense)
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual(3, game.current_player.minions[0].defense)
        self.assertEqual(3, game.current_player.minions[0].max_defense)
        self.assertEqual(5, game.current_player.minions[1].attack_power)
        self.assertEqual(3, game.current_player.minions[1].defense)
        self.assertEqual(3, game.current_player.minions[1].max_defense)

    def test_MirrorImage(self):
        game = generate_game_for(MirrorImage, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(0, game.current_player.minions[0].attack_power)
        self.assertEqual(2, game.current_player.minions[0].defense)
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual("Mirror Image", game.current_player.minions[0].card.name)
        self.assertEqual(0, game.current_player.minions[0].card.mana)

        self.assertEqual(0, game.current_player.minions[1].attack_power)
        self.assertEqual(2, game.current_player.minions[1].defense)
        self.assertTrue(game.current_player.minions[1].taunt)
        self.assertEqual("Mirror Image", game.current_player.minions[1].card.name)
        self.assertEqual(0, game.current_player.minions[1].card.mana)


    def test_ArcaneExplosion(self):
        game = generate_game_for(BloodfenRaptor, ArcaneExplosion, MinionPlayingAgent, SpellTestingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].defense)
        self.assertEqual(30, game.other_player.health)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].defense)
        self.assertEqual(30, game.other_player.health)

    def test_Frostbolt(self):
        game = generate_game_for(OasisSnapjaw, Frostbolt, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertTrue(game.other_player.frozen)
        self.assertEqual(27, game.other_player.health)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(24, game.other_player.health)
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].defense)
        self.assertTrue(game.other_player.minions[0].frozen)

    def test_SorcerersApprentice(self):
        deck1 = StackedDeck([SorcerersApprentice(), ArcaneMissiles(), SorcerersApprentice(), Frostbolt(), Frostbolt(),
                             Frostbolt()], CHARACTER_CLASS.MAGE)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.PRIEST)
        game = Game([deck1, deck2], [SpellTestingAgent(), DoNothingBot()])
        game.pre_game()
        game.current_player = game.players[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].attack_power)
        self.assertEqual(2, game.current_player.minions[0].defense)
        self.assertEqual("Sorcerer's Apprentice", game.current_player.minions[0].card.name)

        #Arcane missiles should also have been played, since it is now free
        self.assertEqual(27, game.other_player.health)

        #Make sure the other frostbolts have been properly reduced
        self.assertEqual(1, game.current_player.hand[1].mana)
        self.assertEqual(1, game.current_player.hand[2].mana)

        game.play_single_turn()
        game.play_single_turn()

        #Both Sorcer's Apprentices are killed by friendly Frostbolts.
        self.assertEqual(0, len(game.current_player.minions))

        #Make sure that the cards in hand are no longer reduced
        self.assertEqual(2, game.current_player.hand[0].mana)

    def test_ArcaneIntellect(self):
        game = generate_game_for(ArcaneIntellect, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(7, len(game.current_player.hand))

    def test_FrostNova(self):
        game = generate_game_for(FrostNova, StonetuskBoar, SpellTestingAgent, MinionPlayingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        for minion in game.other_player.minions:
            self.assertTrue(minion.frozen)

        self.assertFalse(game.other_player.frozen)


    def test_IceBarrier(self):
        game = generate_game_for(IceBarrier, StonetuskBoar, SpellTestingAgent, PredictableBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Ice Barrier", game.current_player.secrets[0].name)

        game.play_single_turn()
        #only one minion because PredictableBot will shoot its own minions if there isn't anything else to shoot.
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, game.other_player.armour)

        #Attacked once on the first turn, the fireballed before getting the armour up
        self.assertEqual(28, game.other_player.health)

