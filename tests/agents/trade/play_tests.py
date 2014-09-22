import unittest
from hearthbreaker.cards import ArgentSquire, DireWolfAlpha, HarvestGolem, BloodfenRaptor, MagmaRager
from hearthbreaker.game_objects import TheCoin
from tests.agents.trade.test_helpers import TestHelpers
from hearthbreaker.agents.trade.possible_play import PossiblePlays
from tests.agents.trade.test_case_mixin import TestCaseMixin


class TestTradeAgentPlayTests(TestCaseMixin, unittest.TestCase):
    def test_simple_plays(self):
        game = TestHelpers().make_game()

        self.set_hand(game, 0, ArgentSquire(), DireWolfAlpha(), HarvestGolem())

        game.play_single_turn()

        self.assert_minions(game.players[0], "Argent Squire")

        game.play_single_turn()
        game.play_single_turn()

        self.assert_minions(game.players[0], "Argent Squire", "Dire Wolf Alpha")

    def test_will_play_biggest(self):
        game = TestHelpers().make_game()

        game.players[0].hand = self.make_cards(ArgentSquire(), ArgentSquire(), DireWolfAlpha())
        game.players[0].mana = 1
        game.players[0].max_mana = 1

        game.play_single_turn()

        self.assert_minions(game.players[0], "Dire Wolf Alpha")

    def test_will_play_multiple(self):
        game = TestHelpers().make_game()

        game.players[0].hand = self.make_cards(ArgentSquire(), ArgentSquire(), ArgentSquire())
        game.players[0].mana = 1
        game.players[0].max_mana = 1

        game.play_single_turn()

        self.assert_minions(game.players[0], "Argent Squire", "Argent Squire")

    def test_will_play_multiple_correct_order(self):
        game = TestHelpers().make_game()

        game.players[0].hand = self.make_cards(ArgentSquire(), ArgentSquire(), ArgentSquire(), HarvestGolem())
        game.players[0].mana = 3
        game.players[0].max_mana = 3

        game.play_single_turn()

        self.assert_minions(game.players[0], "Harvest Golem", "Argent Squire")

    def test_will_use_entire_pool(self):
        game = TestHelpers().make_game()

        game.players[0].hand = self.make_cards(DireWolfAlpha(), DireWolfAlpha(), DireWolfAlpha(), HarvestGolem())
        game.players[0].mana = 3
        game.players[0].max_mana = 3

        game.play_single_turn()

        self.assert_minions(game.players[0], "Dire Wolf Alpha", "Dire Wolf Alpha")


class TestTradeAgentPlayCoinTests(TestCaseMixin, unittest.TestCase):
    def test_coin(self):
        cards = self.make_cards(ArgentSquire(), BloodfenRaptor(), TheCoin())
        possible_plays = PossiblePlays(cards, 1)
        play = possible_plays.plays()[0]
        names = [c.name for c in play.cards]
        self.assertEqual(names, ["The Coin", "Bloodfen Raptor"])

    def test_coin_save(self):
        cards = self.make_cards(ArgentSquire(), MagmaRager(), TheCoin())
        possible_plays = PossiblePlays(cards, 1)
        play = possible_plays.plays()[0]
        names = [c.name for c in play.cards]
        self.assertEqual(names, ["Argent Squire"])
