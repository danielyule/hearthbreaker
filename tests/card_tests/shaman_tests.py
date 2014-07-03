import random
import unittest

from hsgame.agents.basic_agents import PredictableBot
from tests.testing_agents import *
from tests.testing_utils import generate_game_for
from hsgame.cards import *


__author__ = 'Daniel'


class TestShaman(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_ShamanPower(self):
        game = generate_game_for(AlAkirTheWindlord, MogushanWarden, PredictableBot, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stoneclaw Totem", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].taunt)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Healing Totem", game.players[0].minions[1].card.name)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual("Searing Totem", game.players[0].minions[2].card.name)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual("Wrath of Air Totem", game.players[0].minions[3].card.name)
        self.assertEqual(1, game.players[0].minions[3].spell_damage)

        # All Totems are out, nothing should be summoned
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(4, len(game.players[0].minions))

    def test_AlAkirTheWindlord(self):
        game = generate_game_for(AlAkirTheWindlord, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Al'Akir the Windlord", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].wind_fury)
        self.assertTrue(game.players[0].minions[0].charge)
        self.assertTrue(game.players[0].minions[0].divine_shield)
        self.assertTrue(game.players[0].minions[0].taunt)

    def test_DustDevil(self):
        game = generate_game_for(DustDevil, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Dust Devil", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].wind_fury)
        self.assertEqual(2, game.players[0].overload)

        game.play_single_turn()
        # Overload should cause that we start this turn with 0 mana
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, game.players[0].overload)
        self.assertEqual(0, game.players[0].mana)
        self.assertEqual(2, game.players[0].max_mana)

    def test_EarthElemental(self):
        game = generate_game_for(EarthElemental, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        # Earth Elemental should be played
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Earth Elemental", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].taunt)
        self.assertEqual(3, game.players[0].overload)

    def test_FireElemental(self):
        game = generate_game_for(FireElemental, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)

        # Fire Elemental should be played, and its battlecry dealing three damage to opponent
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Fire Elemental", game.players[0].minions[0].card.name)
        self.assertEqual(27, game.players[1].hero.health)

    def test_FlametongueTotem(self):
        game = generate_game_for(StonetuskBoar, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        # There should be three Stonetusk Boars on the board
        self.assertEqual(3, len(game.players[0].minions))

        # add a new Flametongue Totem at index 1
        totem = FlametongueTotem()
        totem.summon(game.players[0], game, 1)

        # The minions to either side should have their attack increased
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].attack_power)
        self.assertEqual(3, game.players[0].minions[2].attack_power)
        self.assertEqual(1, game.players[0].minions[3].attack_power)

        # When removing the minion at index 0, we should not get an error
        game.players[0].minions[0].die(None)
        self.assertEqual(3, len(game.players[0].minions))

        # When removing the minion at index 1, we should have a new minion at index 1,
        # and its attack should be increased
        game.players[0].minions[1].die(None)
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[1].attack_power)

        # Silencing this minion should have no effect on its attack
        game.players[0].minions[1].silence()
        self.assertEqual(3, game.players[0].minions[1].attack_power)

        # We should be able to add a boar on either side of the wolf, and their attack should be increased
        # The attack of the boar which used to be next to the wolf should decrease
        boar = StonetuskBoar()
        boar.summon(game.players[0], game, 0)
        boar.summon(game.players[0], game, 2)
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].attack_power)
        self.assertEqual(3, game.players[0].minions[2].attack_power)
        self.assertEqual(1, game.players[0].minions[3].attack_power)

        # Add a new boar on the left of the totem since we haven't tested that yet
        boar.summon(game.players[0], game, 1)
        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].attack_power)
        self.assertEqual(3, game.players[0].minions[1].attack_power)

        game.players[0].minions[1].die(None)
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].attack_power)

        # If the totem is silenced, then the boars to either side should no longer have increased attack
        game.players[0].minions[1].silence()
        self.assertEqual(1, game.players[0].minions[0].attack_power)
        self.assertEqual(1, game.players[0].minions[2].attack_power)
        self.assertEqual(1, game.players[0].minions[3].attack_power)

    def test_ManaTideTotem(self):
        game = generate_game_for([ManaTideTotem, WarGolem], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(25, game.players[0].deck.left)
        self.assertEqual(0, len(game.players[0].minions))

        # Mana Tide Totem should be played, and we should draw a card at the end of turn
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Mana Tide Totem", game.players[0].minions[0].card.name)
        self.assertEqual(23, game.players[0].deck.left)

        game.play_single_turn()
        # Silence, we should only draw one card next turn
        game.players[0].minions[0].silence()
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(22, game.players[0].deck.left)

    def test_Windspeaker(self):
        game = generate_game_for([StonetuskBoar, Windspeaker], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[0].card.name)
        self.assertFalse(game.players[0].minions[0].wind_fury)

        # Windspeaker should be played, giving the boar windfury
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Windspeaker", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[1].wind_fury)

    def test_AncestralHealing(self):
        game = generate_game_for([FlametongueTotem, AncestralHealing], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Flametongue Totem", game.players[0].minions[0].card.name)
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertFalse(game.players[0].minions[0].taunt)
        game.players[0].minions[0].health = 1

        game.play_single_turn()
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertTrue(game.players[0].minions[0].taunt)

    def test_AncestralSpirit(self):
        game = generate_game_for([ArgentCommander, AncestralSpirit], StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Argent Commander", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertTrue(game.players[0].minions[0].divine_shield)

        game.play_single_turn()
        # Ancestral Spirit should be played on the Argent Commander
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        game.players[0].minions[0].health = 1
        game.players[0].minions[0].divine_shield = False
        # Let the minion die in order to test Ancestral Spirit
        commander = game.players[0].minions[0]
        commander.die(None)
        commander.activate_delayed()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Argent Commander", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertTrue(game.players[0].minions[0].divine_shield)

    def test_Bloodlust(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, StonetuskBoar, StonetuskBoar, Bloodlust], StonetuskBoar,
                                 MinionAttackingAgent, DoNothingBot)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(20, game.players[1].hero.health)

        # Bloodlust should be played, resulting in 4 * 4 = 16 damage
        game.play_single_turn()
        self.assertEqual(4, game.players[1].hero.health)
        # Attack power should be back to normal
        self.assertEqual(1, game.players[0].minions[0].attack_power)

    def test_EarthShock(self):
        game = generate_game_for(EarthShock, ArgentSquire, MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertTrue(game.players[1].minions[0].divine_shield)

        # Earth Shock should be played, resulting in silence which removes the divine shield and then 1 damage
        game.play_single_turn()
        self.assertEqual(0, len(game.players[1].minions))

    def test_FarSight(self):
        game = generate_game_for(FarSight, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        for turn in range(0, 5):
            game.play_single_turn()

        # Far Sight should have been played, our latest card should cost 3 - 3 = 0
        self.assertEqual(0, game.players[0].hand[-1].mana_cost(game.players[0]))
        self.assertEqual(3, game.players[0].hand[0].mana_cost(game.players[0]))
        # Draw a card to make sure the new card doesn't get the effect
        game.players[0].draw()
        self.assertEqual(3, game.players[0].hand[-1].mana_cost(game.players[0]))
        # Our old card shouldn't have been affected
        self.assertEqual(0, game.players[0].hand[-2].mana_cost(game.players[0]))
