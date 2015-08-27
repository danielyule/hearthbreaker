import random
import unittest

from hearthbreaker.agents.basic_agents import PredictableAgent, DoNothingAgent
from hearthbreaker.constants import CHARACTER_CLASS, MINION_TYPE
from hearthbreaker.engine import Game
from hearthbreaker.replay import playback, Replay
from tests.agents.testing_agents import CardTestingAgent, OneCardPlayingAgent, EnemySpellTestingAgent, \
    MinionAttackingAgent, PlayAndAttackAgent
from tests.testing_utils import generate_game_for, StackedDeck
from hearthbreaker.cards import *


class TestMage(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_ArcaneMissiles(self):
        game = generate_game_for(MogushanWarden, ArcaneMissiles, OneCardPlayingAgent, CardTestingAgent)

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
        # The random numbers work so that the arcane missiles hit thrice on each target
        self.assertEqual(9, game.other_player.hero.health)
        self.assertEqual(4, game.other_player.minions[0].health)

    def test_ArcaneMissilesWithSpellPower(self):
        game = playback(Replay("tests/replays/card_tests/ArcaneMissilesWithSpellDamage.hsreplay"))
        game.start()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(2, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(27, game.other_player.hero.health)

        return game

    def test_WaterElemental(self):
        game = generate_game_for(WaterElemental, StonetuskBoar, PredictableAgent, DoNothingAgent)

        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(25, game.other_player.hero.health)
        self.assertFalse(game.other_player.hero.frozen)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertEqual(6, game.current_player.minions[0].health)
        self.assertEqual("Water Elemental", game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(22, game.other_player.hero.health)

        # Always false after the end of a turn
        self.assertTrue(game.other_player.hero.frozen)

        # Now make sure that attacking the Water Elemental directly will freeze a character
        random.seed(1857)
        game = generate_game_for(WaterElemental, IronbarkProtector, OneCardPlayingAgent, PredictableAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(5, game.other_player.minions[0].health)
        # The player won't have taken damage because of armor, but should still be frozen
        self.assertEqual(30, game.current_player.hero.health)
        self.assertTrue(game.current_player.hero.frozen)

        game.play_single_turn()
        game.play_single_turn()

        # The player should still be frozen from last turn, and so shouldn't have attacked
        self.assertEqual(30, game.current_player.hero.health)

    def test_IceLance(self):
        game = generate_game_for(IceLance, OasisSnapjaw, CardTestingAgent, OneCardPlayingAgent)
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
        deck1 = StackedDeck([ManaWyrm(), IceLance(), ManaWyrm(), IceLance(), IceLance(), IceLance()],
                            CHARACTER_CLASS.MAGE)
        deck2 = StackedDeck([IronbeakOwl()], CHARACTER_CLASS.PALADIN)
        game = Game([deck1, deck2], [CardTestingAgent(), OneCardPlayingAgent()])
        game.pre_game()
        game.current_player = 1

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].calculate_max_health())
        self.assertEqual("Mana Wyrm", game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[1].health)
        self.assertEqual(3, game.current_player.minions[1].calculate_max_health())
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(5, game.current_player.minions[1].calculate_attack())
        self.assertEqual(3, game.current_player.minions[1].health)
        self.assertEqual(3, game.current_player.minions[1].calculate_max_health())

    def test_MirrorImage(self):
        game = generate_game_for(MirrorImage, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        game.play_single_turn()
        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(0, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual("Mirror Image", game.current_player.minions[0].card.name)
        self.assertEqual(0, game.current_player.minions[0].card.mana)

        self.assertEqual(0, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].health)
        self.assertTrue(game.current_player.minions[1].taunt)
        self.assertEqual("Mirror Image", game.current_player.minions[1].card.name)
        self.assertEqual(0, game.current_player.minions[1].card.mana)

    def test_ArcaneExplosion(self):
        game = generate_game_for(BloodfenRaptor, ArcaneExplosion, OneCardPlayingAgent, CardTestingAgent)

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
        game = generate_game_for(OasisSnapjaw, Frostbolt, OneCardPlayingAgent, CardTestingAgent)

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
        game = generate_game_for([SorcerersApprentice, ArcaneMissiles, SorcerersApprentice, Frostbolt, Frostbolt,
                                  Frostbolt], StonetuskBoar, CardTestingAgent, DoNothingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual("Sorcerer's Apprentice", game.current_player.minions[0].card.name)

        # Arcane missiles should also have been played, since it is now free
        self.assertEqual(27, game.other_player.hero.health)

        # Make sure the other frostbolts have been properly reduced
        self.assertEqual(1, game.current_player.hand[1].mana_cost())
        self.assertEqual(1, game.current_player.hand[2].mana_cost())

        game.play_single_turn()
        game.play_single_turn()

        # Both Sorcerer's Apprentices are killed by friendly Frostbolts.
        self.assertEqual(0, len(game.current_player.minions))

        # Make sure that the cards in hand are no longer reduced
        self.assertEqual(2, game.current_player.hand[0].mana_cost())

    def test_ArcaneIntellect(self):
        game = generate_game_for(ArcaneIntellect, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(7, len(game.current_player.hand))

    def test_FrostNova(self):
        game = generate_game_for(FrostNova, StonetuskBoar, CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        for minion in game.other_player.minions:
            self.assertTrue(minion.frozen)

        self.assertFalse(game.other_player.hero.frozen)

    def test_Counterspell(self):
        game = generate_game_for(Counterspell, Frostbolt, CardTestingAgent, CardTestingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Counterspell", game.current_player.secrets[0].name)

        game.play_single_turn()

        self.assertFalse(game.other_player.hero.frozen)
        self.assertEqual(27, game.other_player.hero.health)
        # Ensure that secrets are being removed after being revealed
        self.assertEqual(0, len(game.other_player.secrets))

    def test_IceBarrier(self):
        game = generate_game_for(IceBarrier, StonetuskBoar, CardTestingAgent, PredictableAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Ice Barrier", game.current_player.secrets[0].name)

        game.play_single_turn()
        # only one minion because PredictableAgent will shoot its own minions if there isn't anything else to shoot.
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, game.other_player.hero.armor)

        # Attacked twice on the first turn, then fireballed before getting the armor up
        self.assertEqual(27, game.other_player.hero.health)

        # Make sure we can't have two identical secrets at the same time
        random.seed(1857)
        game = generate_game_for(IceBarrier, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.secrets))
        self.assertEqual("Ice Barrier", game.other_player.secrets[0].name)

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Ice Barrier", game.current_player.secrets[0].name)

    def test_IceBlock(self):
        game = generate_game_for([IceBlock, Deathwing], Frostbolt, CardTestingAgent, CardTestingAgent)

        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(game.other_player.hero.health, 3)
        self.assertEqual(1, len(game.other_player.secrets))

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, game.other_player.hero.health)
        self.assertEqual(0, len(game.other_player.secrets))

        game.play_single_turn()
        game.play_single_turn()

        self.assertTrue(game.game_ended)

    def test_MirrorEntity(self):
        game = generate_game_for([StonetuskBoar, MirrorEntity], IronfurGrizzly, CardTestingAgent, OneCardPlayingAgent)

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
        game = generate_game_for([Spellbender, Wisp], Moonfire, CardTestingAgent, CardTestingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        # The moonfire should have been re-directed to the Spellbender, which should have taken one damage
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[1].health)
        self.assertEqual(1, game.other_player.minions[1].calculate_attack())
        self.assertEqual("Spellbender", game.other_player.minions[1].card.name)

        # Now make sure it won't work when the hero is targeted
        random.seed(1857)
        game = generate_game_for(Spellbender, Moonfire, CardTestingAgent, CardTestingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(1, len(game.other_player.secrets))
        self.assertEqual(23, game.other_player.hero.health)

        # Now make sure it doesn't activate when a non-targeted spell is used
        random.seed(1857)
        game = generate_game_for(Spellbender, ArcaneIntellect, CardTestingAgent, CardTestingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        # The arcane intellect should not have caused the Spellbender to activate
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(1, len(game.other_player.secrets))

    def test_SpellbenderFullBoard(self):
        game = generate_game_for([Spellbender, Onyxia], Assassinate, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(17):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(7, len(game.current_player.minions))

        game.play_single_turn()
        self.assertEqual(6, len(game.other_player.minions))
        self.assertEqual(1, len(game.other_player.secrets))

    def test_Spellbender_full_board_target_hero(self):
        game = generate_game_for(BaneOfDoom, [Wisp, Wisp, Wisp, Wisp, Wisp, Wisp, Wisp, Spellbender],
                                 OneCardPlayingAgent, CardTestingAgent)
        for turn in range(10):
            game.play_single_turn()

        self.assertEqual(7, len(game.current_player.minions))
        self.assertEqual(1, len(game.current_player.secrets))
        game.other_player.agent.choose_target = lambda targets: game.players[1].hero

        game.play_single_turn()

        self.assertEqual(7, len(game.other_player.minions))
        self.assertEqual(28, game.other_player.hero.health)
        self.assertEqual(1, len(game.other_player.secrets))

    def test_Spellbender_target_hero_and_attack(self):
        game = generate_game_for([Spellbender, OasisSnapjaw], [LavaBurst, Wisp, Loatheb],
                                 OneCardPlayingAgent, PlayAndAttackAgent)

        for turn in range(5):
            game.play_single_turn()
        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual(0, len(game.other_player.minions))
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.secrets))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(25, game.other_player.hero.health)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(25, game.other_player.hero.health)
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(6, game.other_player.minions[0].health)
        self.assertEqual(1, len(game.other_player.secrets))

    def test_Vaporize(self):
        game = generate_game_for(Vaporize, FaerieDragon, CardTestingAgent, MinionAttackingAgent)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual(30, game.other_player.hero.health)

        random.seed(1857)
        game = generate_game_for(Vaporize, Swipe, CardTestingAgent, PredictableAgent)
        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(28, game.other_player.hero.health)
        self.assertEqual(1, len(game.other_player.secrets))
        self.assertFalse(game.current_player.hero.dead)

    def test_KirinTorMage(self):

        game = generate_game_for([KirinTorMage, Vaporize, Spellbender], StonetuskBoar,
                                 CardTestingAgent, DoNothingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.secrets))
        self.assertEqual("Vaporize", game.current_player.secrets[0].name)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Kirin Tor Mage", game.current_player.minions[0].card.name)
        self.assertEqual(3, game.current_player.hand[0].mana_cost())
        self.assertEqual("Spellbender", game.current_player.hand[0].name)

        random.seed(1857)
        game = generate_game_for([KirinTorMage, Vaporize], StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(0, len(game.current_player.secrets))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Kirin Tor Mage", game.current_player.minions[0].card.name)
        self.assertEqual(3, game.current_player.hand[2].mana_cost())
        self.assertEqual("Vaporize", game.current_player.hand[2].name)

    def test_EtherealArcanist(self):
        game = generate_game_for([Spellbender, EtherealArcanist], StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.secrets))

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(5, game.current_player.minions[0].calculate_max_health())

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(7, game.current_player.minions[0].calculate_attack())
        self.assertEqual(7, game.current_player.minions[0].health)
        self.assertEqual(7, game.current_player.minions[0].calculate_max_health())

        game.current_player.minions[0].silence()

        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].calculate_max_health())

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].calculate_max_health())

        # Test when the player has no secrets at all
        random.seed(1857)
        game = generate_game_for(EtherealArcanist, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].calculate_max_health())

    def test_ConeOfCold(self):
        game = generate_game_for(ConeOfCold, [StonetuskBoar, BloodfenRaptor, BloodfenRaptor], CardTestingAgent,
                                 OneCardPlayingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))

        game.play_single_turn()

        self.assertEqual(3, len(game.other_player.minions))
        self.assertTrue(game.other_player.minions[0].frozen)
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertTrue(game.other_player.minions[1].frozen)
        self.assertEqual(1, game.other_player.minions[1].health)
        self.assertFalse(game.other_player.minions[2].frozen)
        self.assertEqual(1, game.other_player.minions[2].health)
        self.assertEqual(30, game.other_player.hero.health)

        # Now check to ensure that it will work when targeting the other end of the minion list
        game.current_player.agent.choose_target = lambda targets: targets[len(targets) - 1]
        game.play_single_turn()
        game.play_single_turn()

        # Neither of the minions which survive Cone of Cold will be frozen, since they weren't touched this round
        self.assertEqual(2, len(game.other_player.minions))
        self.assertFalse(game.other_player.minions[0].frozen)
        self.assertFalse(game.other_player.minions[1].frozen)

    def test_Fireball(self):
        game = generate_game_for([Fireball, KoboldGeomancer], StonetuskBoar, EnemySpellTestingAgent, DoNothingAgent)
        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(24, game.other_player.hero.health)

        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(17, game.other_player.hero.health)

    def test_Polymorph(self):
        game = generate_game_for(MogushanWarden, Polymorph, OneCardPlayingAgent, CardTestingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(7, game.current_player.minions[0].health)
        self.assertEqual("Mogu'shan Warden", game.current_player.minions[0].card.name)

        game.play_single_turn()
        self.assertEqual(1, len(game.other_player.minions))
        self.assertFalse(game.other_player.minions[0].taunt)
        self.assertEqual(1, game.other_player.minions[0].calculate_attack())
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual("Sheep", game.other_player.minions[0].card.name)
        self.assertEqual(MINION_TYPE.BEAST, game.other_player.minions[0].card.minion_type)

    def test_Blizzard(self):
        game = generate_game_for(Blizzard, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(7, game.current_player.minions[0].health)
        self.assertEqual(7, game.current_player.minions[1].health)
        self.assertFalse(game.current_player.minions[0].frozen)
        self.assertFalse(game.current_player.minions[1].frozen)

        game.play_single_turn()
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(5, game.other_player.minions[0].health)
        self.assertEqual(5, game.other_player.minions[1].health)
        self.assertTrue(game.other_player.minions[0].frozen)
        self.assertTrue(game.other_player.minions[1].frozen)

    def test_Flamestrike(self):
        game = generate_game_for(Flamestrike, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(7, game.current_player.minions[0].health)
        self.assertEqual(7, game.current_player.minions[1].health)
        self.assertEqual(7, game.current_player.minions[2].health)

        game.play_single_turn()
        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual(3, game.other_player.minions[0].health)
        self.assertEqual(3, game.other_player.minions[1].health)
        self.assertEqual(3, game.other_player.minions[2].health)

    def test_Pyroblast(self):
        game = generate_game_for(Pyroblast, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        for turn in range(0, 18):
            game.play_single_turn()

        self.assertEqual(30, game.current_player.hero.health)
        game.play_single_turn()
        self.assertEqual(20, game.other_player.hero.health)

    def test_ArchmageAntonidas(self):
        game = generate_game_for([ArchmageAntonidas, Vaporize], StonetuskBoar, CardTestingAgent, DoNothingAgent)
        for turn in range(0, 12):
            game.play_single_turn()

        game.play_single_turn()
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Archmage Antonidas", game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual("Fireball", game.current_player.hand[9].name)

    def test_Duplicate(self):
        game = generate_game_for([BloodfenRaptor, Duplicate], ShadowBolt, OneCardPlayingAgent, CardTestingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(6, len(game.other_player.hand))
        self.assertEqual("Bloodfen Raptor", game.other_player.hand[4].name)
        self.assertEqual("Bloodfen Raptor", game.other_player.hand[5].name)
        self.assertEqual(0, len(game.other_player.secrets))

    def test_Duplicate_and_play_after(self):
        game = generate_game_for([Wisp, Wisp, Wisp, Wisp, Wisp, Duplicate], LightningStorm,
                                 CardTestingAgent, OneCardPlayingAgent)

        for turn in range(5):
            game.play_single_turn()

        self.assertEqual(0, len(game.current_player.hand))
        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(1, len(game.current_player.secrets))

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(2, len(game.other_player.hand))

        game.play_single_turn()

        self.assertEqual(0, len(game.current_player.hand))
        self.assertEqual(3, len(game.current_player.minions))

    def test_Duplicate_MadScientist(self):
        game = generate_game_for(Hellfire, [MadScientist, MagmaRager, Duplicate],
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(6):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(0, len(game.current_player.secrets))

        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(0, len(game.other_player.secrets))
        self.assertEqual("Magma Rager", game.other_player.hand[-1].name)
        self.assertEqual("Magma Rager", game.other_player.hand[-2].name)

    def test_Snowchugger(self):
        game = generate_game_for(Snowchugger, StonetuskBoar, PredictableAgent, DoNothingAgent)

        for turn in range(0, 7):
            game.play_single_turn()

        self.assertEqual(27, game.other_player.hero.health)
        self.assertFalse(game.other_player.hero.frozen)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual("Snowchugger", game.current_player.minions[0].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(25, game.other_player.hero.health)

        # Always false after the end of a turn
        self.assertTrue(game.other_player.hero.frozen)

        # Now make sure that attacking the Snowchugger directly will freeze a character
        random.seed(1857)
        game = generate_game_for(Snowchugger, IronbarkProtector, OneCardPlayingAgent, PredictableAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].health)
        # The player should be frozen because of weapon attack
        self.assertEqual(29, game.current_player.hero.health)
        self.assertTrue(game.current_player.hero.frozen)

        game.play_single_turn()
        game.play_single_turn()

        # The player should still be frozen from last turn, and thus shouldn't have attacked
        self.assertEqual(29, game.current_player.hero.health)

        # If Snowchugger gets 0 attack, and is being attacked so will the minion NOT be frozen since no damage was dealt
        game = generate_game_for(Snowchugger, StonetuskBoar, PredictableAgent, PredictableAgent)

        for turn in range(0, 2):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual("Snowchugger", game.players[1].minions[0].card.name)
        # Cheat
        game.players[1].minions[0].base_attack = 0
        self.assertEqual(0, game.players[1].minions[0].calculate_attack())
        self.assertEqual(3, game.players[1].minions[0].health)

        # Stonetusk should have attacked the Snowchugger, and will NOT be frozen since they didn't take damage
        game.play_single_turn()
        self.assertEqual(1, game.players[1].minions[0].health)
        self.assertFalse(game.players[0].minions[0].frozen)

    def test_GoblinBlastmage(self):
        game = generate_game_for([GoblinBlastmage, ClockworkGnome, GoblinBlastmage], [Mechwarper, ClockworkGnome],
                                 CardTestingAgent, CardTestingAgent)

        for turn in range(6):
            game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(7, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(1, game.current_player.minions[1].health)
        self.assertEqual(3, game.current_player.minions[2].health)
        self.assertEqual(1, game.current_player.minions[3].health)
        self.assertEqual(3, game.current_player.minions[4].health)
        self.assertEqual(1, game.current_player.minions[5].health)
        self.assertEqual(3, game.current_player.minions[6].health)

        # Blastmage should not go off, as there is no friendly mech down
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(7, len(game.other_player.minions))
        self.assertEqual(3, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[1].health)
        self.assertEqual(3, game.other_player.minions[2].health)
        self.assertEqual(1, game.other_player.minions[3].health)
        self.assertEqual(3, game.other_player.minions[4].health)
        self.assertEqual(1, game.other_player.minions[5].health)
        self.assertEqual(3, game.other_player.minions[6].health)
        self.assertEqual(30, game.other_player.hero.health)

        game.play_single_turn()
        game.play_single_turn()

        # The Blastmage hits the warper at index 2 twice, and the two gnomes at indices 1 and 3.
        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(5, len(game.other_player.minions))
        self.assertEqual(3, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[1].health)
        self.assertEqual(1, game.other_player.minions[2].health)
        self.assertEqual(3, game.other_player.minions[3].health)
        self.assertEqual(3, game.other_player.minions[4].health)
        self.assertEqual(30, game.other_player.hero.health)

    def test_Flamecannon(self):
        game = generate_game_for(Flamecannon, SenjinShieldmasta, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        # Flamecannon hasn't been played since there hasn't been an enemy minion until now.
        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(5, game.players[1].minions[0].health)

        # Enemy minion exist, so Flamecannon will be played.
        game.play_single_turn()
        self.assertEqual(7, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[1].minions[0].health)

    def test_WeeSpellstopper(self):
        game = generate_game_for(WeeSpellstopper, ShadowBolt, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        # First Spellstopper gets Bolted but lives with 1 hp
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)

        # Once there are 2 Spellstoppers, they are both spell immune
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[0].minions[1].health)

        game.play_single_turn()
        game.players[0].minions[0].die(None)
        game.players[0].minions[1].die(None)
        game.check_delayed()
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)

        # Last Spellstopper is not immune and dies to Shadow Bolt
        game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))

    def test_WeeSpellstopperSilence(self):
        game = generate_game_for(WeeSpellstopper, [Silence, ShadowBolt], OneCardPlayingAgent,
                                 OneCardPlayingAgent)
        for turn in range(0, 8):
            game.play_single_turn()

        # First Spellstopper gets silenced
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].health)

        # Once there are 2 Spellstoppers, but only the first receives the aura
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(5, game.players[0].minions[1].health)

    def test_FlameLeviathan(self):
        game = generate_game_for(Wisp, FlameLeviathan, CardTestingAgent, CardTestingAgent)

        game.play_single_turn()
        self.assertEqual(4, len(game.current_player.minions))
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(30, game.other_player.hero.health)

        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(28, game.current_player.hero.health)
        self.assertEqual(28, game.other_player.hero.health)

    def test_EchoOfMedivh(self):
        game = generate_game_for([NoviceEngineer, NoviceEngineer, GnomishInventor, GnomishInventor, EchoOfMedivh], Wisp,
                                 OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        # Plays first 4 "draw" minions
        self.assertEqual(8, len(game.players[0].hand))
        self.assertEqual(4, len(game.players[0].minions))

        game.play_single_turn()

        # Plays Echo and overflows
        self.assertEqual(10, len(game.players[0].hand))
        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual("Novice Engineer", game.players[0].hand[8].name)
        self.assertEqual("Novice Engineer", game.players[0].hand[9].name)

    def test_UnstablePortal(self):
        game = generate_game_for(UnstablePortal, StonetuskBoar, CardTestingAgent, DoNothingAgent)

        for turn in range(3):
            game.play_single_turn()

        self.assertEqual(5, len(game.current_player.hand))
        self.assertTrue(game.current_player.hand[-1].is_minion())
        if game.current_player.hand[-1].mana >= 3:
            # TODO This assertion may fail, if unstable portal summons a Giant.  Don't know how to solve that issue
            self.assertEqual(3, game.current_player.hand[-1].mana - game.current_player.hand[-1].mana_cost())

    def test_DragonsBreath(self):
        game = generate_game_for([Flamestrike, DragonsBreath], StonetuskBoar, CardTestingAgent, OneCardPlayingAgent)

        for turn in range(13):
            game.play_single_turn()

        # The flamestrike kills 6 boars, so the Dragon's Breath is free
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(26, game.other_player.hero.health)

        game.play_single_turn()
        game.play_single_turn()

        # The Flamestrike only kills one boar, so we can't afford the Dragon's breath
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(26, game.other_player.hero.health)

    def test_Flamewaker(self):
        game = generate_game_for([Flamewaker, CircleOfHealing], CircleOfHealing,
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(6):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(30, game.players[1].hero.health)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(30, game.players[0].hero.health)
        self.assertEqual(28, game.players[1].hero.health)

    def test_ArcaneBlast(self):
        game = generate_game_for([KoboldGeomancer, DalaranMage, OgreMagi, ArcaneBlast], TournamentMedic,
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(8):
            game.play_single_turn()

        self.assertEqual(3, len(game.other_player.minions))
        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(3, len(game.current_player.minions))
