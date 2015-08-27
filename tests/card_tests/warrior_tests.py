import random
import unittest

from hearthbreaker.agents.basic_agents import DoNothingAgent, PredictableAgent
from tests.agents.testing_agents import OneCardPlayingAgent, PlayAndAttackAgent, CardTestingAgent,\
    SelfSpellTestingAgent, EnemyMinionSpellTestingAgent
from tests.testing_utils import generate_game_for
from hearthbreaker.cards import *


class TestWarrior(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_ArathiWeaponsmith(self):
        game = generate_game_for(ArathiWeaponsmith, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        # Arathi Weaponsmith should be played
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual("Arathi Weaponsmith", game.players[0].minions[0].card.name)
        self.assertEqual(2, game.players[0].weapon.base_attack)
        self.assertEqual(2, game.players[0].weapon.durability)

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

        # Three Stonetusks should attack, generating one armor each
        game.play_single_turn()
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].hero.armor)

    def test_CruelTaskmaster(self):
        game = generate_game_for(CruelTaskmaster, Shieldbearer, OneCardPlayingAgent, OneCardPlayingAgent)

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

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].calculate_attack())
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertEqual(2, game.players[1].minions[0].calculate_attack())
        self.assertEqual(3, game.players[1].minions[0].health)
        self.assertEqual(2, game.players[1].minions[1].calculate_attack())
        self.assertEqual(3, game.players[1].minions[1].health)

    def test_FrothingBerserker(self):
        game = generate_game_for(FrothingBerserker, AngryChicken, OneCardPlayingAgent, PlayAndAttackAgent)

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
        game = generate_game_for(GrommashHellscream, ExplosiveTrap, PlayAndAttackAgent, CardTestingAgent)

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
        game = generate_game_for(KorkronElite, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        # Kor'kron Elite should be played and attack (charge)
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(26, game.players[1].hero.health)

    def test_WarsongCommander(self):
        game = generate_game_for(WarsongCommander, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)

        # Super special test cases - http://www.hearthhead.com/card=1009/warsong-commander#comments:id=1935295
        game.players[0].mana = 100

        # Play the Warsong Commander
        commander = WarsongCommander()
        commander.player = game.players[0]
        commander.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[0].charge())  # Should not give charge to itself

        # Test so that enrage doesn't remove the charge
        worgen = RagingWorgen()
        worgen.player = game.players[0]
        worgen.use(game.players[0], game)
        game.players[0].minions[0].damage(1, None)  # Trigger enrage, charge should still be active
        self.assertEqual(4, game.players[0].minions[0].calculate_attack())
        self.assertTrue(game.players[0].minions[0].charge())

        # Test so that charge gets applied before a battlecry
        weapon = FieryWarAxe().create_weapon(game.players[0])
        weapon.equip(game.players[0])
        self.assertEqual(3, game.players[0].weapon.base_attack)
        self.assertEqual(2, game.players[0].weapon.durability)
        bloodsail = BloodsailRaider()
        bloodsail.player = game.players[0]
        bloodsail.use(game.players[0], game)  # Should gain charge first, then 4 attack from weapon
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())
        self.assertTrue(game.players[0].minions[0].charge())

        # TODO: Test with Faceless Manipulator here

        # Remove the Warsong Commander
        game.players[0].minions[-1].die(None)
        game.check_delayed()
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
        # And play it again. It should get the aura FIRST, making it a 4/4 minion, and thus DOES NOT gain charge!
        worgen.use(game.players[0], game)
        self.assertFalse(game.players[0].minions[0].charge())

        # Minions summoned by other minions
        dragonling = DragonlingMechanic()
        dragonling.player = game.players[0]
        dragonling.use(game.players[0], game)
        self.assertTrue(game.players[0].minions[0].charge())
        self.assertEqual("Mechanical Dragonling", game.players[0].minions[1].card.name)
        self.assertTrue(game.players[0].minions[1].charge())
        # Kill them to make room
        game.players[0].minions[0].die(None)
        game.players[0].minions[0].activate_delayed()
        game.players[0].minions[0].die(None)
        game.players[0].minions[0].activate_delayed()
        creeper = HauntedCreeper()
        creeper.player = game.players[0]
        creeper.use(game.players[0], game)
        self.assertTrue(game.players[0].minions[0].charge())
        game.players[0].minions[0].die(None)
        game.players[0].minions[0].activate_delayed()
        game.check_delayed()
        self.assertEqual("Spectral Spider", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].charge())

    def test_BattleRage(self):
        game = generate_game_for(BattleRage, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        game.players[0].mana = 100

        shield = Shieldbearer()
        shield.player = game.players[0]
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
        game = generate_game_for(Brawl, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        game.players[0].mana = 100

        shield = Shieldbearer()
        shield.player = game.players[0]
        shield.use(game.players[0], game)
        shield.use(game.players[0], game)
        golem = HarvestGolem()
        golem.player = game.players[0]
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
        game = generate_game_for([Shieldbearer, Charge], StonetuskBoar, CardTestingAgent, DoNothingAgent)
        game.players[0].agent.play_on = 4

        for turn in range(0, 6):
            game.play_single_turn()

        # Shieldbearer and Charge should be played
        game.play_single_turn()
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertTrue(game.players[0].minions[0].charge())

    def test_Cleave(self):
        game = generate_game_for(Cleave, SenjinShieldmasta, OneCardPlayingAgent, OneCardPlayingAgent)

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
        game = generate_game_for(Execute, [GoldshireFootman, Whirlwind], CardTestingAgent, OneCardPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].health)

        game.play_single_turn()

        self.assertEqual(0, len(game.players[1].minions))

    def test_HeroicStrike(self):
        game = generate_game_for(HeroicStrike, StonetuskBoar, PlayAndAttackAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(26, game.players[1].hero.health)

    def test_InnerRageRampage(self):
        game = generate_game_for([InnerRage, Rampage], GoldshireFootman, OneCardPlayingAgent, OneCardPlayingAgent)

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
        game = generate_game_for([ShieldBlock, ShieldSlam], Doomsayer, OneCardPlayingAgent, OneCardPlayingAgent)

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
        game = generate_game_for(Slam, [GoldshireFootman, Doomsayer], OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()  # Slam to kill Footman, no draw

        self.assertEqual(4, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].minions))

        game.play_single_turn()  # Slam and Doomsayer survives

        self.assertEqual(5, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].minions))

    def test_Upgrade(self):
        game = generate_game_for(Upgrade, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, game.players[0].weapon.base_attack)
        self.assertEqual(3, game.players[0].weapon.durability)

        game.play_single_turn()

        self.assertEqual(2, game.players[0].weapon.base_attack)
        self.assertEqual(4, game.players[0].weapon.durability)

    def test_MortalStrike(self):
        game = generate_game_for(MortalStrike, StonetuskBoar, SelfSpellTestingAgent, DoNothingAgent)
        game.players[0].hero.health = 14
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(10, game.players[0].hero.health)

        game.play_single_turn()

        self.assertEqual(4, game.players[0].hero.health)

    def test_CommandingShout(self):
        game = generate_game_for([StonetuskBoar, StonetuskBoar, StonetuskBoar, StonetuskBoar,
                                  CommandingShout], UnstableGhoul,
                                 PlayAndAttackAgent, OneCardPlayingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Unstable Ghoul", game.current_player.minions[0].card.name)

        game.play_single_turn()
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.minions))

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(0, len(game.current_player.minions))

    def test_Gorehowl(self):
        game = generate_game_for([Gorehowl, Deathwing], [BoulderfistOgre, Deathwing],
                                 PlayAndAttackAgent, CardTestingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(7, game.players[1].minions[0].health)

        game.play_single_turn()

        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(1, game.players[0].weapon.durability)  # Gorehowl does not break from killing Boulderfist
        self.assertEqual(6, game.players[0].weapon.base_attack)  # But it does lose 1 attack
        self.assertEqual(24, game.players[0].hero.health)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertIsNone(game.players[0].weapon)  # Attacks face and weapon breaks
        self.assertEqual(24, game.players[0].hero.health)
        self.assertEqual(24, game.players[1].hero.health)

    def test_FieryWarAxe(self):
        game = generate_game_for(FieryWarAxe, BoulderfistOgre,
                                 PlayAndAttackAgent, DoNothingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, game.current_player.weapon.durability)
        self.assertEqual(3, game.current_player.weapon.base_attack)
        self.assertEqual(27, game.other_player.hero.health)

    def test_DeathsBite(self):
        game = generate_game_for([IronfurGrizzly, DeathsBite], Deathlord,
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertIsNotNone(game.current_player.weapon)
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

    def test_Warbot(self):
        game = generate_game_for(Warbot, StonetuskBoar, CardTestingAgent, PlayAndAttackAgent)

        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())

        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].calculate_attack())

    def test_BouncingBlades(self):
        game = generate_game_for([GoldshireFootman, EchoingOoze, BouncingBlade], [GoldshireFootman, EchoingOoze],
                                 CardTestingAgent, CardTestingAgent)

        for turn in range(4):
            game.play_single_turn()

        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(2, game.players[0].minions[1].health)
        self.assertEqual(2, game.players[0].minions[2].health)
        self.assertEqual(2, game.players[1].minions[0].health)
        self.assertEqual(2, game.players[1].minions[1].health)
        self.assertEqual(2, game.players[1].minions[2].health)

        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(3, len(game.players[1].minions))

        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].health)
        self.assertEqual(2, game.players[1].minions[0].health)
        self.assertEqual(2, game.players[1].minions[1].health)
        self.assertEqual(1, game.players[1].minions[2].health)

    def test_OgreWarmaul(self):
        game = generate_game_for(OgreWarmaul,
                                 [StonetuskBoar, GoldshireFootman, SilverbackPatriarch],
                                 PlayAndAttackAgent, OneCardPlayingAgent)

        for turn in range(5):
            game.play_single_turn()

        self.assertIsNotNone(game.current_player.weapon)

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Stonetusk Boar", game.other_player.minions[0].card.name)
        self.assertEqual(30, game.other_player.hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual("Silverback Patriarch", game.other_player.minions[0].card.name)
        self.assertEqual(30, game.other_player.hero.health)

    def test_SiegeEngine(self):
        game = generate_game_for(SiegeEngine, StonetuskBoar, PredictableAgent, DoNothingAgent)

        # Arathi Weaponsmith should be played
        for turn in range(0, 13):
            game.play_single_turn()

        self.assertEqual(12, game.players[0].hero.armor)
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[-1].calculate_attack())
        self.assertEqual(5, game.players[0].minions[-1].health)
        self.assertEqual("Siege Engine", game.players[0].minions[0].card.name)

        # Hero Power will be used, triggering the Siege Engine
        for turn in range(0, 2):
            game.play_single_turn()
        self.assertEqual(14, game.players[0].hero.armor)
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(6, game.players[0].minions[-1].calculate_attack())
        self.assertEqual(5, game.players[0].minions[-1].health)

    def test_Crush(self):
        game = generate_game_for([Crush, ChillwindYeti], DreadInfernal, EnemyMinionSpellTestingAgent,
                                 CardTestingAgent)

        # Player 2 plays a Dread Infernal
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))

        # Player 1 pays 7 mana to use Crush
        game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(0, game.players[0].mana)

        # Player 2 plays another Dread Infernal
        game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))

        # Player 1 plays Yeti, can't afford Crush
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))

        # Player 2 plays another Dread Infernal, damaging the Yeti
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(4, game.players[0].minions[-1].health)

        # Player 1 pays 3 mana to use Crush and 4 the play a 2nd Yeti
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[0].mana)

    def test_BurrowingMine(self):
        game = generate_game_for(BurrowingMine, StonetuskBoar, DoNothingAgent, DoNothingAgent)

        game.play_single_turn()
        self.assertEqual(0, game.current_player.hero.health)
        self.assertEqual(3, len(game.current_player.hand))
        self.assertEqual(0, game.current_player.deck.left)

    def test_IronJuggernaut(self):
        game = generate_game_for(IronJuggernaut, CircleOfHealing, OneCardPlayingAgent, PredictableAgent)
        for turn in range(11):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Iron Juggernaut", game.players[0].minions[0].card.name)

        found_mine = False
        for card in game.players[1].deck.cards:
            if card.name == "Burrowing Mine":
                found_mine = True

        self.assertTrue(found_mine, "Did not find the burrowing mine in the opponent's deck")

        # Will draw multiple mines in a row
        self.assertEqual(30, game.players[1].hero.health)
        for turn in range(43):
            game.play_single_turn()
        self.assertEqual(0, game.players[1].hero.health)

    def test_ScrewjankClunker(self):
        game = generate_game_for([Wisp, ScrewjankClunker, ScrewjankClunker], [Wisp, MoltenGiant],
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(8):
            game.play_single_turn()

        # Clunker cannot buff anything
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(1, game.players[1].minions[0].health)

        game.play_single_turn()

        # Clunker buffs previous Clunker
        self.assertEqual(3, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_attack())
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(4, game.players[0].minions[1].calculate_attack())
        self.assertEqual(7, game.players[0].minions[1].health)
        self.assertEqual(1, game.players[0].minions[2].calculate_attack())
        self.assertEqual(1, game.players[0].minions[2].health)
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual(1, game.players[1].minions[0].health)

    def test_AxeFlinger(self):
        game = generate_game_for(AxeFlinger, [MortalCoil, ShadowWordPain], OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()  # Mortal Coils the Axe Flinger

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(28, game.players[1].hero.health)

        game.play_single_turn()  # Plays 2nd Axe Flinger
        game.play_single_turn()  # Pains 1 Axe Flinger, no damage

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(28, game.players[1].hero.health)

    def test_Revenge(self):
        game = generate_game_for(SinisterStrike, [ChillwindYeti, Revenge, Revenge],
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(11):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(4, game.players[1].minions[0].health)  # 1st Revenge cast at 15 hp, so 1 damage
        self.assertEqual(12, game.players[1].hero.health)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].health)  # 2nd Revenge cast at 12 hp, so 3 damage
        self.assertEqual(12, game.players[1].hero.health)

    def test_AlextraszasChampion(self):
        game = generate_game_for([AlexstraszasChampion, AlexstraszasChampion, AlexstraszasChampion,
                                  AlexstraszasChampion, AlexstraszasChampion, Nefarian], StonetuskBoar,
                                 CardTestingAgent, DoNothingAgent)

        for turn in range(3):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertFalse(game.current_player.minions[0].charge())

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertTrue(game.current_player.minions[0].charge())
