import random
import unittest
from hsgame.agents.basic_agents import PredictableBot, DoNothingBot
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Game
from hsgame.replay import SavedGame
from tests.testing_agents import SpellTestingAgent, MinionPlayingAgent, MinionAttackingAgent, OneSpellTestingAgent
from tests.testing_utils import generate_game_for, StackedDeck

from hsgame.cards import *

__author__ = 'Daniel'

class TestMage(unittest.TestCase):

    def setUp(self):
        random.seed(1857)

    def test_ArcaneMissiles(self):
        game = generate_game_for(MogushanWarden, ArcaneMissiles, MinionPlayingAgent,SpellTestingAgent)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(27, game.other_player.hero.health)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Mogu'shan Warden", game.current_player.minions[0].card.name)

        game.play_single_turn()
        #The random numbers work so that both arcane missiles hit the Warden twice and the other player once
        self.assertEqual(10, game.other_player.hero.health)
        self.assertEqual(3, game.other_player.minions[0].health)

    def test_ArcaneMissilesWithSpellPower(self):
        game = SavedGame("tests/replays/card_tests/ArcaneMissilesWithSpellDamage.rep")
        game.start()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(2, game.other_player.minions[0].max_health)
        self.assertEqual(27, game.other_player.hero.health)

        return game

    def test_WaterElemental(self):
        game = generate_game_for(WaterElemental, StonetuskBoar, PredictableBot, DoNothingBot)

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(25, game.other_player.hero.health)
        self.assertFalse(game.other_player.hero.frozen_this_turn)
        self.assertFalse(game.other_player.hero.frozen)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].attack_power)
        self.assertEqual(6, game.current_player.minions[0].health)
        self.assertEqual("Water Elemental", game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(22, game.other_player.hero.health)

        # Always false after the end of a turn
        self.assertFalse(game.other_player.hero.frozen_this_turn)
        self.assertTrue(game.other_player.hero.frozen)

        #Now make sure that attacking the Water Elemental directly will freeze a character
        random.seed(1857)
        game = generate_game_for(WaterElemental, IronbarkProtector, MinionPlayingAgent, PredictableBot)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(5, game.other_player.minions[0].health)
        #The player won't have taken damage because of armour, and so shouldn't be frozen
        self.assertEqual(30, game.current_player.hero.health)
        self.assertFalse(game.current_player.hero.frozen)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(28, game.current_player.hero.health)
        self.assertTrue(game.current_player.hero.frozen)

    def test_IceLance(self):
        game = generate_game_for(IceLance, OasisSnapjaw, SpellTestingAgent, MinionPlayingAgent)
        game.play_single_turn()

        self.assertTrue(game.other_player.hero.frozen)
        self.assertEqual(30, game.other_player.hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertTrue(game.other_player.hero.frozen)
        self.assertEqual(26, game.other_player.hero.health)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertTrue(game.other_player.minions[0].frozen)
        self.assertEqual(7, game.other_player.minions[0].health)

    def test_ManaWyrm(self):
        deck1 = StackedDeck([ManaWyrm(), IceLance(), ManaWyrm(), IceLance(), IceLance(), IceLance()], CHARACTER_CLASS.MAGE)
        deck2 = StackedDeck([IronbeakOwl()], CHARACTER_CLASS.PALADIN)
        game = Game([deck1, deck2], [SpellTestingAgent(), MinionPlayingAgent()])
        game.pre_game()
        game.current_player = 1

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].max_health)
        self.assertEqual("Mana Wyrm",game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].max_health)
        self.assertEqual(2, game.current_player.minions[1].attack_power)
        self.assertEqual(3, game.current_player.minions[1].health)
        self.assertEqual(3, game.current_player.minions[1].max_health)
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].attack_power)
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].max_health)
        self.assertEqual(5, game.current_player.minions[1].attack_power)
        self.assertEqual(3, game.current_player.minions[1].health)
        self.assertEqual(3, game.current_player.minions[1].max_health)

    def test_MirrorImage(self):
        game = generate_game_for(MirrorImage, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(0, game.current_player.minions[0].attack_power)
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual("Mirror Image", game.current_player.minions[0].card.name)
        self.assertEqual(0, game.current_player.minions[0].card.mana)

        self.assertEqual(0, game.current_player.minions[1].attack_power)
        self.assertEqual(2, game.current_player.minions[1].health)
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
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(30, game.other_player.hero.health)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(30, game.other_player.hero.health)

    def test_Frostbolt(self):
        game = generate_game_for(OasisSnapjaw, Frostbolt, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertTrue(game.other_player.hero.frozen)
        self.assertEqual(27, game.other_player.hero.health)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(24, game.other_player.hero.health)
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
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
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual("Sorcerer's Apprentice", game.current_player.minions[0].card.name)

        #Arcane missiles should also have been played, since it is now free
        self.assertEqual(27, game.other_player.hero.health)

        #Make sure the other frostbolts have been properly reduced
        self.assertEqual(1, game.current_player.hand[1].mana_cost(game.current_player))
        self.assertEqual(1, game.current_player.hand[2].mana_cost(game.current_player))

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

        self.assertFalse(game.other_player.hero.frozen)

    def test_Counterspell(self):
        game = generate_game_for(Counterspell, Frostbolt, SpellTestingAgent, SpellTestingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Counterspell", game.current_player.secrets[0].name)

        game.play_single_turn()

        self.assertFalse(game.other_player.hero.frozen)
        self.assertEqual(27, game.other_player.hero.health)
        #Ensure that secrets are being removed after being revealed
        self.assertEqual(0, len(game.other_player.secrets))

    def test_IceBarrier(self):
        game = generate_game_for(IceBarrier, StonetuskBoar, SpellTestingAgent, PredictableBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Ice Barrier", game.current_player.secrets[0].name)

        game.play_single_turn()
        #only one minion because PredictableBot will shoot its own minions if there isn't anything else to shoot.
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, game.other_player.hero.armour)

        #Attacked once on the first turn, the fireballed before getting the armour up
        self.assertEqual(28, game.other_player.hero.health)

        #Make sure we can't have two identical secrets at the same time
        random.seed(1857)
        game = generate_game_for(IceBarrier, StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.secrets))
        self.assertEqual("Ice Barrier", game.other_player.secrets[0].name)

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Ice Barrier", game.current_player.secrets[0].name)

    def test_IceBlock(self):
        game = generate_game_for(IceBlock, Frostbolt, SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(game.other_player.hero.health, 3)
        self.assertEqual(1, len(game.other_player.secrets))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, game.other_player.hero.health)
        self.assertEqual(0, len(game.other_player.secrets))

    def test_MirrorEntity(self):
        game = generate_game_for([StonetuskBoar, MirrorEntity], IronfurGrizzly, SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 5):
            game.play_single_turn()
        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Mirror Entity", game.current_player.secrets[0].name)

        game.play_single_turn()
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual("Ironfur Grizzly", game.other_player.minions[1].card.name)
        self.assertEqual(game.other_player, game.other_player.minions[1].player)
        self.assertEqual(1, game.other_player.minions[1].index)

    def test_Spellbender(self):
        game = generate_game_for(Spellbender, Moonfire, SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        #The moonfire should have been re-directed to the Spellbender, which should have taken one damage
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].attack_power)
        self.assertEqual("Spellbender", game.other_player.minions[0].card.name)

        #Now make sure it doesn't activate when a non-targeted spell is used
        random.seed(1857)
        game = generate_game_for(Spellbender, ArcaneIntellect, SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        #The arcane intellect should not have caused the Spellbender to activate
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(1, len(game.other_player.secrets))


    def test_Vaporize(self):
        game = generate_game_for(Vaporize, FaerieDragon, SpellTestingAgent, MinionAttackingAgent)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual(30, game.other_player.hero.health)

        random.seed(1857)
        game = generate_game_for(Vaporize, Swipe, SpellTestingAgent, PredictableBot)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(28, game.other_player.hero.health)
        self.assertEqual(1, len(game.other_player.secrets))
        self.assertFalse(game.current_player.hero.dead)


    def test_KirinTorMage(self):

        game = generate_game_for([KirinTorMage, Vaporize, Spellbender], StonetuskBoar, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Vaporize", game.current_player.secrets[0].name)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Kirin Tor Mage", game.current_player.minions[0].card.name)
        self.assertEqual(3, game.current_player.hand[0].mana_cost(game.current_player))
        self.assertEqual("Spellbender", game.current_player.hand[0].name)

        random.seed(1857)
        game = generate_game_for([KirinTorMage, Vaporize], StonetuskBoar, OneSpellTestingAgent, DoNothingBot)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(0, len(game.current_player.secrets))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Kirin Tor Mage", game.current_player.minions[0].card.name)
        self.assertEqual(3, game.current_player.hand[2].mana_cost(game.current_player))
        self.assertEqual("Vaporize", game.current_player.hand[2].name)

