import random
import unittest

from hearthbreaker.agents.basic_agents import DoNothingBot
from tests.agents.testing_agents import MinionPlayingAgent, PredictableAgentWithoutHeroPower, SpellTestingAgent, \
    OneSpellTestingAgent, SelfSpellTestingAgent
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *


class TestWarrior(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_ArathiWeaponsmith(self):
        game = generate_game_for(ArathiWeaponsmith, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        # Arathi Weaponsmith should be played
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual("Arathi Weaponsmith", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].hero.weapon.base_attack)
        self.assertEqual(2, game.players[0].hero.weapon.durability)

    def test_Armorsmith(self):
        game = generate_game_for(Armorsmith, StonetuskBoar, MinionPlayingAgent, PredictableAgentWithoutHeroPower)

        # Armorsmith should be played
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual("Armorsmith", game.players[0].minions[0].card.name)
        self.assertEqual(0, game.players[0].hero.armor)

        # Three Stonetusks should attack, generating one armor each
        game.play_single_turn()
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].hero.armor)

    def test_CruelTaskmaster(self):
        game = generate_game_for(CruelTaskmaster, Shieldbearer, MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(0, game.players[1].minions[0].calculate_attack())
        self.assertEqual(4, game.players[1].minions[0].health)

        # Cruel Taskmaster should be played, targeting the Shieldbearer
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual("Cruel Taskmaster", game.players[0].minions[0].card.name)
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[1].minions[0].calculate_attack())
        self.assertEqual(3, game.players[1].minions[0].health)

    def test_FrothingBerserker(self):
        game = generate_game_for(FrothingBerserker, AngryChicken, MinionPlayingAgent, PredictableAgentWithoutHeroPower)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(3, len(game.players[1].minions))

        # Frothing Berserker should be played
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual("Frothing Berserker", game.players[0].minions[0].card.name)

        # Three chickens should attack, generating a total of +6 attack for the Frothing Berserker
        game.play_single_turn()
        self.assertEqual(8, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)

    def test_GrommashHellscream(self):
        game = generate_game_for(GrommashHellscream, ExplosiveTrap, PredictableAgentWithoutHeroPower, SpellTestingAgent)

        for turn in range(0, 14):
            game.play_single_turn()

        # Hellscream should be played, attacking (charge) and getting 2 damage by trap that will trigger enrage,
        # dealing 10 damage as result
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(10, game.players[0].minions[0].calculate_attack())
        self.assertEqual(7, game.players[0].minions[0].health)
        self.assertEqual(20, game.players[1].hero.health)

        game.players[0].minions[0].heal(2, None)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        game.players[0].minions[0].damage(2, None)
        self.assertEqual(10, game.players[0].minions[0].calculate_attack())

        game.players[0].minions[0].silence()
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        game.players[0].minions[0].heal(2, None)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        game.players[0].minions[0].damage(2, None)
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())

    def test_KorkronElite(self):
        game = generate_game_for(KorkronElite, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)

        for turn in range(0, 6):
            game.play_single_turn()

        # Kor'kron Elite should be played and attack (charge)
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(26, game.players[1].hero.health)

    def test_WarsongCommander(self):
        game = generate_game_for(WarsongCommander, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)

        # Super special test cases - http://www.hearthhead.com/card=1009/warsong-commander#comments:id=1935295
        game.players[0].mana = 100

        # Play the Warsong Commander
        commander = WarsongCommander()
        commander.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[0].charge)  # Should not give charge to itself

        # Test so that enrage doesn't remove the charge
        worgen = RagingWorgen()
        worgen.use(game.players[0], game)
        game.players[0].minions[0].damage(1, None)  # Trigger enrage, charge should still be active
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertTrue(game.players[0].minions[0].charge)

        # Test so that charge gets applied before a battlecry
        weapon = FieryWarAxe().create_weapon(game.players[0])
        weapon.equip(game.players[0])
        self.assertEqual(3, game.players[0].hero.weapon.base_attack)
        self.assertEqual(2, game.players[0].hero.weapon.durability)
        bloodsail = BloodsailRaider()
        bloodsail.use(game.players[0], game)  # Should gain charge first, then 4 attack from weapon
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertTrue(game.players[0].minions[0].charge)

        # TODO: Test with Faceless Manipulator here

        # Remove the Warsong Commander
        game.players[0].minions[-1].die(None)
        game.check_delayed()
        # The previous charged minions should still have charge
        self.assertTrue(game.players[0].minions[0].charge)
        self.assertTrue(game.players[0].minions[-1].charge)

        # Test so that a minion played before Warsong doesn't get charge
        shield = Shieldbearer()
        shield.summon(game.players[0], game, 0)
        self.assertFalse(game.players[0].minions[0].charge)
        commander.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[1].charge)
        # Remove the Warsong again
        game.players[0].minions[0].die(None)
        game.players[0].minions[0].activate_delayed()
        # Buff a minion to above 3
        game.players[0].minions[0].change_attack(5)
        # Play Warsong, the buffed minion should not get charge
        commander.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[1].charge)

        # Auras!
        stormwind = StormwindChampion()
        stormwind.use(game.players[0], game)
        self.assertEqual(3, game.players[0].minions[1].calculate_attack())
        self.assertEqual(4, game.players[0].minions[1].health)
        # Kill the worgen
        game.players[0].minions[-1].die(None)
        game.players[0].minions[-1].activate_delayed()
        # And play it again. It should get the aura FIRST, making it a 4/4 minion, and thus DOES NOT gain charge!
        worgen.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[0].charge)

    def test_BattleRage(self):
        game = generate_game_for(BattleRage, StonetuskBoar, SpellTestingAgent, DoNothingBot)

        game.players[0].mana = 100

        shield = Shieldbearer()
        shield.use(game.players[0], game)
        shield.use(game.players[0], game)
        shield.use(game.players[0], game)
        game.players[0].minions[0].damage(1, None)
        game.players[0].minions[1].damage(1, None)
        game.players[0].hero.damage(1, None)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(4, len(game.players[0].hand))

        # Battle Rage should be played, 3 damaged characters = 3 cards drawn
        game.play_single_turn()
        self.assertEqual(7, len(game.players[0].hand))

    def test_Brawl(self):
        game = generate_game_for(Brawl, StonetuskBoar, SpellTestingAgent, DoNothingBot)

        game.players[0].mana = 100

        shield = Shieldbearer()
        shield.use(game.players[0], game)
        shield.use(game.players[0], game)
        golem = HarvestGolem()
        golem.use(game.players[0], game)
        shield.use(game.players[1], game)
        shield.use(game.players[1], game)
        shield.use(game.players[1], game)

        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))

        # Brawl should be played, leaving one minion behind and Damaged Golem should have spawned for first player
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Damaged Golem", game.players[0].minions[0].card.name)
        self.assertEqual(1, len(game.players[1].minions))

    def test_Charge(self):
        game = generate_game_for([Shieldbearer, Charge], StonetuskBoar, SpellTestingAgent, DoNothingBot)
        game.players[0].agent.play_on = 4

        for turn in range(0, 6):
            game.play_single_turn()

        # Shieldbearer and Charge should be played
        game.play_single_turn()
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertTrue(game.players[0].minions[0].charge)

    def test_Cleave(self):
        game = generate_game_for(Cleave, SenjinShieldmasta, OneSpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(8, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(5, game.players[1].minions[0].health)
        self.assertEqual(5, game.players[1].minions[1].health)

        # 2 enemy minions are now in play, so Cleave should be played
        game.play_single_turn()
        self.assertEqual(8, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(3, game.players[1].minions[0].health)
        self.assertEqual(3, game.players[1].minions[1].health)

    def test_WhirlwindExecute(self):
        game = generate_game_for(Execute, [GoldshireFootman, Whirlwind], SpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].health)

        game.play_single_turn()

        self.assertEqual(0, len(game.players[1].minions))

    def test_HeroicStrike(self):
        game = generate_game_for(HeroicStrike, StonetuskBoar, PredictableAgentWithoutHeroPower, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(26, game.players[1].hero.health)

    def test_InnerRageRampage(self):
        game = generate_game_for([InnerRage, Rampage], GoldshireFootman, OneSpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(2, game.players[1].minions[0].health)
        self.assertEqual(3, game.players[1].minions[1].calculate_attack())
        self.assertEqual(1, game.players[1].minions[1].health)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(2, game.players[1].minions[0].health)
        self.assertEqual(6, game.players[1].minions[1].calculate_attack())
        self.assertEqual(4, game.players[1].minions[1].health)

    def test_ShieldBlockShieldSlam(self):
        game = generate_game_for([ShieldBlock, ShieldSlam], Doomsayer, OneSpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(6, len(game.players[0].hand))
        self.assertEqual(5, game.players[0].hero.armor)
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(7, game.players[1].minions[0].health)

        game.play_single_turn()

        self.assertEqual(5, game.players[0].hero.armor)
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[1].minions[0].health)

    def test_Slam(self):
        game = generate_game_for(Slam, [GoldshireFootman, Doomsayer], OneSpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()  # Slam to kill Footman, no draw

        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].minions))

        game.play_single_turn()  # Slam and Doomsayer survives

        self.assertEqual(5, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].minions))

    def test_Upgrade(self):
        game = generate_game_for(Upgrade, StonetuskBoar, OneSpellTestingAgent, DoNothingBot)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].hero.weapon.base_attack)
        self.assertEqual(3, game.players[0].hero.weapon.durability)

        game.play_single_turn()

        self.assertEqual(2, game.players[0].hero.weapon.base_attack)
        self.assertEqual(4, game.players[0].hero.weapon.durability)

    def test_MortalStrike(self):
        game = generate_game_for(MortalStrike, StonetuskBoar, SelfSpellTestingAgent, DoNothingBot)
        game.players[0].hero.health = 14
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(10, game.players[0].hero.health)

        game.play_single_turn()

        self.assertEqual(4, game.players[0].hero.health)

    def test_CommandingShout(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, StonetuskBoar,
                                  StonetuskBoar, StonetuskBoar, CommandingShout], Abomination,
                                 PredictableAgentWithoutHeroPower, MinionPlayingAgent)
        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))

    def test_Gorehowl(self):
        game = generate_game_for(Gorehowl, [BoulderfistOgre, Deathwing],
                                 PredictableAgentWithoutHeroPower, SpellTestingAgent)

        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(1, game.current_player.hero.weapon.durability)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(23, game.other_player.hero.health)
        self.assertIsNone(game.current_player.hero.weapon)

    def test_FieryWarAxe(self):
        game = generate_game_for(FieryWarAxe, BoulderfistOgre,
                                 PredictableAgentWithoutHeroPower, DoNothingBot)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, game.current_player.hero.weapon.durability)
        self.assertEqual(3, game.current_player.hero.weapon.base_attack)
        self.assertEqual(27, game.other_player.hero.health)

    def test_DeathsBite(self):
        game = generate_game_for([IronfurGrizzly, DeathsBite], Deathlord,
                                 PredictableAgentWithoutHeroPower, MinionPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertIsNotNone(game.current_player.hero.weapon)
        self.assertEqual(1, game.other_player.minions[0].health)

        game.play_single_turn()
        game.play_single_turn()

        # The Death's Bite attacks the new Deathlord, triggering the weapon's deathrattle
        # This finishes off the other deathlord and the first friendly Grizzly
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(3, game.other_player.minions[0].health)
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[1].health)
