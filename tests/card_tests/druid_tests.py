import random
import unittest

from hearthbreaker.agents.basic_agents import DoNothingAgent
from hearthbreaker.engine import Game
from tests.agents.testing_agents import SelfSpellTestingAgent, EnemySpellTestingAgent, OneCardPlayingAgent, \
    EnemyMinionSpellTestingAgent, CardTestingAgent, PlayAndAttackAgent
from hearthbreaker.constants import CHARACTER_CLASS, MINION_TYPE
from hearthbreaker.replay import playback, Replay
from tests.testing_utils import generate_game_for, StackedDeck, mock
from hearthbreaker.cards import *


class TestDruid(unittest.TestCase):
    def setUp(self):
        random.seed(1857)

    def test_Innervate(self):
        game = generate_game_for(Innervate, StonetuskBoar, SelfSpellTestingAgent, DoNothingAgent)
        # triggers all four innervate cards the player is holding.
        game.play_single_turn()
        self.assertEqual(9, game.current_player.mana)

        for turn in range(0, 16):
            game.play_single_turn()

        # The mana should not go over 10 on turn 9 (or any other turn)
        self.assertEqual(10, game.current_player.mana)

    def test_Claw(self):
        testing_env = self

        class ClawAgent(EnemySpellTestingAgent):
            def do_turn(self, player):
                super().do_turn(player)
                testing_env.assertEqual(2, game.current_player.hero.calculate_attack())
                testing_env.assertEqual(2, game.current_player.hero.armor)

        game = generate_game_for(Claw, StonetuskBoar, ClawAgent, OneCardPlayingAgent)
        game.pre_game()
        game.play_single_turn()

    def test_Naturalize(self):
        game = generate_game_for(StonetuskBoar, Naturalize, OneCardPlayingAgent, EnemyMinionSpellTestingAgent)
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(5, len(game.other_player.hand))

    def test_Savagery(self):
        class SavageryAgent(EnemyMinionSpellTestingAgent):
            def do_turn(self, player):
                if player.mana > 2:
                    player.hero.power.use()
                    super().do_turn(player)

        game = generate_game_for(Savagery, BloodfenRaptor, SavageryAgent, OneCardPlayingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)

    def test_ClawAndSavagery(self):

        game = generate_game_for(BloodfenRaptor, [Claw, Claw, Savagery], OneCardPlayingAgent,
                                 EnemyMinionSpellTestingAgent)
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))

    def test_MarkOfTheWild(self):
        game = generate_game_for(MarkOfTheWild, StonetuskBoar, EnemyMinionSpellTestingAgent, OneCardPlayingAgent)
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, game.other_player.minions[0].calculate_attack())
        self.assertEqual(3, game.other_player.minions[0].health)
        self.assertEqual(3, game.other_player.minions[0].calculate_max_health())

        # Test that this spell is being silenced properly as well
        game.other_player.minions[0].silence()
        self.assertEqual(1, game.other_player.minions[0].calculate_attack())
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(1, game.other_player.minions[0].calculate_max_health())

    def test_PowerOfTheWild(self):
        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), PowerOfTheWild()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)

        # This is a test of the +1/+1 option of the Power Of the Wild Card
        game = Game([deck1, deck2], [OneCardPlayingAgent(), OneCardPlayingAgent()])
        game.current_player = game.players[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertEqual(2, game.current_player.minions[1].calculate_attack())
        self.assertEqual(2, game.current_player.minions[1].calculate_max_health())

        # This is a test of the "Summon Panther" option of the Power of the Wild Card

        agent = OneCardPlayingAgent()
        agent.choose_option = lambda options, player: options[1]

        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), PowerOfTheWild()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)
        game = Game([deck1, deck2], [agent, OneCardPlayingAgent()])
        game.current_player = game.players[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual("Panther", game.current_player.minions[2].card.__class__.__name__)
        self.assertEqual(3, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].calculate_max_health())

    def test_WildGrowth(self):
        game = generate_game_for(WildGrowth, StonetuskBoar, SelfSpellTestingAgent, DoNothingAgent)
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(3, game.current_player.max_mana)

        # Make sure that the case where the player is at 10 mana works as well.
        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(10, game.other_player.max_mana)
        card_draw_mock = mock.Mock(side_effect=game.other_player.draw)
        game.other_player.draw = card_draw_mock
        game.play_single_turn()
        # Each time the player draws, they will draw another wild growth, which will turn into excess mana,
        # which will draw another card.  However, because of the ordering of the cards, the last excess mana
        # will be after a wild growth, which prevents SpellTestingAgent from playing the card, so only
        # 5 draws are made instead of the possible 6
        self.assertEqual(5, card_draw_mock.call_count)

    def test_Wrath(self):
        game = generate_game_for(Wrath, StonetuskBoar, EnemyMinionSpellTestingAgent, OneCardPlayingAgent)
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(5, len(game.current_player.hand))

        random.seed(1857)
        game = generate_game_for(Wrath, MogushanWarden, EnemyMinionSpellTestingAgent, OneCardPlayingAgent)
        game.players[0].agent.choose_option = lambda options, player: options[1]
        for turn in range(0, 8):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))

        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        # Two wraths will have been played
        self.assertEqual(1, game.other_player.minions[0].health)

    def test_HealingTouch(self):
        game = generate_game_for(HealingTouch, StonetuskBoar, SelfSpellTestingAgent, DoNothingAgent)
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.other_player.hero.health = 20
        game.play_single_turn()
        self.assertEqual(28, game.current_player.hero.health)
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(30, game.current_player.hero.health)

    def test_MarkOfNature(self):
        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), MarkOfNature()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)
        game = Game([deck1, deck2], [OneCardPlayingAgent(), OneCardPlayingAgent()])

        game.current_player = 1
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, game.other_player.minions[0].calculate_attack())

        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), MarkOfNature()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)
        agent = OneCardPlayingAgent()
        agent.choose_option = lambda options, player: options[1]
        game = Game([deck1, deck2], [agent, OneCardPlayingAgent()])

        game.current_player = 1
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(5, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(5, game.other_player.minions[0].health)
        self.assertTrue(game.other_player.minions[0].taunt)

    def test_SavageRoar(self):
        deck1 = StackedDeck([StonetuskBoar(), StonetuskBoar(), SavageRoar()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.MAGE)
        game = Game([deck1, deck2], [OneCardPlayingAgent(), OneCardPlayingAgent()])

        game.current_player = 1
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        minion_increase_mock = mock.Mock()

        game.other_player.minions[0].bind("attack_changed", minion_increase_mock)
        game.other_player.minions[1].bind("attack_changed", minion_increase_mock)

        player_increase_mock = mock.Mock()

        game.other_player.hero.bind("attack_changed", player_increase_mock)

        game.play_single_turn()

        self.assertEqual(0, game.current_player.mana)

        # Make sure the attack got increased
        self.assertListEqual([mock.call(2), mock.call(2)], minion_increase_mock.call_args_list)
        self.assertListEqual([mock.call(2)], player_increase_mock.call_args_list)

        # And make sure that it went down again
        self.assertEqual(1, game.current_player.minions[0].calculate_attack())
        self.assertEqual(1, game.current_player.minions[1].calculate_attack())
        self.assertEqual(0, game.current_player.hero.calculate_attack())

    def test_Bite(self):
        testing_env = self

        class BiteAgent(EnemySpellTestingAgent):
            def do_turn(self, player):
                super().do_turn(player)
                if player.mana == 0:
                    testing_env.assertEqual(4, game.current_player.hero.calculate_attack())
                    testing_env.assertEqual(4, game.current_player.hero.armor)

        game = generate_game_for(Bite, StonetuskBoar, BiteAgent, DoNothingAgent)
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

    def test_SoulOfTheForest(self):
        game = playback(Replay("tests/replays/card_tests/SoulOfTheForest.hsreplay"))
        game.start()
        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].calculate_attack())
        self.assertEqual(2, game.other_player.minions[0].health)
        self.assertEqual("Treant", game.other_player.minions[0].card.name)

    def test_Swipe(self):
        deck1 = StackedDeck([BloodfenRaptor(), StonetuskBoar(), StonetuskBoar()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([Swipe()], CHARACTER_CLASS.DRUID, )
        game = Game([deck1, deck2], [OneCardPlayingAgent(), EnemyMinionSpellTestingAgent()])
        game.pre_game()
        game.current_player = game.players[1]
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        # The bloodfen raptor should be left, with one hp
        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(1, game.other_player.minions[0].health)
        self.assertEqual(29, game.other_player.hero.health)

    def test_KeeperOfTheGrove(self):
        # Test Moonfire option

        game = generate_game_for(KeeperOfTheGrove, StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))

        game.play_single_turn()

        self.assertEqual(2, len(game.other_player.minions))

        # Test Dispel option

        random.seed(1857)

        game = generate_game_for(KeeperOfTheGrove, StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)

        game.players[0].agent.choose_option = lambda options, player: options[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertTrue(game.current_player.minions[0].charge())

        game.play_single_turn()

        self.assertFalse(game.other_player.minions[0].charge())

        # Test when there are no targets for the spell
        random.seed(1857)
        game = generate_game_for(KeeperOfTheGrove, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual("Keeper of the Grove", game.current_player.minions[0].card.name)

    def test_Moonfire(self):
        game = generate_game_for(Moonfire, StonetuskBoar, EnemySpellTestingAgent, OneCardPlayingAgent)
        game.play_single_turn()
        self.assertEqual(26, game.other_player.hero.health)

    def test_DruidOfTheClaw(self):
        game = generate_game_for(DruidOfTheClaw, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 9):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())
        self.assertTrue(game.current_player.minions[0].charge())
        self.assertFalse(game.current_player.minions[0].taunt)

        test_bear = game.current_player.minions[0].card.create_minion(None)
        test_bear.player = game.current_player
        self.assertEqual(4, test_bear.calculate_attack())
        self.assertEqual(4, test_bear.calculate_max_health())

        game.current_player.agent.choose_option = lambda options, player: options[1]

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(6, game.current_player.minions[0].calculate_max_health())
        self.assertFalse(game.current_player.minions[0].charge())
        self.assertTrue(game.current_player.minions[0].taunt)

        test_bear = game.current_player.minions[0].card.create_minion(None)
        test_bear.player = game.current_player
        self.assertEqual(4, test_bear.calculate_attack())
        self.assertEqual(6, test_bear.calculate_max_health())

    def test_Nourish(self):

        # Test gaining two mana
        game = generate_game_for(Nourish, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(7, game.current_player.max_mana)
        self.assertEqual(7, len(game.current_player.hand))

        # Ensure that the case where we would be over 10 mana is handled correctly

        game.play_single_turn()
        game.play_single_turn()
        # Nourish is played.  it brings the player to 10

        self.assertEqual(10, game.current_player.max_mana)
        self.assertEqual(5, game.current_player.mana)

        game.play_single_turn()
        game.play_single_turn()

        # Nourish is played.  It doesn't affect the max_mana, but it does fill in two crystals.
        # Tested on patch 2.1.0.7785
        self.assertEqual(10, game.current_player.max_mana)
        self.assertEqual(7, game.current_player.mana)

        # Test drawing three cards
        random.seed(1857)
        game = generate_game_for(Nourish, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        game.players[0].agent.choose_option = lambda options, player: options[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(10, len(game.current_player.hand))
        self.assertEqual(5, game.current_player.max_mana)

    def test_Starfall(self):

        # Test damage to all
        game = generate_game_for(Starfall, StonetuskBoar, CardTestingAgent, OneCardPlayingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(4, len(game.current_player.minions))
        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(30, game.other_player.hero.health)

        # Test damage to one
        random.seed(1857)
        game = generate_game_for(Starfall, MogushanWarden, CardTestingAgent, OneCardPlayingAgent)
        game.players[0].agent.choose_option = lambda options, player: options[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].health)
        self.assertEqual(30, game.other_player.hero.health)

    def test_ForceOfNature(self):
        game = generate_game_for(ForceOfNature, StonetuskBoar, CardTestingAgent, DoNothingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        def check_minions():
            self.assertEqual(3, len(game.current_player.minions))

            for minion in game.current_player.minions:
                self.assertEqual(2, minion.calculate_attack())
                self.assertEqual(2, minion.health)
                self.assertEqual(2, minion.calculate_max_health())
                self.assertTrue(minion.charge())
                self.assertEqual("Treant", minion.card.name)

        game.other_player.bind_once("turn_ended", check_minions)

        game.play_single_turn()

        self.assertEqual(0, len(game.other_player.minions))

    def test_Starfire(self):
        game = generate_game_for(Starfire, MogushanWarden, EnemyMinionSpellTestingAgent, OneCardPlayingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))

        game.play_single_turn()

        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(2, game.other_player.minions[0].health)
        self.assertEqual(7, game.other_player.minions[1].health)
        self.assertEqual(9, len(game.current_player.hand))

    def test_AncientOfLore(self):
        game = generate_game_for(AncientOfLore, Starfire, OneCardPlayingAgent, EnemySpellTestingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(game.other_player.hero.health, 25)

        game.play_single_turn()

        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())
        self.assertEqual("Ancient of Lore", game.current_player.minions[0].card.name)

        random.seed(1857)

        game = generate_game_for(AncientOfLore, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        game.players[0].agent.choose_option = lambda options, player: options[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(10, len(game.current_player.hand))
        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())
        self.assertEqual("Ancient of Lore", game.current_player.minions[0].card.name)

    def test_AncientOfWar(self):
        game = generate_game_for(AncientOfWar, IronbeakOwl, OneCardPlayingAgent, OneCardPlayingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())
        self.assertEqual(10, game.current_player.minions[0].health)
        self.assertEqual(10, game.current_player.minions[0].calculate_max_health())
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual("Ancient of War", game.current_player.minions[0].card.name)
        self.assertEqual(5, len(game.other_player.minions))

        game.play_single_turn()

        self.assertEqual(6, len(game.current_player.minions))
        self.assertEqual(5, game.other_player.minions[0].health)
        self.assertEqual(5, game.other_player.minions[0].calculate_max_health())
        self.assertFalse(game.other_player.minions[0].taunt)

        random.seed(1857)
        game = generate_game_for(AncientOfWar, IronbeakOwl, OneCardPlayingAgent, OneCardPlayingAgent)
        game.players[0].agent.choose_option = lambda options, player: options[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(10, game.current_player.minions[0].calculate_attack())
        self.assertEqual(5, game.current_player.minions[0].health)
        self.assertEqual(5, game.current_player.minions[0].calculate_max_health())
        self.assertFalse(game.current_player.minions[0].taunt)
        self.assertEqual("Ancient of War", game.current_player.minions[0].card.name)
        self.assertEqual(5, len(game.other_player.minions))

        game.play_single_turn()

        self.assertEqual(6, len(game.current_player.minions))
        self.assertEqual(5, game.other_player.minions[0].health)
        self.assertEqual(5, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(5, game.other_player.minions[0].calculate_attack())
        self.assertFalse(game.other_player.minions[0].taunt)

    def test_IronbarkProtector(self):
        game = generate_game_for(IronbarkProtector, IronbeakOwl, OneCardPlayingAgent, OneCardPlayingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(8, game.current_player.minions[0].calculate_attack())
        self.assertEqual(8, game.current_player.minions[0].health)
        self.assertEqual(8, game.current_player.minions[0].calculate_max_health())
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual("Ironbark Protector", game.current_player.minions[0].card.name)
        self.assertEqual(6, len(game.other_player.minions))

        game.play_single_turn()

        self.assertEqual(7, len(game.current_player.minions))
        self.assertFalse(game.other_player.minions[0].taunt)

    def test_Cenarius(self):
        deck1 = StackedDeck([StonetuskBoar()], CHARACTER_CLASS.DRUID)
        deck2 = StackedDeck([WarGolem(), WarGolem(), Cenarius(), Cenarius()], CHARACTER_CLASS.DRUID)
        game = Game([deck1, deck2], [DoNothingAgent(), OneCardPlayingAgent()])
        game.pre_game()

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()
        self.assertEqual(2, len(game.other_player.minions))
        for minion in game.other_player.minions:
            self.assertEqual(7, minion.calculate_attack())
            self.assertEqual(7, minion.health)
            self.assertEqual(7, minion.calculate_max_health())
        game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))

        self.assertEqual(5, game.current_player.minions[0].calculate_attack())
        self.assertEqual(8, game.current_player.minions[0].health)
        self.assertEqual(8, game.current_player.minions[0].calculate_max_health())
        self.assertEqual("Cenarius", game.current_player.minions[0].card.name)

        for minion_index in range(1, 3):
            minion = game.current_player.minions[minion_index]
            self.assertEqual(9, minion.calculate_attack())
            self.assertEqual(9, minion.health)
            self.assertEqual(9, minion.calculate_max_health())

        game.players[1].agent.choose_option = lambda options, player: options[1]

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(6, len(game.current_player.minions))

        self.assertEqual(5, game.current_player.minions[1].calculate_attack())
        self.assertEqual(8, game.current_player.minions[1].health)
        self.assertEqual(8, game.current_player.minions[1].calculate_max_health())
        self.assertEqual("Cenarius", game.current_player.minions[1].card.name)

        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual("Treant", game.current_player.minions[0].card.name)

        self.assertEqual(2, game.current_player.minions[2].calculate_attack())
        self.assertEqual(2, game.current_player.minions[2].health)
        self.assertEqual(2, game.current_player.minions[2].calculate_max_health())
        self.assertTrue(game.current_player.minions[2].taunt)
        self.assertEqual("Treant", game.current_player.minions[2].card.name)

    def test_PoisonSeeds(self):
        game = generate_game_for([StonetuskBoar, BloodfenRaptor, IronfurGrizzly, PoisonSeeds],
                                 HauntedCreeper, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(0, 6):
            game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(3, len(game.other_player.minions))

        game.play_single_turn()

        self.assertEqual(3, len(game.current_player.minions))
        self.assertEqual(6, len(game.other_player.minions))

        for minion in game.current_player.minions:
            self.assertEqual("Treant", minion.card.name)
            self.assertEqual(2, minion.calculate_attack())
            self.assertEqual(2, minion.calculate_max_health())

        for index in range(0, 4):
            self.assertEqual("Spectral Spider", game.other_player.minions[index].card.name)
            self.assertEqual(1, game.other_player.minions[index].calculate_attack())
            self.assertEqual(1, game.other_player.minions[index].calculate_max_health())

        self.assertEqual("Treant", game.other_player.minions[4].card.name)
        self.assertEqual(2, game.other_player.minions[4].calculate_attack())
        self.assertEqual(2, game.other_player.minions[4].calculate_max_health())

        self.assertEqual("Treant", game.other_player.minions[5].card.name)
        self.assertEqual(2, game.other_player.minions[5].calculate_attack())
        self.assertEqual(2, game.other_player.minions[5].calculate_max_health())

    def test_AnodizedRoboCub(self):
        game = generate_game_for(AnodizedRoboCub, IronbeakOwl, OneCardPlayingAgent, OneCardPlayingAgent)

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(3, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].health)
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual("Anodized Robo Cub", game.current_player.minions[0].card.name)
        self.assertEqual(0, len(game.other_player.minions))

        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.other_player.minions[0].health)
        self.assertEqual(2, game.other_player.minions[0].calculate_max_health())
        self.assertFalse(game.other_player.minions[0].taunt)

        random.seed(1857)
        game = generate_game_for(AnodizedRoboCub, IronbeakOwl, OneCardPlayingAgent, OneCardPlayingAgent)
        game.players[0].agent.choose_option = lambda options, player: options[1]

        game.play_single_turn()
        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(3, game.current_player.minions[0].health)
        self.assertEqual(3, game.current_player.minions[0].calculate_max_health())
        self.assertTrue(game.current_player.minions[0].taunt)
        self.assertEqual("Anodized Robo Cub", game.current_player.minions[0].card.name)
        self.assertEqual(0, len(game.other_player.minions))

        game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(2, game.other_player.minions[0].health)
        self.assertEqual(2, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(2, game.other_player.minions[0].calculate_attack())
        self.assertFalse(game.other_player.minions[0].taunt)

    def test_MechBearCat(self):
        game = generate_game_for(MechBearCat, Whirlwind, OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 11):
            game.play_single_turn()

        self.assertEqual(8, len(game.players[0].hand))
        self.assertEqual(6, game.players[0].minions[0].health)

        # Whirlwind damages Mech-Bear-Cat drawing a Spare Part
        game.play_single_turn()

        self.assertEqual(9, len(game.players[0].hand))
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual("Rusty Horn", game.players[0].hand[8].name)

    def test_DarkWispers(self):
        game = generate_game_for(DarkWispers, SaltyDog, CardTestingAgent, OneCardPlayingAgent)
        game.players[0].agent.choose_option = lambda options, player: options[1]
        for turn in range(0, 10):
            game.play_single_turn()

        # 1 Salty Dog on the field
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(7, game.players[1].minions[0].calculate_attack())
        self.assertEqual(4, game.players[1].minions[0].health)
        self.assertFalse(game.players[1].minions[0].taunt)

        # Chooses to buff enemy Salty Dog
        game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(12, game.players[1].minions[0].calculate_attack())
        self.assertEqual(9, game.players[1].minions[0].health)
        self.assertTrue(game.players[1].minions[0].taunt)

        random.seed(1857)
        game = generate_game_for(DarkWispers, SaltyDog, CardTestingAgent, OneCardPlayingAgent)
        for turn in range(0, 10):
            game.play_single_turn()

        # 1 Salty Dog on the field
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))

        # Summons 5 Wisps
        game.play_single_turn()

        self.assertEqual(5, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[0].minions[0].calculate_attack())
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual("Wisp", game.players[0].minions[0].card.name)
        self.assertEqual(1, game.players[0].minions[1].calculate_attack())
        self.assertEqual(1, game.players[0].minions[1].health)
        self.assertEqual("Wisp", game.players[0].minions[1].card.name)
        self.assertEqual(1, game.players[0].minions[2].calculate_attack())
        self.assertEqual(1, game.players[0].minions[2].health)
        self.assertEqual("Wisp", game.players[0].minions[2].card.name)
        self.assertEqual(1, game.players[0].minions[3].calculate_attack())
        self.assertEqual(1, game.players[0].minions[3].health)
        self.assertEqual("Wisp", game.players[0].minions[3].card.name)
        self.assertEqual(1, game.players[0].minions[4].calculate_attack())
        self.assertEqual(1, game.players[0].minions[4].health)
        self.assertEqual("Wisp", game.players[0].minions[4].card.name)

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(7, len(game.players[0].minions))

    def test_DruidOfTheFang(self):
        game = generate_game_for([StonetuskBoar, DruidOfTheFang], DruidOfTheFang,
                                 OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(10):
            game.play_single_turn()

        self.assertEqual(2, len(game.other_player.minions))
        self.assertEqual(7, game.other_player.minions[0].calculate_attack())
        self.assertEqual(7, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(MINION_TYPE.BEAST, game.other_player.minions[0].card.minion_type)

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(4, game.current_player.minions[0].calculate_attack())
        self.assertEqual(4, game.current_player.minions[0].calculate_max_health())

        game.other_player.minions[0].silence()
        self.assertEqual(7, game.other_player.minions[0].calculate_attack())
        self.assertEqual(7, game.other_player.minions[0].calculate_max_health())
        self.assertEqual(MINION_TYPE.BEAST, game.other_player.minions[0].card.minion_type)

    def test_Recycle(self):
        game = generate_game_for(Recycle, StonetuskBoar, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(10):
            game.play_single_turn()

        self.assertEqual(5, len(game.current_player.minions))
        self.assertEqual(21, game.current_player.deck.left)

        game.play_single_turn()
        self.assertEqual(4, len(game.other_player.minions))
        self.assertEqual(22, game.other_player.deck.left)

    def test_Malorne(self):
        game = generate_game_for(Malorne, Assassinate, OneCardPlayingAgent, OneCardPlayingAgent)

        for turn in range(13):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(20, game.players[0].deck.left)

        game.play_single_turn()
        self.assertEqual(0, len(game.other_player.minions))
        self.assertEqual(21, game.other_player.deck.left)
        for card in game.other_player.deck.cards:
            self.assertIsNotNone(card)

    def test_Malorne_game_ends(self):
        game = generate_game_for(Malorne, Malorne, PlayAndAttackAgent, PlayAndAttackAgent)

        for turn in range(500):
            game.play_single_turn()

        self.assertTrue(game.game_ended)

    def test_GroveTender(self):
        game = generate_game_for(GroveTender, Wisp, OneCardPlayingAgent, DoNothingAgent)
        for turn in range(0, 4):
            game.play_single_turn()

        # Before Gift of Mana
        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(2, game.players[0].max_mana)
        self.assertEqual(2, game.players[1].max_mana)

        game.play_single_turn()

        # Both players have 1 more full mana crystal
        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, game.players[0].mana)
        self.assertEqual(4, game.players[0].max_mana)
        self.assertEqual(3, game.players[1].mana)
        self.assertEqual(3, game.players[1].max_mana)

        game.players[0].agent.choose_option = lambda options, player: options[1]

        # Before Gift of Cards
        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, len(game.players[0].hand))
        self.assertEqual(8, len(game.players[1].hand))

        # Both players draw 1
        game.play_single_turn()

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(6, len(game.players[0].hand))
        self.assertEqual(9, len(game.players[1].hand))

    def test_TreeOfLife(self):
        game = generate_game_for([SpiderTank, Hellfire, TreeOfLife], [SpiderTank, Deathwing],
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 16):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(1, game.players[0].minions[0].health)
        self.assertEqual(1, game.players[1].minions[0].health)
        self.assertEqual(27, game.current_player.hero.health)
        self.assertEqual(27, game.other_player.hero.health)

        game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(4, game.players[0].minions[0].health)
        self.assertEqual(4, game.players[1].minions[0].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(30, game.other_player.hero.health)

    def test_TreeOfLifeAuchenai(self):
        game = generate_game_for([ShieldBlock, AuchenaiSoulpriest, TreeOfLife], [ShieldBlock, Deathwing],
                                 OneCardPlayingAgent, OneCardPlayingAgent)
        for turn in range(0, 16):
            game.play_single_turn()

        self.assertEqual(1, len(game.players[0].minions))
        self.assertEqual(5, game.players[0].minions[0].health)
        self.assertEqual(30, game.current_player.hero.health)
        self.assertEqual(30, game.other_player.hero.health)
        self.assertEqual(5, game.current_player.hero.armor)
        self.assertEqual(5, game.other_player.hero.armor)

        game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(5, game.current_player.hero.health)
        self.assertEqual(5, game.other_player.hero.health)
        self.assertEqual(0, game.current_player.hero.armor)
        self.assertEqual(0, game.other_player.hero.armor)

    def test_DruidOfTheFlame(self):
        game = generate_game_for(DruidOfTheFlame, StonetuskBoar, OneCardPlayingAgent, DoNothingAgent)

        for turn in range(0, 5):
            game.play_single_turn()

        self.assertEqual(1, len(game.current_player.minions))
        self.assertEqual(5, game.current_player.minions[0].calculate_attack())
        self.assertEqual(2, game.current_player.minions[0].calculate_max_health())

        test_cat = game.current_player.minions[0].card.create_minion(None)
        test_cat.player = game.current_player
        self.assertEqual(5, test_cat.calculate_attack())
        self.assertEqual(2, test_cat.calculate_max_health())

        game.current_player.agent.choose_option = lambda options, player: options[1]

        game.play_single_turn()
        game.play_single_turn()

        self.assertEqual(2, len(game.current_player.minions))
        self.assertEqual(2, game.current_player.minions[0].calculate_attack())
        self.assertEqual(5, game.current_player.minions[0].calculate_max_health())

        test_bird = game.current_player.minions[0].card.create_minion(None)
        test_bird.player = game.current_player
        self.assertEqual(2, test_bird.calculate_attack())
        self.assertEqual(5, test_bird.calculate_max_health())

    def test_VolcanicLumberer(self):
        game = generate_game_for(LeeroyJenkins, [TwistingNether, VolcanicLumberer],
                                 OneCardPlayingAgent, CardTestingAgent)

        for turn in range(0, 15):
            game.play_single_turn()

        self.assertEqual(4, len(game.players[0].minions))
        self.assertEqual(7, len(game.players[1].minions))

        game.play_single_turn()

        self.assertEqual(0, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))
        self.assertEqual(7, game.players[1].minions[0].calculate_attack())
        self.assertEqual(8, game.players[1].minions[0].calculate_max_health())
