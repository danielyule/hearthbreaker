import random
import unittest
from tests.testing_agents import *
from tests.testing_utils import generate_game_for
from hsgame.cards import *


class TestRogue(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_DefiasRingleader(self):
        game = generate_game_for(DefiasRingleader, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Defias Ringleader", game.players[0].minions[0].card.name)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))

        # Combo should activate this turn
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual("Defias Bandit", game.players[0].minions[1].card.name)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)

    def test_EdwinVanCleef(self):
        game = generate_game_for(EdwinVanCleef, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))

        # Two Edwins should be played this turn, the second with a +2/+2 buff with the combo
        game.play_single_turn()
        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual("Edwin VanCleef", game.players[0].minions[0].card.name)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].health)

    def test_Kidnapper(self):
        game = generate_game_for([Backstab, Kidnapper], AzureDrake, PredictableAgentWithoutHeroPower,
                                 MinionPlayingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(9, len(game.players[1].hand))

        # Backstab should be played, targeting the drake who survives. Kidnapper should be played next, returning the
        # drake to the owner's hand with the combo.
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Kidnapper", game.players[0].minions[0].card.name)
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(10, len(game.players[1].hand))

    def test_MasterOfDisguise(self):
        game = generate_game_for([StonetuskBoar, MasterOfDisguise], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertFalse(game.players[0].minions[0].stealth)

        # Master of Disguise should be played, targeting the boar.
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[1].card.name)
        self.assertTrue(game.players[0].minions[1].stealth)

    def test_Backstab(self):
        game = generate_game_for(Backstab, StonetuskBoar, SpellTestingAgent, MinionPlayingAgent)

        # Nothing should happen
        game.play_single_turn()

        # Boar should be played
        game.play_single_turn()
        self.assertEqual(1, len(game.players[1].minions))

        # Backstab should be used on the undamaged boar
        game.play_single_turn()
        self.assertEqual(0, len(game.players[1].minions))
