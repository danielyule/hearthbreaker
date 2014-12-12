import random
import unittest

from tests.agents.testing_agents import PlayAndAttackAgent, OneCardPlayingAgent, CardTestingAgent
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *
from hearthbreaker.agents.basic_agents import PredictableAgent, DoNothingAgent


class TestRogue(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_DefiasRingleader(self):
        game = generate_game_for(DefiasRingleader, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)

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
        game = generate_game_for(EdwinVanCleef, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)

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
        game = generate_game_for([Backstab, Kidnapper], AzureDrake, PlayAndAttackAgent,
                                 OneCardPlayingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(10, len(game.players[1].hand))

        # Backstab should be played, targeting the drake who survives. Kidnapper should be played next, returning the
        # drake to the owner's hand with the combo.
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Kidnapper", game.players[0].minions[0].card.name)
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(10, len(game.players[1].hand))

    def test_MasterOfDisguise(self):
        game = generate_game_for([StonetuskBoar, MasterOfDisguise], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

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
                                  Shieldbearer], [Sunwalker, Malygos], PlayAndAttackAgent,
                                 OneCardPlayingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        # Lots of turns have passed. The opponent hero shouldn't have died of the poison effect
        self.assertEqual(7, len(game.players[0].minions))
        self.assertEqual(26, game.players[1].hero.health)
        self.assertFalse(game.players[1].hero.dead)
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
        game = generate_game_for(SI7Agent, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        # SI:7 Agent should have been played, no combo
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(30, game.players[1].hero.health)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))

        # Two SI:7 should be played, the second trigger the combo targeting one of our own minions...
        game.play_single_turn()
        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[1].health)

    def test_Assassinate(self):
        game = generate_game_for(Assassinate, Sunwalker, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertTrue(game.players[1].minions[0].divine_shield)
        self.assertTrue(game.players[1].minions[0].taunt)

        # Assassinate should be used on the Sunwalker
        game.play_single_turn()
        self.assertEqual(0, len(game.players[1].minions))

    def test_Backstab(self):
        game = generate_game_for(Backstab, StonetuskBoar, CardTestingAgent, OneCardPlayingAgent)

        # Nothing should happen
        game.play_single_turn()

        # Boar should be played
        game.play_single_turn()
        self.assertEqual(1, len(game.players[1].minions))

        # Backstab should be used on the undamaged boar
        game.play_single_turn()
        self.assertEqual(0, len(game.players[1].minions))

    def test_Betrayal(self):
        game = generate_game_for([IronfurGrizzly, EmperorCobra], Betrayal, OneCardPlayingAgent, CardTestingAgent)

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

    def test_BetrayalMiddle(self):
        game = generate_game_for(StonetuskBoar, Betrayal, CardTestingAgent, CardTestingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        game.players[1].agent.choose_target = lambda targets: targets[len(targets) - 2]

        game.play_single_turn()  # Middle boar kills 2 edge boars

        self.assertEqual(1, len(game.players[0].minions))

    def test_BladeFlurry(self):
        game = generate_game_for(Shieldbearer, BladeFlurry, OneCardPlayingAgent, PredictableAgent)

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
        game = generate_game_for([StonetuskBoar, ColdBlood, ColdBlood], StonetuskBoar,
                                 CardTestingAgent, DoNothingAgent)

        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())

        game.play_single_turn()
        # Two Cold Blood should be played, targeting the Boar. The first one should not have combo, but the second one
        # should have the combo, resulting in 2 + 4 = 6 attack buff
        game.play_single_turn()
        self.assertEqual(7, game.players[0].minions[0].calculate_attack())

    def test_Conceal(self):
        game = generate_game_for([StonetuskBoar, Conceal, MogushanWarden], StonetuskBoar, CardTestingAgent,
                                 DoNothingAgent)

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

    def test_Conceal_Silence(self):
        game = generate_game_for([IronfurGrizzly, Conceal, BoulderfistOgre], MassDispel, CardTestingAgent,
                                 CardTestingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        # Grizzly and Conceal should have been played
        self.assertEqual(1, len(game.players[0].minions))
        self.assertTrue(game.players[0].minions[0].stealth)
        # Stealth should be gone from all minions
        game.play_single_turn()
        self.assertFalse(game.players[0].minions[0].stealth)
        # Conceal would be gone, but it's been removed by silence
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertFalse(game.players[0].minions[0].stealth)

    def test_DeadlyPoison(self):
        game = generate_game_for(DeadlyPoison, StonetuskBoar, PredictableAgent, DoNothingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        # Knife should have been played
        self.assertEqual(1, game.players[0].hero.weapon.base_attack)

        game.play_single_turn()
        # Deadly Poison should have been played
        game.play_single_turn()
        self.assertEqual(3, game.players[0].hero.weapon.base_attack)

    def test_Eviscerate(self):
        game = generate_game_for(Eviscerate, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        # Eviscerate should have been played with no combo, dealing 2 damage
        self.assertEqual(28, game.players[1].hero.health)

        # Just another Eviscerate
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(26, game.players[1].hero.health)

        game.play_single_turn()
        game.play_single_turn()
        # Two Eviscerate should have been played, the first with no combo and a second with combo, dealing
        # 2 + 4 = 6 damage
        self.assertEqual(20, game.players[1].hero.health)

    def test_FanOfKnives(self):
        game = generate_game_for(FanOfKnives, StonetuskBoar, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(5, len(game.players[0].hand))

        # Fan of Knives should be played
        game.play_single_turn()
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(6, len(game.players[0].hand))

    def test_Headcrack(self):
        game = generate_game_for(Headcrack, StonetuskBoar, CardTestingAgent, DoNothingAgent)

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
        self.assertEqual(20, game.players[1].hero.health)
        self.assertEqual(5, len(game.players[0].hand))

    def test_HeadcrackOverload(self):
        game = generate_game_for(Headcrack, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        game.players[0].max_mana = 10
        miracle = GadgetzanAuctioneer()
        miracle.summon(game.players[0], game, 0)

        game.play_single_turn()

        self.assertEqual(24, game.players[1].hero.health)  # 3 Headcracks, 2nd 2 combo'd
        self.assertEqual(6, len(game.players[0].hand))  # 6 = 4 - 3 Headcracks + 3 Auctioneer + 2 Headcrack

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(18, game.players[1].hero.health)  # 3 Headcracks, 2nd 2 combo'd
        self.assertEqual(9, len(game.players[0].hand))  # 9 = 7 - 3 Headcracks + 3 Auctioneer + 2 Headcrack

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(12, game.players[1].hero.health)  # 3 Headcracks, 2nd 2 combo'd
        self.assertEqual(10, len(game.players[0].hand))  # 12 = 10 - 3 Headcracks + 3 Auctioneer + 2 Headcrack

    def test_Preparation(self):
        game = generate_game_for([Preparation, BloodfenRaptor, Headcrack], StonetuskBoar,
                                 PredictableAgent, DoNothingAgent)

        # Preparation should be played. Bloodfen shouldn't be played, since that isn't a spell, but Headcrack should.
        game.play_single_turn()
        self.assertEqual(28, game.players[1].hero.health)
        self.assertEqual(0, len(game.players[0].minions))

    def test_Sap(self):
        game = generate_game_for(Sap, StonetuskBoar, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(5, len(game.players[1].hand))
        self.assertEqual(1, len(game.players[1].minions))

        # Sap should be played, targeting the boar
        game.play_single_turn()
        self.assertEqual(6, len(game.players[1].hand))
        self.assertEqual(0, len(game.players[1].minions))

    def test_Shadowstep(self):
        game = generate_game_for([StonetuskBoar, Shadowstep], StonetuskBoar, PlayAndAttackAgent,
                                 DoNothingAgent)

        # The Boar should be played, Shadowstep will follow targeting the Boar
        game.play_single_turn()
        self.assertEqual(3, len(game.players[0].hand))
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(0, game.players[0].hand[2].mana_cost(game.players[0]))

    def test_Shiv(self):
        game = generate_game_for(Shiv, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)
        self.assertEqual(4, len(game.players[0].hand))

        # Shiv should be played, targeting enemy hero. A card should be drawn.
        game.play_single_turn()
        self.assertEqual(29, game.players[1].hero.health)
        self.assertEqual(5, len(game.players[0].hand))

    def test_SinisterStrike(self):
        game = generate_game_for(SinisterStrike, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        self.assertEqual(30, game.players[1].hero.health)

        # Sinister Strike should be played.
        game.play_single_turn()
        self.assertEqual(27, game.players[1].hero.health)

    def test_Sprint(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, StonetuskBoar, StonetuskBoar, StonetuskBoar,
                                  StonetuskBoar, StonetuskBoar, Sprint], StonetuskBoar,
                                 CardTestingAgent, DoNothingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].hand))

        # Sprint should be played.
        game.play_single_turn()
        self.assertEqual(6, len(game.players[0].hand))

    def test_Vanish(self):
        game = generate_game_for([StonetuskBoar, Vanish], StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(5, len(game.players[1].minions))
        self.assertEqual(4, len(game.players[1].hand))

        # Vanish should be played.
        game.play_single_turn()
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(8, len(game.players[0].hand))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(9, len(game.players[1].hand))

    def test_AssassinsBlade(self):
        game = generate_game_for(AssassinsBlade, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(3, game.players[0].hero.weapon.base_attack)
        self.assertEqual(4, game.players[0].hero.weapon.durability)

    def test_PerditionsBlade(self):
        game = generate_game_for(PerditionsBlade, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, game.players[0].hero.weapon.base_attack)
        self.assertEqual(2, game.players[0].hero.weapon.durability)
        self.assertEqual(29, game.players[1].hero.health)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(27, game.players[1].hero.health)

        # Test Combo (1 + 2 = 3 damage)
        game.play_single_turn()
        self.assertEqual(2, game.players[0].hero.weapon.base_attack)
        self.assertEqual(2, game.players[0].hero.weapon.durability)
        self.assertEqual(24, game.players[1].hero.health)

    def test_AnubarAmbusher(self):
        game = generate_game_for(AnubarAmbusher, SiphonSoul, OneCardPlayingAgent, CardTestingAgent)

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[0].hand))

        # Siphon Soul should be played
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(7, len(game.players[0].hand))

    def test_AnubarAmbusher_no_targets(self):
        game = generate_game_for(AnubarAmbusher, StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))

        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))

    def test_AnubarAmbusher_many_targets(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, StonetuskBoar, AnubarAmbusher], StonetuskBoar,
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))

        game.current_player.minions[0].die(None)
        game.check_delayed()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(7, len(game.current_player.minions))
        self.assertEqual(7, len(game.other_player.minions))
        game.current_player.minions[0].silence()
        game.current_player.minions[0].die(None)
        game.check_delayed()
        self.assertEqual(6, len(game.current_player.minions))
        self.assertEqual(7, len(game.other_player.minions))
