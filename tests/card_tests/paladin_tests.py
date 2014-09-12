import random
import unittest

from hearthbreaker.agents.basic_agents import PredictableBot, DoNothingBot
from tests.agents.testing_agents import MinionPlayingAgent, SpellTestingAgent, EnemyMinionSpellTestingAgent, \
    PredictableAgentWithoutHeroPower
from tests.testing_utils import generate_game_for
from hearthbreaker.replay import SavedGame
from hearthbreaker.cards import *


class TestPaladin(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_AvengingWrath(self):
        game = generate_game_for(MogushanWarden, AvengingWrath, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        # The random numbers work so that Avenging Wrath hits the player once, first minion once,
        # second minion four times and third minion two times (total of eight hits)
        self.assertEqual(29, game.other_player.hero.health)
        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual("Mogu'shan Warden", game.other_player.minions[0].card.name)
        self.assertEqual("Mogu'shan Warden", game.other_player.minions[1].card.name)
        self.assertEqual("Mogu'shan Warden", game.other_player.minions[2].card.name)
        self.assertEqual(6, game.other_player.minions[0].health)
        self.assertEqual(3, game.other_player.minions[1].health)
        self.assertEqual(5, game.other_player.minions[2].health)

    def test_BlessedChampion(self):
        game = generate_game_for(BlessedChampion, StonetuskBoar, EnemyMinionSpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(2, game.other_player.minions[0].calculate_attack())
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].calculate_max_health())

        # Test that this spell is being silenced properly as well
        game.other_player.minions[0].silence()
        self.assertEqual(1, game.other_player.minions[0].calculate_attack())
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].calculate_max_health())

    def test_BlessingOfKings(self):
        game = generate_game_for(BlessingOfKings, StonetuskBoar, EnemyMinionSpellTestingAgent, MinionPlayingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(5, game.other_player.minions[0].calculate_attack())
        self.assertEqual(5, game.other_player.minions[0].health)
        self.assertEqual(5, game.other_player.minions[0].calculate_max_health())

        # Test that this spell is being silenced properly as well
        game.other_player.minions[0].silence()
        self.assertEqual(1, game.other_player.minions[0].calculate_attack())
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].calculate_max_health())

    def test_BlessingOfMight(self):
        game = generate_game_for(StonetuskBoar, BlessingOfMight, MinionPlayingAgent, EnemyMinionSpellTestingAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(4, game.other_player.minions[0].calculate_attack())
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].calculate_max_health())

        # Test that this spell is being silenced properly as well
        game.other_player.minions[0].silence()
        self.assertEqual(1, game.other_player.minions[0].calculate_attack())
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].calculate_max_health())

    def test_BlessingOfWisdom(self):
        game = SavedGame("tests/replays/card_tests/BlessingOfWisdom.rep")
        game.start()
        self.assertEqual(3, len(game.current_player.minions))
        # 7 cards have been drawn.
        # 3 for starting first, 3 for new turn and 1 for minion attack with Blessing of Wisdom
        # (the second minion who had it got silenced)
        self.assertEqual(23, game.other_player.deck.left)

    def test_Consecration(self):
        game = generate_game_for(StonetuskBoar, Consecration, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(4, len(game.players[0].minions))
        game.play_single_turn()
        self.assertEqual(28, game.players[0].hero.health)
        self.assertEqual(0, len(game.players[0].minions))

    def test_DivineFavor(self):
        game = generate_game_for(StonetuskBoar, DivineFavor, DoNothingBot, SpellTestingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        # Cheat
        for cheat in range(0, 4):
            game.players[0].draw()

        self.assertEqual(10, len(game.players[0].hand))
        self.assertEqual(7, len(game.players[1].hand))
        game.play_single_turn()
        self.assertEqual(10, len(game.players[0].hand))
        self.assertEqual(10, len(game.players[1].hand))
        # The following test is if we have 10 cards in hand already.
        # Casting Divine Favor should count as being down to 9 again, and then draw a 10th card
        game.play_single_turn()
        self.assertEqual(10, len(game.players[0].hand))
        self.assertEqual(10, len(game.players[1].hand))
        game.play_single_turn()
        # New turn, p2 draws a card that is discarded (10), cast Divine Favor (9), draws a new card (10)
        self.assertEqual(10, len(game.players[0].hand))
        self.assertEqual(10, len(game.players[1].hand))

    def test_Equality(self):
        game = generate_game_for(MogushanWarden, Equality, MinionPlayingAgent, SpellTestingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(6, len(game.players[1].hand))
        game.play_single_turn()
        # SpellTestingAgent should draw a card, have 2 mana and try to cast Equality,
        # which it shouldn't be able to do (no minions), so hand should be 6
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(7, len(game.players[1].hand))

        for turn in range(0, 3):
            game.play_single_turn()

        # Make sure there's a minion on the playfield
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(7, game.players[0].minions[0].health)
        self.assertEqual(7, game.players[0].minions[0].calculate_max_health())
        game.play_single_turn()  # Equality should be played this turn
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[0].calculate_max_health())
        # Test it again to make sure the minion stays at 1 health
        game.play_single_turn()  # A new minion should be played
        game.play_single_turn()  # And Equality should be played here
        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[0].calculate_max_health())
        self.assertEqual(1, game.players[0].minions[1].health)
        self.assertEqual(1, game.players[0].minions[1].calculate_max_health())
        # Test to ensure that silencing works correctly
        game.players[0].minions[0].silence()
        self.assertEqual(7, game.players[0].minions[0].health)
        self.assertEqual(7, game.players[0].minions[0].calculate_max_health())

    def test_HammerOfWrath(self):
        game = generate_game_for(MogushanWarden, HammerOfWrath, DoNothingBot, SpellTestingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(8, len(game.players[1].hand))
        game.play_single_turn()  # Hammer of Wrath should be played
        self.assertEqual(27, game.players[0].hero.health)
        self.assertEqual(9, len(game.players[1].hand))

    def test_HandOfProtection(self):
        game = generate_game_for(StonetuskBoar, HandOfProtection, MinionPlayingAgent, SpellTestingAgent)

        game.play_single_turn()  # Stonetusk Boar should be played
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[0].card.name)
        self.assertFalse(game.players[0].minions[0].divine_shield)
        game.play_single_turn()
        # Hand of Protection should be played here, and the only available target should be the enemy minion
        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Stonetusk Boar", game.players[0].minions[0].card.name)
        self.assertTrue(game.players[0].minions[0].divine_shield)

    def test_HolyLight(self):
        game = generate_game_for(StonetuskBoar, HolyLight, DoNothingBot, SpellTestingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        game.players[0].hero.health = 20
        game.play_single_turn()  # Holy Light should be played
        self.assertEqual(26, game.players[0].hero.health)
        game.play_single_turn()
        game.play_single_turn()  # Holy Light should be played
        self.assertEqual(30, game.players[0].hero.health)

    def test_HolyWrath(self):
        game = generate_game_for(StonetuskBoar, HolyWrath, DoNothingBot, SpellTestingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(30, game.players[0].hero.health)
        game.play_single_turn()
        # Holy Wrath should be played that will draw Holy Wrath that costs 5 mana, thus dealing 5 damage
        self.assertEqual(25, game.players[0].hero.health)

    def test_Humility(self):
        game = generate_game_for(BloodfenRaptor, Humility, MinionPlayingAgent, SpellTestingAgent)

        game.play_single_turn()
        game.play_single_turn()  # No targets for Humility
        game.play_single_turn()  # Bloodfen Raptor should be played
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Bloodfen Raptor", game.players[0].minions[0].card.name)
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)
        game.play_single_turn()  # Humility should be played, and target the enemy Bloodfen Raptor
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Bloodfen Raptor", game.players[0].minions[0].card.name)
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(2, game.players[0].minions[0].health)

    def test_LayOnHands(self):
        game = generate_game_for(StonetuskBoar, LayOnHands, DoNothingBot, SpellTestingAgent)

        for turn in range(0, 15):
            game.play_single_turn()

        game.players[0].hero.health = 20
        # Put back some cards from hand, for testing purpose
        for putback in range(0, 4):
            game.players[1].put_back(game.players[1].hand[0])
        game.players[1].put_back(game.players[1].hand[1])
        self.assertEqual(5, len(game.players[1].hand))
        game.play_single_turn()  # Lay on Hands should be played
        self.assertEqual(28, game.players[0].hero.health)
        self.assertEqual(7, len(game.players[1].hand))
        game.play_single_turn()
        game.play_single_turn()  # Lay on Hands should be played, and a card be discarded since we have 8 already
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(10, len(game.players[1].hand))

    def test_AldorPeacekeeper(self):
        game = generate_game_for(AldorPeacekeeper, BloodfenRaptor, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[1].minions[0].health)
        self.assertEqual(3, game.players[1].minions[0].calculate_attack())
        self.assertEqual("Bloodfen Raptor", game.players[1].minions[0].card.name)
        game.play_single_turn()  # Aldor Peacekeeper should be played
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(2, game.players[1].minions[0].health)
        self.assertEqual(1, game.players[1].minions[0].calculate_attack())
        self.assertEqual("Bloodfen Raptor", game.players[1].minions[0].card.name)
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertEqual(3, game.players[0].minions[0].calculate_attack())
        self.assertEqual("Aldor Peacekeeper", game.players[0].minions[0].card.name)
        game.players[1].minions[0].silence()
        self.assertEqual(2, game.players[1].minions[0].health)
        self.assertEqual(3, game.players[1].minions[0].calculate_attack())

    def test_ArgentProtector(self):
        game = generate_game_for(ArgentProtector, BloodfenRaptor, MinionPlayingAgent, MinionPlayingAgent)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        game.play_single_turn()  # Argent Protector should be played
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Argent Protector", game.players[0].minions[0].card.name)
        self.assertFalse(game.players[0].minions[0].divine_shield)
        game.play_single_turn()
        game.play_single_turn()  # Argent Protector should be played, and the previous AP should get Divine Shield
        self.assertEqual(2, len(game.players[0].minions))
        self.assertTrue(game.players[0].minions[1].divine_shield)
        game.players[0].minions[1].silence()
        self.assertFalse(game.players[0].minions[1].divine_shield)

    def test_GuardianOfKings(self):
        game = generate_game_for(GuardianOfKings, BloodfenRaptor, MinionPlayingAgent, DoNothingBot)
        for turn in range(0, 12):
            game.play_single_turn()

        game.players[0].hero.health = 20

        self.assertEqual(0, len(game.players[0].minions))
        game.play_single_turn()  # Guardian of Kings should be played
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual("Guardian of Kings", game.players[0].minions[0].card.name)
        self.assertEqual(26, game.players[0].hero.health)

    def test_EyeForAnEye(self):
        game = generate_game_for(EyeForAnEye, StonetuskBoar, SpellTestingAgent, PredictableBot)

        game.play_single_turn()  # Eye for an Eye should be played
        self.assertEqual(1, len(game.players[0].secrets))
        self.assertEqual("Eye for an Eye", game.players[0].secrets[0].name)
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()
        # Attack with Stonetusk should happen, and the secret should trigger, making both players take 1 damage.
        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(28, game.players[0].hero.health)
        self.assertEqual(29, game.players[1].hero.health)

    def test_NobleSacrifice(self):
        game = generate_game_for(NobleSacrifice, StonetuskBoar, SpellTestingAgent, PredictableBot)

        game.play_single_turn()  # NobleSacrifice should be played
        self.assertEqual(1, len(game.players[0].secrets))
        self.assertEqual("Noble Sacrifice", game.players[0].secrets[0].name)

        game.play_single_turn()
        # Attack with Stonetusk should happen, and the secret should trigger. Both minions should die.
        # One boar is left (after being summoned after the coin)
        self.assertEqual(0, len(game.players[0].secrets))
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(29, game.players[0].hero.health)

        # Test with 7 minions
        game = SavedGame("tests/replays/card_tests/NobleSacrifice.rep")
        game.start()
        self.assertEqual(7, len(game.players[0].minions))
        self.assertEqual(29, game.players[0].hero.health)
        self.assertEqual(1, len(game.players[0].secrets))
        self.assertEqual("Noble Sacrifice", game.players[0].secrets[0].name)

    def test_Redemption(self):
        game = generate_game_for([Redemption, SilvermoonGuardian], WarGolem, SpellTestingAgent, PredictableBot)

        # Redemption and Silvermoon Guardian should be played
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].secrets))
        self.assertEqual("Redemption", game.players[0].secrets[0].name)
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_max_health())
        self.assertEqual(3, game.players[0].minions[0].health)
        self.assertTrue(game.players[0].minions[0].divine_shield)

        # Mage hero power should have been used
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].secrets))
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_max_health())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertFalse(game.players[0].minions[0].divine_shield)

        game.play_single_turn()
        # Silvermoon Guardian should be killed by the mage hero power, that will trigger the secret
        self.assertEqual(0, len(game.players[0].secrets))
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(3, game.players[0].minions[0].calculate_max_health())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertTrue(game.players[0].minions[0].divine_shield)

    def test_RedemptionEnemy(self):
        game = generate_game_for([Redemption, Whirlwind], StonetuskBoar, SpellTestingAgent, PredictableBot)
        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(2, len(game.players[1].minions))
        self.assertEqual(1, len(game.players[0].secrets))

        game.play_single_turn()

        self.assertEqual(0, len(game.players[1].minions))
        self.assertEqual(1, len(game.players[0].secrets))

    def test_Repentance(self):
        game = generate_game_for(Repentance, TwilightDrake, SpellTestingAgent, MinionPlayingAgent)

        # Repentance should be played
        game.play_single_turn()
        self.assertEqual(1, len(game.players[0].secrets))
        self.assertEqual("Repentance", game.players[0].secrets[0].name)

        # Twilight Drake (4 attack / 1 health) should be played, gaining lots of health due to its battlecry,
        # and the secret should activate afterwards and reduced the minions health to 1
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(0, len(game.players[0].secrets))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].calculate_max_health())
        self.assertEqual(1, game.players[1].minions[0].health)

    def test_RepentanceSelf(self):
        game = generate_game_for([Repentance, BluegillWarrior], TwilightDrake, SpellTestingAgent, DoNothingBot)
        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].secrets))
        self.assertEqual(1, len(game.players[0].minions))

    def test_LightsJustice(self):
        game = generate_game_for(LightsJustice, StonetuskBoar, PredictableBot, DoNothingBot)

        # Light's Justice should be played
        game.play_single_turn()
        self.assertEqual(1, game.players[0].hero.weapon.base_attack)
        self.assertEqual(4, game.players[0].hero.weapon.durability)

    def test_SwordOfJustice(self):
        game = generate_game_for([SwordOfJustice, MagmaRager, MagmaRager, MagmaRager, MagmaRager, MagmaRager],
                                 StonetuskBoar, MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 4):
            game.play_single_turn()

        # Sword of Justice should be played, and hero will attack once
        game.play_single_turn()
        self.assertEqual(1, game.players[0].hero.weapon.base_attack)
        self.assertEqual(5, game.players[0].hero.weapon.durability)

        # Four minions should have been played, buffing each one
        for turn in range(0, 9):
            game.play_single_turn()
        self.assertEqual(1, game.players[0].hero.weapon.durability)
        self.assertEqual(4, len(game.players[0].minions))
        for i in range(0, 4):
            self.assertEqual(2, game.players[0].minions[i].calculate_max_health())
            self.assertEqual(2, game.players[0].minions[i].health)
            self.assertEqual(6, game.players[0].minions[i].calculate_attack())

        # A fifth minion should be played, buffed by the last durability of the weapon which should be destroyed
        game.play_single_turn()
        self.assertEqual(None, game.players[0].hero.weapon)
        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].minions[0].calculate_max_health())
        self.assertEqual(2, game.players[0].minions[0].health)
        self.assertEqual(6, game.players[0].minions[0].calculate_attack())

        game.players[0].minions[0].silence()
        self.assertEqual(1, game.players[0].minions[0].calculate_max_health())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(5, game.players[0].minions[0].calculate_attack())

    def test_TruesilverChampion(self):
        game = generate_game_for([TruesilverChampion, MindControl], StonetuskBoar, PredictableAgentWithoutHeroPower,
                                 MinionPlayingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        game.players[0].hero.health = 20
        # Truesilver Champion should be played, and hero will attack once, healing by two but get one damage from boar
        game.play_single_turn()
        self.assertEqual(4, game.players[0].hero.weapon.base_attack)
        self.assertEqual(1, game.players[0].hero.weapon.durability)
        self.assertEqual(21, game.players[0].hero.health)

        game.play_single_turn()
        game.play_single_turn()  # Attacks, breaking the Truesilver

    def test_TirionFordring(self):
        game = generate_game_for(TirionFordring, StonetuskBoar, MinionPlayingAgent, DoNothingBot)

        # Tirion Fordring should be played
        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(6, game.players[0].minions[0].calculate_attack())
        self.assertEqual(6, game.players[0].minions[0].health)
        self.assertEqual("Tirion Fordring", game.players[0].minions[0].card.name)
        self.assertEqual(None, game.players[0].hero.weapon)

        # Let Tirion Fordring die, and a weapon should be equiped
        tirion = game.players[0].minions[0]
        tirion.die(None)
        tirion.activate_delayed()
        self.assertEqual(5, game.players[0].hero.weapon.base_attack)
        self.assertEqual(3, game.players[0].hero.weapon.durability)

    def test_Avenge(self):
        game = generate_game_for([Avenge, StonetuskBoar, StonetuskBoar], Frostbolt,
                                 SpellTestingAgent, SpellTestingAgent)

        for turn in range(0, 3):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(1, game.current_player.minions[1].calculate_max_health())

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(4, game.other_player.minions[0].calculate_attack())
        self.assertEqual(3, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(0, len(game.other_player.secrets))

    def test_AvengewithAoE(self):
        game = generate_game_for(Flamestrike, [Avenge, Shieldbearer, IronfurGrizzly, Deathwing],
                                 MinionPlayingAgent, MinionPlayingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))

        # The Flamestrike should kill both minions.  If one dies, then the other should not be buffed.  If one is
        # buffed before Flamestroke completes, then it will survive, which should not happen.

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(1, len(game.other_player.secrets))
