import unittest
from hearthbreaker.cards import Wisp, WarGolem, BloodfenRaptor, GoldshireFootman, RiverCrocolisk, MagmaRager, \
    ChillwindYeti, Voidwalker, AmaniBerserker, AbusiveSergeant, DarkIronDwarf, ShatteredSunCleric, ImpMaster, \
    ElvenArcher, Shieldbearer, StormpikeCommando
from hearthbreaker.cards.base import MinionCard
from hearthbreaker.game_objects import Hero
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
        game = self.make_game()
        me = self.make_cards(game.current_player, MagmaRager())
        opp = self.make_cards(game.other_player, Wisp(), ChillwindYeti())

        trades = self.make_trades(me, opp)

        self.assertEqual(len(trades.trades()), 3)
        self.assertEqual(trades.trades()[0].opp_minion.name, "Chillwind Yeti")

    def test_trades_smart2(self):
        game = self.make_game()
        me = self.make_cards(game.current_player, Voidwalker())
        opp = self.make_cards(game.other_player, Wisp(), ChillwindYeti())

        trades = self.make_trades(me, opp)

        self.assertEqual(len(trades.trades()), 3)
        self.assertEqual(trades.trades()[0].opp_minion.name, "Wisp")

    def test_trades_smart3(self):
        me = [Voidwalker()]
        opp = [ChillwindYeti()]

        trades = self.make_trades(me, opp)

        self.assertEqual(len(trades.trades()), 2)
        self.assertEqual(trades.trades()[0].opp_minion.__class__, Hero)


class TestProperBuffs(TestCaseMixin, unittest.TestCase):
    def test_smoke(self):
        self.assertEqual(2, 2)

    def test_abusive(self):
        game = TestHelpers().make_game()

        self.set_hand(game, 0, AbusiveSergeant())
        self.set_board(game, 0, Wisp())
        self.set_board(game, 1, RiverCrocolisk())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[0], "Abusive Sergeant")
        self.assert_minions(game.players[1])

    def test_dwarf(self):
        game = TestHelpers().make_game()

        self.set_hand(game, 0, DarkIronDwarf())
        self.set_board(game, 0, Wisp())
        self.set_board(game, 1, RiverCrocolisk())

        game.players[0].mana = 4
        game.players[0].max_mana = 4

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[0], "Dark Iron Dwarf")
        self.assert_minions(game.players[1])

    def test_cleric(self):
        game = TestHelpers().make_game()

        self.set_hand(game, 0, ShatteredSunCleric())
        self.set_board(game, 0, Wisp())
        self.set_board(game, 1, BloodfenRaptor())
        self.set_mana(game, 0, 3)

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[0], "Shattered Sun Cleric")
        self.assert_minions(game.players[1])

    def test_cleric_buff_to_keep_alive(self):
        # This test does not pass yet. Agent picks a random friendly minion
        return

        game = TestHelpers().make_game()

        self.set_hand(game, 0, ShatteredSunCleric())
        self.set_board(game, 0, MagmaRager(), Wisp())
        self.set_board(game, 1, ImpMaster())
        self.set_mana(game, 0, 3)

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[0], "Shattered Sun Cleric", "Magma Rager", "Wisp")
        self.assert_minions(game.players[1])

    def test_archer_attacks_enemy(self):
        game = TestHelpers().make_game()

        self.set_hand(game, 0, ElvenArcher())
        self.set_board(game, 0, Shieldbearer())
        self.set_board(game, 1, BloodfenRaptor())

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[0], "Shieldbearer", "Elven Archer")
        self.assertEqual(game.players[1].minions[0].health, 1)

    def test_commando_attacks_enemy(self):
        game = TestHelpers().make_game()

        self.set_hand(game, 0, StormpikeCommando())
        self.set_board(game, 0, Wisp())
        self.set_board(game, 1, BloodfenRaptor())
        self.set_mana(game, 0, 5)

        self.make_all_active(game)
        game.play_single_turn()

        self.assert_minions(game.players[0], "Wisp", "Stormpike Commando")
        self.assert_minions(game.players[1])


# class TestTempCard(unittest.TestCase):
#     def test_make(self):
#         m = TempCard.make("1/2")
#         self.assertEqual(m.create_minion(None).health, 2)
#
#     def test_taunt(self):
#         mm = TempCard.make("1/2t")
#         m = mm.create_minion(None)
#         self.assertEqual(m.health, 2)
#         m.add_to_board(0)
#         self.assertEqual(m.taunt, True)


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
        opp = self.make_minions("1/1t", "2/1", "3/2t", "2/6", "4/4", "5/5t", "2/5t")

        game, trades = self.make_trades2(me, opp)
        trade = trades.trades()[0]
        self.assertEqual(not trade, False)
