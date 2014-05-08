import random
import unittest
from hsgame.agents.basic_agents import PredictableBot, DoNothingBot
from hsgame.constants import CHARACTER_CLASS
from hsgame.game_objects import Game
from tests.testing_agents import *
from tests.testing_utils import generate_game_for, StackedDeck
from hsgame.replay import SavedGame

from hsgame.cards import *

__author__ = 'Daniel'

class TestPriest(unittest.TestCase):

    def setUp(self):
        random.seed(1857)


    def testPriestPower(self):
        game = generate_game_for(CircleOfHealing, MogushanWarden, PredictableBot, DoNothingBot)

        game.players[1].health = 20

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(22, game.players[1].health)


    def testCircleOfHealing(self):
        deck1 = StackedDeck([CircleOfHealing(), MogushanWarden(), CircleOfHealing(), CircleOfHealing(), CircleOfHealing(), CircleOfHealing(), CircleOfHealing()], CHARACTER_CLASS.PRIEST)
        deck2 = StackedDeck([MogushanWarden()], CHARACTER_CLASS.PALADIN)
        game = Game([deck1, deck2], [SpellTestingAgent(), MinionPlayingAgent()])
        game.pre_game()
        game.current_player = 1
        
        for turn in range(0, 8):
            game.play_single_turn()

        game.players[0].minions[0].defense = 4
        game.players[1].minions[0].defense = 4
        game.play_single_turn() # Circle of Healing should be played
        self.assertEqual(game.players[0].minions[0].max_defense, game.players[0].minions[0].defense)
        self.assertEqual(game.players[1].minions[0].max_defense, game.players[1].minions[0].defense)
        
    def testDivineSpirit(self):
        game = generate_game_for(DivineSpirit, MogushanWarden, SpellTestingAgent, MinionPlayingAgent)
        
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].attack_power)
        self.assertEqual(7, game.players[1].minions[0].defense)
        self.assertEqual(7, game.players[1].minions[0].max_defense)
        game.play_single_turn() # Two Divine Spirits should be played
        self.assertEqual(1, game.players[1].minions[0].attack_power)
        self.assertEqual(28, game.players[1].minions[0].defense)
        self.assertEqual(28, game.players[1].minions[0].max_defense)
        # Test that this spell is being silenced properly as well
        game.players[1].minions[0].silence()
        self.assertEqual(1, game.players[1].minions[0].attack_power)
        self.assertEqual(7, game.players[1].minions[0].defense)
        self.assertEqual(7, game.players[1].minions[0].max_defense)
        game.play_single_turn()
        # Let's say the minion got damaged
        game.players[1].minions[0].defense = 4
        game.play_single_turn() # Three Divine Spirits should be played
        self.assertEqual(1, game.players[1].minions[0].attack_power)
        self.assertEqual(32, game.players[1].minions[0].defense)
        self.assertEqual(35, game.players[1].minions[0].max_defense)
        # Test that this spell is being silenced properly as well
        game.players[1].minions[0].silence()
        self.assertEqual(1, game.players[1].minions[0].attack_power)
        self.assertEqual(7, game.players[1].minions[0].defense)
        self.assertEqual(7, game.players[1].minions[0].max_defense)
        
    def testHolyFire(self):
        game = generate_game_for(HolyFire, MogushanWarden, SpellTestingAgent, MinionPlayingAgent)
        
        for turn in range(0, 10):
            game.play_single_turn()

        game.players[0].health = 20
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].attack_power)
        self.assertEqual(7, game.players[1].minions[0].defense)
        self.assertEqual(7, game.players[1].minions[0].max_defense)
        game.play_single_turn() # Holy Fire should be played
        self.assertEqual(1, game.players[1].minions[0].attack_power)
        self.assertEqual(2, game.players[1].minions[0].defense)
        self.assertEqual(7, game.players[1].minions[0].max_defense)
        self.assertEqual(25, game.players[0].health)
        
    def testHolyNova(self):
        deck1 = StackedDeck([MogushanWarden(), HolyNova()], CHARACTER_CLASS.PRIEST)
        deck2 = StackedDeck([MogushanWarden()], CHARACTER_CLASS.PALADIN)
        game = Game([deck1, deck2], [SpellTestingAgent(), MinionPlayingAgent()])
        game.pre_game()
        game.current_player = 1
        
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        game.players[0].minions[0].defense = 4 # Fake damage
        self.assertEqual(4, game.players[0].minions[0].defense)
        self.assertEqual(7, game.players[1].minions[0].defense)
        game.play_single_turn() # Holy Nova should be played
        self.assertEqual(6, game.players[0].minions[0].defense)
        self.assertEqual(5, game.players[1].minions[0].defense)