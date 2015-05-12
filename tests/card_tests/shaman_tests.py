import random
import unittest
from hearthbreaker.cards.spells.neutral import TheCoin

from tests.agents.testing_agents import OneCardPlayingAgent, MinionAttackingAgent, CardTestingAgent, \
    PlayAndAttackAgent
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *
from hearthbreaker.constants import MINION_TYPE
from hearthbreaker.agents.basic_agents import PredictableAgent, DoNothingAgent


class TestShaman(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_AlAkirTheWindlord(self):
        game = generate_game_for(AlAkirTheWindlord, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Al'Akir the Windlord", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].windfury())
        self.assertTrue(game.players[0].minions[0].charge())
        self.assertTrue(game.players[0].minions[0].divine_shield)
        self.assertTrue(game.players[0].minions[0].taunt)

    def test_DustDevil(self):
        game = generate_game_for(DustDevil, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Dust Devil", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].windfury())
        self.assertEqual(2, game.players[0].upcoming_overload)

        game.play_single_turn()
        # Overload should cause that we start this turn with 0 mana
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(0, game.players[0].upcoming_overload)
        self.assertEqual(0, game.players[0].mana)
        self.assertEqual(2, game.players[0].max_mana)

    def test_EarthElemental(self):
        game = generate_game_for(EarthElemental, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        # Earth Elemental should be played
        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Earth Elemental", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].taunt)
        self.assertEqual(3, game.players[0].upcoming_overload)

    def test_FireElemental(self):
        game = generate_game_for(FireElemental, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)

        # Fire Elemental should be played, and its battlecry dealing three damage to opponent
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Fire Elemental", game.players[0].minions[0].card.name)
        self.assertEqual(27, game.players[1].hero.health)

    def test_FlametongueTotem(self):
        game = generate_game_for(StonetuskBoar, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        # There should be three Stonetusk Boars on the board
        self.assertEqual(3, len(game.players[0].minions))

        # add a new Flametongue Totem at index 1
        totem = FlametongueTotem()
        totem.summon(game.players[0], game, 1)

        # The minions to either side should have their attack increased
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[2].calculate_attack())
        self.assertEqual(1, game.players[0].minions[3].calculate_attack())

        # When removing the minion at index 0, we should not get an error
        game.players[0].minions[0].die(None)
        game.players[0].minions[0].activate_delayed()
        self.assertEqual(3, len(game.players[0].minions))

        # When removing the minion at index 1, we should have a new minion at index 1,
        # and its attack should be increased
        game.players[0].minions[1].die(None)
        game.players[0].minions[1].activate_delayed()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())

        # Silencing this minion should have no effect on its attack
        game.players[0].minions[1].silence()
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())

        # We should be able to add a boar on either side of the wolf, and their attack should be increased
        # The attack of the boar which used to be next to the wolf should decrease
        boar = StonetuskBoar()
        boar.summon(game.players[0], game, 0)
        boar.summon(game.players[0], game, 2)
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[2].calculate_attack())
        self.assertEqual(1, game.players[0].minions[3].calculate_attack())

        # Add a new boar on the left of the totem since we haven't tested that yet
        boar.summon(game.players[0], game, 1)
        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())

        game.players[0].minions[1].die(None)
        game.players[0].minions[1].activate_delayed()
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())

        # If the totem is silenced, then the boars to either side should no longer have increased attack
        game.players[0].minions[1].silence()
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[2].calculate_attack())
        self.assertEqual(1, game.players[0].minions[3].calculate_attack())

    def test_ManaTideTotem(self):
        game = generate_game_for([ManaTideTotem, WarGolem], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

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

    def test_UnboundElemental(self):
        game = generate_game_for([UnboundElemental, DustDevil, DustDevil], StonetuskBoar, OneCardPlayingAgent,
                                 DoNothingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Unbound Elemental", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].calculate_max_health())

        # One Dust Devil should be played, giving the Unbound Elemental +1/+1
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[-1].calculate_attack())
        self.assertEqual(5, game.players[0].minions[-1].calculate_max_health())
        # Test the silence
        game.players[0].minions[-1].silence()
        self.assertEqual(2, game.players[0].minions[-1].calculate_attack())
        self.assertEqual(4, game.players[0].minions[-1].calculate_max_health())

        # Another Dust Devil, nothing should happen because of silence
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[-1].calculate_attack())
        self.assertEqual(4, game.players[0].minions[-1].calculate_max_health())

    def test_Windspeaker(self):
        game = generate_game_for([StonetuskBoar, Windspeaker], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[0].card.name)
        self.assertFalse(game.players[0].minions[0].windfury())

        # Windspeaker should be played, giving the boar windfury
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual("Windspeaker", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[1].windfury())

    def test_AncestralHealing(self):
        game = generate_game_for([FlametongueTotem, AncestralHealing], StonetuskBoar,
                                 OneCardPlayingAgent, DoNothingAgent)

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
        game = generate_game_for([ArgentCommander, AncestralSpirit], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

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

    def test_AncestralSpiritDeathrattle(self):
        game = generate_game_for([LootHoarder, AncestralSpirit], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[0].hand))

        loot = game.players[0].minions[0]
        loot.die(None)
        loot.activate_delayed()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[0].hand))

    def test_Bloodlust(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, StonetuskBoar, StonetuskBoar, Bloodlust], StonetuskBoar,
                                 MinionAttackingAgent, DoNothingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(20, game.players[1].hero.health)

        # Bloodlust should be played, resulting in 4 * 4 = 16 damage
        game.play_single_turn()
        self.assertEqual(4, game.players[1].hero.health)
        # Attack power should be back to normal
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())

    def test_EarthShock(self):
        game = generate_game_for(EarthShock, ArgentSquire, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertTrue(game.players[1].minions[0].divine_shield)

        # Earth Shock should be played, resulting in silence which removes the divine shield and then 1 damage
        game.play_single_turn()
        self.assertEqual(0, len(game.players[1].minions))

    def test_FarSight(self):
        game = generate_game_for(FarSight, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        # Far Sight should have been played, our latest card should cost 3 - 3 = 0
        self.assertEqual(0, game.players[0].hand[-1].mana_cost())
        self.assertEqual(3, game.players[0].hand[0].mana_cost())
        # Draw a card to make sure the new card doesn't get the effect
        game.players[0].draw()
        self.assertEqual(3, game.players[0].hand[-1].mana_cost())
        # Our old card shouldn't have been affected
        self.assertEqual(0, game.players[0].hand[-2].mana_cost())

    def test_FeralSpirit(self):
        game = generate_game_for(FeralSpirit, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))

        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertTrue(game.players[0].minions[0].taunt)
        self.assertEqual("Spirit Wolf", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].minions[0].card.mana)

        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(3, game.players[0].minions[1].health)
        self.assertTrue(game.players[0].minions[1].taunt)
        self.assertEqual("Spirit Wolf", game.players[0].minions[1].card.name)
        self.assertEqual(2, game.players[0].minions[1].card.mana)

        self.assertEqual(2, game.players[0].upcoming_overload)

    def test_VitalityTotem(self):
        game = generate_game_for(VitalityTotem, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        game.players[0].hero.health = 20
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(24, game.players[0].hero.health)
        self.assertEqual(0, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()
        # player now has two vitality totems in play
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(2, len(game.players[0].minions))

    def test_ForkedLightning(self):
        game = generate_game_for(ForkedLightning, StonetuskBoar, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        # Nothing should have happened yet, since the opponent haven't got 2 minions until now
        self.assertEqual(2, len(game.players[1].minions))

        # Forked Lightning should be played
        game.play_single_turn()
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(2, game.players[0].upcoming_overload)

    def test_FrostShock(self):
        game = generate_game_for(FrostShock, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        # Frost Shock should be played
        game.play_single_turn()
        self.assertEqual(29, game.players[1].hero.health)
        self.assertTrue(game.players[1].hero.frozen)

    def test_Hex(self):
        game = generate_game_for(ChillwindYeti, Hex, OneCardPlayingAgent, CardTestingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertFalse(game.players[0].minions[0].taunt)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual("Chillwind Yeti", game.players[0].minions[0].card.name)

        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertTrue(game.players[0].minions[0].taunt)
        self.assertEqual(0, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual("Frog", game.players[0].minions[0].card.name)
        self.assertEqual(MINION_TYPE.BEAST, game.players[0].minions[0].card.minion_type)

    def test_LavaBurst(self):
        game = generate_game_for(LavaBurst, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        self.assertEqual(25, game.players[1].hero.health)
        self.assertEqual(2, game.players[0].upcoming_overload)

    def test_LightningBolt(self):
        game = generate_game_for(LightningBolt, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        self.assertEqual(27, game.players[1].hero.health)
        self.assertEqual(1, game.players[0].upcoming_overload)

    def test_LightningStorm(self):
        game = generate_game_for(LightningStorm, Shieldbearer, CardTestingAgent, PlayAndAttackAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        # Lightning Storm should be played
        game.play_single_turn()
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].health)
        self.assertEqual(2, game.players[1].minions[1].health)
        self.assertEqual(2, game.players[1].minions[2].health)
        self.assertEqual(2, game.players[0].upcoming_overload)

    def test_RockbiterWeapon(self):
        game = generate_game_for(RockbiterWeapon, Shieldbearer, PlayAndAttackAgent, DoNothingAgent)

        self.assertEqual(30, game.players[1].hero.health)

        # Rockbiter Weapon should be played and used
        game.play_single_turn()
        self.assertEqual(27, game.players[1].hero.health)

    def test_RockbiterWeapon_and_Hex(self):
        game = generate_game_for([IronfurGrizzly, RockbiterWeapon, Hex], StonetuskBoar,
                                 CardTestingAgent, DoNothingAgent)

        for turn in range(7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Frog", game.current_player.minions[0].card.name)

    def test_RockbiterWeapon_and_BaronGeddon(self):
        game = generate_game_for([BaronGeddon, RecklessRocketeer, RockbiterWeapon], StonetuskBoar,
                                 PlayAndAttackAgent, DoNothingAgent)

        for turn in range(15):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Baron Geddon", game.current_player.minions[0].card.name)
        self.assertEqual(11, game.other_player.hero.health)

    def test_TotemicMight(self):
        game = generate_game_for([TotemicMight, StonetuskBoar], Shieldbearer, PredictableAgent, DoNothingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[0].card.name)

        # Hero power and Totemic Might should be played
        game.play_single_turn()
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_max_health())
        self.assertEqual("Stoneclaw Totem", game.players[0].minions[1].card.name)
        self.assertEqual(4, game.players[0].minions[1].calculate_max_health())

    def test_Windfury(self):
        game = generate_game_for(Windfury, StonetuskBoar, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertFalse(game.players[1].minions[0].windfury())

        # Windfury should be played
        game.play_single_turn()
        self.assertTrue(game.players[1].minions[0].windfury())

    def test_Doomhammer(self):
        game = generate_game_for(Doomhammer, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(30, game.players[1].hero.health)
        self.assertFalse(game.players[0].hero.windfury())

        # Doomhammer should be played
        game.play_single_turn()
        self.assertTrue(game.players[0].hero.windfury())
        self.assertEqual(2, game.players[0].hero.weapon.base_attack)
        self.assertEqual(6, game.players[0].hero.weapon.durability)
        self.assertEqual(2, game.players[0].upcoming_overload)
        self.assertEqual(26, game.players[1].hero.health)

    def test_StormforgedAxe(self):
        game = generate_game_for(StormforgedAxe, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(2, game.players[0].hero.weapon.base_attack)
        self.assertEqual(3, game.players[0].hero.weapon.durability)
        self.assertEqual(1, game.players[0].upcoming_overload)

    def test_Crackle(self):
        game = generate_game_for(Crackle, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(25, game.players[1].hero.health)
        self.assertEqual(1, game.players[0].upcoming_overload)

    def test_SiltfinSpiritwalker(self):
        game = generate_game_for([MurlocTidecaller, MurlocTidehunter, SiltfinSpiritwalker, Deathwing],
                                 [MurlocTidecaller, Hellfire, BaneOfDoom], OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(6):
            game.play_single_turn()

        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))

        # Play Siltfin

        game.play_single_turn()

        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))

        self.assertEqual(4, len(game.current_player.hand))
        self.assertEqual(7, len(game.other_player.hand))

        # Hellfire will kill all the murlocs but the siltfin.
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(7, len(game.other_player.hand))
        self.assertEqual(0, len(game.current_player.minions))
        self.assertEqual(7, len(game.current_player.hand))

    def test_WhirlingZapOMatic(self):
        game = generate_game_for(WhirlingZapomatic, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Whirling Zap-o-matic", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].windfury())

    def test_DunemaulShaman(self):
        game = generate_game_for(DunemaulShaman,
                                 [StonetuskBoar, GoldshireFootman, SilverbackPatriarch, MogushanWarden],
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))

        game.play_single_turn()
        # The shaman's forgetful ability triggers once.  It hits the warden one time (its intended target)
        # and the footman one time (after triggering forgetful)
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual("Mogu'shan Warden", game.other_player.minions[0].card.name)
        self.assertEqual("Silverback Patriarch", game.other_player.minions[1].card.name)
        self.assertEqual("Stonetusk Boar", game.other_player.minions[2].card.name)
        self.assertEqual(30, game.other_player.hero.health)

    def test_Powermace(self):
        game = generate_game_for([Powermace, SpiderTank, SpiderTank], Wisp, PlayAndAttackAgent, DoNothingAgent)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(27, game.players[1].hero.health)
        self.assertEqual(3, game.players[0].hero.weapon.base_attack)
        self.assertEqual(1, game.players[0].hero.weapon.durability)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(24, game.players[1].hero.health)
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

    def test_Neptulon(self):
        game = generate_game_for([TheCoin, TheCoin, TheCoin, TheCoin, TheCoin, TheCoin, TheCoin, TheCoin, TheCoin,
                                  Neptulon], Wisp, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[0].hand))

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual("Siltfin Spiritwalker", game.players[0].hand[0].name)
        self.assertEqual("Murloc Tidecaller", game.players[0].hand[1].name)
        self.assertEqual("Grimscale Oracle", game.players[0].hand[2].name)
        self.assertEqual("Coldlight Seer", game.players[0].hand[3].name)

    def test_AncestorsCall(self):
        game = generate_game_for([AncestorsCall, StonetuskBoar], [Doomguard, Soulfire],
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(6):
            game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Stonetusk Boar", game.current_player.minions[0].card.name)
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Doomguard", game.other_player.minions[0].card.name)
        self.assertEqual(5, len(game.current_player.hand))
        self.assertEqual(7, len(game.other_player.hand))

    def test_LavaShock(self):
        game = generate_game_for([Doomhammer, LightningBolt, LavaShock], StonetuskBoar,
                                 CardTestingAgent, DoNothingAgent)
        for turn in range(11):
            game.play_single_turn()

        # The player should have been able to do everything AND have three mana left over
        self.assertEqual(25, game.other_player.hero.health)
        self.assertEqual(3, game.current_player.mana)

    def test_FireguardDestroyer(self):
        game = generate_game_for(FireguardDestroyer, Wisp, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual(6, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(6, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(7, len(game.players[0].minions))  # Well, I was trying to get a 7/6 but no luck
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)
