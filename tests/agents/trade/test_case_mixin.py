import random
from tests.agents.trade.test_helpers import TestHelpers
from hearthbreaker.agents.trade.trade import Trades


class TestCaseMixin:
    def setUp(self):
        TestHelpers.fix_create_minion()
        random.seed(1857)

    def add_minions(self, game, player_index, *minions):
        player = game.players[player_index]
        for minion in minions:
            minion.use(player, game)

    def make_all_active(self, game):
        for player in game.players:
            for minion in player.minions:
                minion.active = True
                minion.exhausted = False

    def assert_minions(self, player, *names):
        actual = self.card_names(player.minions)
        self.assertEqual(sorted(actual), sorted(names))

    def card_names(self, cards):
        return [m.try_name() for m in cards]

    def player_str(self, player):
        res = []
        res.append("\nPlayer\n")
        res.append("Hand: ")
        res.append(self.card_names(player.hand))
        res.append("\nDeck: ")
        res.append(self.card_names(player.deck.cards[0:5]))
        res.append("\n")

        res = [str(x) for x in res]

        return str.join("", res)

    def make_trades2(self, me, opp, game_callback=None):
        me = [m for m in map(lambda c: c.create_minion(None), me)]
        opp = [m for m in map(lambda c: c.create_minion(None), opp)]

        game = self.make_game()
        if game_callback:
            game_callback(game)

        trades = Trades(game.players[0], me, opp, game.players[1].hero)

        return [game, trades]

    def make_trades(self, me, opp):
        return self.make_trades2(me, opp)[1]

    def make_cards(self, *cards):
        return [c for c in cards]

    def make_game(self):
        return TestHelpers().make_game()

    def set_hand(self, game, player_index, *cards):
        cards = self.make_cards(*cards)
        game.players[player_index].hand = cards
