import random
import unittest
from tests.testing_agents import *
from tests.testing_utils import generate_game_for
from hsgame.cards import *
from hsgame.agents.basic_agents import PredictableBot


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

    def test_PatientAssassin(self):
        game = generate_game_for([PatientAssassin, Shieldbearer, Shieldbearer, Shieldbearer, Shieldbearer, Shieldbearer,
                                  Shieldbearer], [Sunwalker, Malygos], PredictableAgentWithoutHeroPower,
                                 MinionPlayingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        # Lots of turns have passed. The opponent hero shouldn't have died of the poison effect
        self.assertEqual(7, len(game.players[0].minions))
        self.assertEqual(26, game.players[1].hero.health)
        # And Sunwalker should have been played
        self.assertEqual(1, len(game.players[1].minions))
        self.assertTrue(game.players[1].minions[0].divine_shield)

        # Patient Assassin should attack the Sunwalker, but only divine shield should be affected
        game.play_single_turn()
        self.assertEqual(6, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertFalse(game.players[1].minions[0].divine_shield)
        self.assertEqual(5, game.players[1].minions[0].health)

        # A new Patient Assassin should be played
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(7, len(game.players[0].minions))

        # Patient Assassin should attack again, this time killing the Sunwalker since it no longer has divine shield
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(6, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))

    def test_SI7Agent(self):
        game = generate_game_for(SI7Agent, StonetuskBoar, SpellTestingAgent, DoNothingBot)

        for turn in range(0, 6):
            game.play_single_turn()

        # SI:7 Agent should have been played, no combo
        self.assertEqual(1, len(game.players[0].minions))

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(5, len(game.players[0].minions))

        # Two SI:7 should be played, the second trigger the combo targeting one of our own minions...
        game.play_single_turn()
        self.assertEqual(7, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[1].health)

    def test_Assassinate(self):
        game = generate_game_for(Assassinate, Sunwalker, SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertTrue(game.players[1].minions[0].divine_shield)
        self.assertTrue(game.players[1].minions[0].taunt)

        # Assassinate should be used on the Sunwalker
        game.play_single_turn()
        self.assertEqual(0, len(game.players[1].minions))

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

    def test_Betrayal(self):
        game = generate_game_for([IronfurGrizzly, EmperorCobra], Betrayal, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))

        # Betrayal should be played on the Emperor Cobra, who should kill the grizzly because of the poisonous effect,
        # and the cobra shouldn't take any damage at all
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Emperor Cobra", game.players[0].minions[0].card.name)
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertFalse(game.players[0].minions[0].immune)

    def test_BladeFlurry(self):
        game = generate_game_for(Shieldbearer, BladeFlurry, MinionPlayingAgent, PredictableBot)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[1].health)
        self.assertEqual(3, game.players[0].minions[2].health)
        self.assertEqual(4, game.players[0].minions[3].health)

        # An attack with our knife should first happen, and then should Blade Flurry be played, destroying our knife
        # and dealing 1 damage to all enemy minions
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(29, game.players[0].hero.health)
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertEqual(2, game.players[0].minions[2].health)
        self.assertEqual(3, game.players[0].minions[3].health)

    def test_ColdBlood(self):
        game = generate_game_for([StonetuskBoar, ColdBlood, ColdBlood], StonetuskBoar, SpellTestingAgent, DoNothingBot)

        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())

        game.play_single_turn()
        # Two Cold Blood should be played, targeting the Boar. The first one should not have combo, but the second one
        # should have the combo, resulting in 2 + 4 = 6 attack buff
        game.play_single_turn()
        self.assertEqual(7, game.players[0].minions[0].calculate_attack())

    def test_Conceal(self):
        game = generate_game_for([StonetuskBoar, Conceal, MogushanWarden], StonetuskBoar, SpellTestingAgent,
                                 DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        # Stonetusk and Conceal should have been played
        self.assertEqual(1, len(game.players[0].minions))
        self.assertTrue(game.players[0].minions[0].stealth)

        game.play_single_turn()
        # Conceal should fade off
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertFalse(game.players[0].minions[0].stealth)
