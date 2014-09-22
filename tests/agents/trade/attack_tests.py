import unittest
from hearthbreaker.cards import Wisp, WarGolem, BloodfenRaptor, GoldshireFootman, RiverCrocolisk, MagmaRager, \
    ChillwindYeti, VoidWalker, AmaniBerserker
from hearthbreaker.game_objects import Hero, MinionCard
from tests.agents.trade.test_helpers import TestHelpers, TempCard
from tests.agents.trade.test_case_mixin import TestCaseMixin


class TestTradeAgentAttackBasicTests(TestCaseMixin, unittest.TestCase):
    def test_will_attack_face(self):
        game = TestHelpers().make_game()

        self.add_minions(game, 0, BloodfenRaptor())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1])
        self.assert_minions(game.players[0], "Bloodfen Raptor")

        self.assertEqual(27, game.players[1].hero.health)

    def test_will_attack_minion_and_face(self):
        game = TestHelpers().make_game()

        self.add_minions(game, 1, Wisp())
        self.add_minions(game, 0, BloodfenRaptor(), RiverCrocolisk())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1])
        self.assert_minions(game.players[0], "Bloodfen Raptor", "River Crocolisk")

        self.assertEqual(27, game.players[1].hero.health)

    def test_will_respect_taunt(self):
        game = TestHelpers().make_game()

        self.add_minions(game, 1, Wisp(), GoldshireFootman())
        self.add_minions(game, 0, BloodfenRaptor())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1], "Wisp")
        self.assert_minions(game.players[0], "Bloodfen Raptor")

    def test_will_attack_twice(self):
        game = TestHelpers().make_game()

        self.add_minions(game, 1, Wisp(), GoldshireFootman())
        self.add_minions(game, 0, BloodfenRaptor(), RiverCrocolisk())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[1])
        self.assert_minions(game.players[0], "Bloodfen Raptor", "River Crocolisk")

    def test_trades_obj_smoke(self):
        me = [BloodfenRaptor(), RiverCrocolisk()]
        opp = [Wisp(), WarGolem()]

        trades = self.make_trades(me, opp)

        self.assertEqual(len(trades.trades()), 6)


class TestTradeAgentAttackTradesTests(TestCaseMixin, unittest.TestCase):
    def test_trades_smart(self):
        me = self.make_cards(MagmaRager())
        opp = self.make_cards(Wisp(), ChillwindYeti())

        trades = self.make_trades(me, opp)

        self.assertEqual(len(trades.trades()), 3)
        self.assertEqual(trades.trades()[0].opp_minion.name, "Chillwind Yeti")

    def test_trades_smart2(self):
        me = self.make_cards(VoidWalker())
        opp = self.make_cards(Wisp(), ChillwindYeti())

        trades = self.make_trades(me, opp)

        self.assertEqual(len(trades.trades()), 3)
        self.assertEqual(trades.trades()[0].opp_minion.name, "Wisp")

    def test_trades_smart3(self):
        me = [VoidWalker()]
        opp = [ChillwindYeti()]

        trades = self.make_trades(me, opp)

        self.assertEqual(len(trades.trades()), 2)
        self.assertEqual(trades.trades()[0].opp_minion.__class__, Hero)


class TestTempCard(unittest.TestCase):
    def test_make(self):
        m = TempCard.make("1/2")
        self.assertEqual(m.create_minion(None).health, 2)

    def test_taunt(self):
        mm = TempCard.make("1/2t")
        m = mm.create_minion(None)
        self.assertEqual(m.health, 2)
        self.assertEqual(m.taunt, True)


class TestTradeAgentAttackLethalTests(TestCaseMixin, unittest.TestCase):
    def make_minions(self, *strs):
        res = []
        for s in strs:
            if isinstance(s, MinionCard):
                res.append(s)
            else:
                m = TempCard.make(s)
                res.append(m)
        return res

    def test_lethal(self):
        me = [ChillwindYeti()]
        opp = [AmaniBerserker()]

        a = self.make_trades2(me, opp)
        trades = a[1]
        game = a[0]
        game.players[1].hero.health = 1

        self.assertEqual(len(trades.trades()), 1)
        self.assertEqual(trades.trades()[0].opp_minion.__class__, Hero)

    def test_lethal_with_two(self):
        me = [ChillwindYeti(), WarGolem()]
        opp = [AmaniBerserker()]

        a = self.make_trades2(me, opp)
        trades = a[1]
        game = a[0]
        game.players[1].hero.health = 10

        self.assertEqual(len(trades.trades()), 2)
        self.assertEqual(trades.trades()[0].opp_minion.__class__, Hero)

    def test_lethal_with_taunt(self):
        me = self.make_minions("2/9", "3/1")
        opp = self.make_minions("9/2t")

        def cb(g):
            g.players[1].hero.health = 3

        game, trades = self.make_trades2(me, opp, cb)
        trade = trades.trades()[0]

        self.assertEqual(len(trades.trades()), 2)
        self.assertEqual(trade.my_minion.health, 9)

    def test_lethal_with_taunt2(self):
        me = self.make_minions("2/9", "3/1", "2/8")
        opp = self.make_minions("9/4t")

        def cb(g):
            g.players[1].hero.health = 3

        game, trades = self.make_trades2(me, opp, cb)
        trade = trades.trades()[0]

        self.assertEqual(len(trades.trades()), 3)
        self.assertEqual(trade.my_minion.health, 8)

    def test_good_trade_with_taunt2(self):
        me = self.make_minions("2/6", "1/6", "9/1")
        opp = self.make_minions("8/2t", "9/9")

        game, trades = self.make_trades2(me, opp)
        trade = trades.trades()[0]

        self.assertEqual(len(trades.trades()), 3)
        self.assertEqual(trade.my_minion.health, 6)
        self.assertEqual(trade.opp_minion.health, 2)

    def test_lots(self):
        me = self.make_minions("1/1", "2/1", "3/2", "2/6", "4/4", "5/5")
        opp = self.make_minions("1/1t", "2/1", "3/2t", "2/6", "4/4", "5/5t", "2/5t", "8/3t")

        game, trades = self.make_trades2(me, opp)
        trade = trades.trades()[0]
        self.assertEqual(not trade, False)
