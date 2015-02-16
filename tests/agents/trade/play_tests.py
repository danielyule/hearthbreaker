import unittest
from hearthbreaker.cards import ArgentSquire, DireWolfAlpha, HarvestGolem, BloodfenRaptor, MagmaRager, Wisp, Ysera
from hearthbreaker.cards.spells.neutral import TheCoin
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

        game.players[0].hand = self.make_cards(game.current_player, ArgentSquire(), ArgentSquire(), DireWolfAlpha())
        game.players[0].mana = 1
        game.players[0].max_mana = 1

        game.play_single_turn()

        self.assert_minions(game.players[0], "Dire Wolf Alpha")

    def test_will_play_multiple(self):
        game = TestHelpers().make_game()

        game.players[0].hand = self.make_cards(game.current_player, ArgentSquire(), ArgentSquire(), ArgentSquire())
        game.players[0].mana = 1
        game.players[0].max_mana = 1

        game.play_single_turn()

        self.assert_minions(game.players[0], "Argent Squire", "Argent Squire")

    def test_will_play_multiple_correct_order(self):
        game = TestHelpers().make_game()

        game.players[0].hand = self.make_cards(game.current_player, ArgentSquire(), ArgentSquire(), ArgentSquire(),
                                               HarvestGolem())
        game.players[0].mana = 3
        game.players[0].max_mana = 3

        game.play_single_turn()

        self.assert_minions(game.players[0], "Harvest Golem", "Argent Squire")

    def test_will_use_entire_pool(self):
        game = TestHelpers().make_game()

        game.players[0].hand = self.make_cards(game.current_player, DireWolfAlpha(), DireWolfAlpha(), DireWolfAlpha(),
                                               HarvestGolem())
        game.players[0].mana = 3
        game.players[0].max_mana = 3

        game.play_single_turn()

        self.assert_minions(game.players[0], "Dire Wolf Alpha", "Dire Wolf Alpha")

    def test_will_play_three_cards(self):
        game = TestHelpers().make_game()

        self.set_hand(game, 0, Wisp(), ArgentSquire(), DireWolfAlpha())
        self.set_mana(game, 0, 3)

        game.play_single_turn()

        self.assert_minions(game.players[0], "Wisp", "Argent Squire", "Dire Wolf Alpha")


class TestTradeAgentPlayCoinTests(TestCaseMixin, unittest.TestCase):
    def test_coin(self):
        game = self.make_game()
        cards = self.make_cards(game.current_player, ArgentSquire(), BloodfenRaptor(), TheCoin())
        possible_plays = PossiblePlays(cards, 1)
        play = possible_plays.plays()[0]
        names = [c.name for c in play.cards]
        self.assertEqual(names, ["The Coin", "Bloodfen Raptor"])

    def test_coin_save(self):
        game = self.make_game()
        cards = self.make_cards(game.current_player, ArgentSquire(), MagmaRager(), TheCoin())
        possible_plays = PossiblePlays(cards, 1)
        play = possible_plays.plays()[0]
        names = [c.name for c in play.cards]
        self.assertEqual(names, ["Argent Squire"])


class TestTradeAgentHeroPowerTests(TestCaseMixin, unittest.TestCase):
    def test_will_use_hero_power_with_empty_hand(self):
        game = TestHelpers().make_game()

        self.set_hand(game, 0)
        self.set_mana(game, 0, 10)

        possible = PossiblePlays([], 10)
        play = possible.plays()[0]
        self.assertEqual(play.cards[0].name, "Hero Power")

        game.play_single_turn()
        self.assert_minions(game.players[0], "War Golem")

    def test_wont_kill_self_with_hero_power(self):
        game = TestHelpers().make_game()

        self.set_hand(game, 0)
        self.set_mana(game, 0, 2)
        game.players[0].hero.health = 1

        game.play_single_turn()
        self.assert_minions(game.players[0])
        self.assertEqual(game.players[0].hero.health, 1)

    def test_will_hero_power_first_if_inevitable(self):
        game = self.make_game()
        cards = self.make_cards(game.current_player, DireWolfAlpha())
        possible = PossiblePlays(cards, 10)
        play = possible.plays()[0]
        self.assertEqual(play.first_card().name, "Hero Power")

    def test_will_not_hero_power_if_not_inevitable(self):
        game = self.make_game()
        cards = self.make_cards(game.current_player, Ysera())
        possible = PossiblePlays(cards, 10)
        play = possible.plays()[0]
        self.assertEqual(play.first_card().name, "Ysera")
