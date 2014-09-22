import unittest
from hearthbreaker.cards import Wisp, WarGolem, BloodfenRaptor, RiverCrocolisk, AbusiveSergeant, ArgentSquire
from tests.agents.trade.test_helpers import TestHelpers
from tests.agents.trade.test_case_mixin import TestCaseMixin
from hearthbreaker.agents.trade.possible_play import PossiblePlays


class TestTradeAgent(TestCaseMixin, unittest.TestCase):
    def test_setup_smoke(self):
        game = TestHelpers().make_game()

        self.add_minions(game, 0, Wisp(), WarGolem())
        self.add_minions(game, 1, BloodfenRaptor())

        self.assertEqual(2, len(game.players[0].minions))
        self.assertEqual(1, len(game.players[1].minions))

    def test_basic_trade(self):
        game = TestHelpers().make_game()

        self.add_minions(game, 1, Wisp(), WarGolem())
        self.add_minions(game, 0, BloodfenRaptor())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1], "War Golem")
        self.assert_minions(game.players[0], "Bloodfen Raptor")

    def test_buff_target(self):
        game = TestHelpers().make_game()

        self.add_minions(game, 0, BloodfenRaptor(), RiverCrocolisk())
        self.make_all_active(game)
        self.add_minions(game, 0, AbusiveSergeant())

        game.play_single_turn()

    def test_hero_power(self):
        cards = [ArgentSquire()]
        possible_plays = PossiblePlays(cards, 10, allow_hero_power=True)

        self.assertEqual(1, len(possible_plays.plays()))
